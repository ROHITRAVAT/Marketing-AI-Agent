import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.core.security import hash_password
from app.models.user import User


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    from sqlalchemy import event
    
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    from app.models.user import User
    from app.models.campaign import Campaign
    from app.models.integration import IntegrationConnection
    from app.models.scheduled_post import ScheduledPost
    from app.models.social_analytics import SocialAnalytics
    from app.models.error_log import AgentErrorLog
    from app.models.approval import ApprovalRequest

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine):
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def seeded_db_session(db_session: AsyncSession):
    active_user = User(
        id=1,
        email="auth-test@example.com",
        username="auth_test",
        hashed_password=hash_password("StrongPass123"),
        full_name="Auth Test User",
        role="user",
        is_active=True,
        is_superuser=False,
    )

    inactive_user = User(
        id=9,
        email="inactive-test@example.com",
        username="inactive_test",
        hashed_password=hash_password("StrongPass123"),
        full_name="Inactive Test User",
        role="user",
        is_active=False,
        is_superuser=False,
    )

    from app.models.integration import IntegrationConnection
    linkedin_conn = IntegrationConnection(
        user_id=1,
        provider="linkedin",
        access_token="mock_valid_token",
        provider_user_id="mock_urn"
    )
    
    facebook_conn = IntegrationConnection(
        user_id=1,
        provider="facebook",
        access_token="mock_valid_fb_token",
        provider_user_id="mock_fb_urn"
    )

    facebook_page_conn = IntegrationConnection(
        user_id=1,
        provider="facebook_page",
        access_token="mock_page_token",
        provider_user_id="mock_page_id",
        scopes="selected"
    )

    await db_session.merge(active_user)
    await db_session.merge(inactive_user)
    await db_session.merge(linkedin_conn)
    await db_session.merge(facebook_conn)
    await db_session.merge(facebook_page_conn)
    await db_session.commit()

    yield db_session



@pytest.fixture(autouse=True)
def mock_worker_session(test_engine):
    from unittest.mock import patch
    
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    from langgraph.checkpoint.memory import MemorySaver
    from contextlib import asynccontextmanager
    
    # Create a single memory saver for the entire test
    test_checkpointer = MemorySaver()
    
    @asynccontextmanager
    async def mock_get_checkpointer():
        yield test_checkpointer
    
    with patch("app.database.connection.AsyncSessionLocal", new=async_session), \
         patch("app.agents.checkpoint.get_checkpointer", new=mock_get_checkpointer), \
         patch("app.services.agent_service.get_checkpointer", new=mock_get_checkpointer), \
         patch("app.services.approval_service.get_checkpointer", new=mock_get_checkpointer):
        yield



@pytest.fixture(autouse=True)
def mock_rag_services():
    from unittest.mock import patch, AsyncMock, MagicMock
    
    mock_ollama = MagicMock()
    mock_ollama.embed = AsyncMock(return_value=[0.1] * 768)
    
    from qdrant_client.models import ScoredPoint
    mock_qdrant = MagicMock()
    mock_qdrant.search = AsyncMock(return_value=[
        ScoredPoint(id=1, version=1, score=0.9, payload={"content": "Mocked retrieved document"})
    ])
    
    with patch("app.agents.nodes.retrieval.get_ollama_service", return_value=mock_ollama), \
         patch("app.agents.nodes.retrieval.get_qdrant_service", return_value=mock_qdrant):
        yield

@pytest_asyncio.fixture
async def integration_client(test_engine, seeded_db_session):
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    from app.api.deps import get_db_session, get_current_user as deps_get_current_user
    from app.dependencies.auth import get_current_user as auth_get_current_user
    from app.models.user import User
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def _get_test_db():
        async with async_session() as session:
            yield session

    async def _get_test_user():
        async with async_session() as session:
            return await session.get(User, 1)

    app.dependency_overrides[get_db_session] = _get_test_db
    app.dependency_overrides[deps_get_current_user] = _get_test_user
    app.dependency_overrides[auth_get_current_user] = _get_test_user

    async with AsyncClient(
        transport=ASGITransport(app=app, client=("127.0.0.1", 12345), raise_app_exceptions=False), base_url="http://testserver"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_social_platforms():
    from unittest.mock import patch, AsyncMock, MagicMock
    import httpx
    
    original_get = httpx.AsyncClient.get
    original_post = httpx.AsyncClient.post
    
    mock_get = AsyncMock()
    mock_post = AsyncMock()
    
    async def mock_get_side_effect(self, *args, **kwargs):
        if "testserver" in str(self.base_url):
            return await original_get(self, *args, **kwargs)
            
        url = args[0] if args else kwargs.get("url", "")
        url_str = str(url)
            
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        
        if "linkedin" in url_str:
            mock_resp.json = MagicMock(return_value={
                "elements": [
                    {"totalShareStatistics": {"impressionCount": 2000, "engagement": 150, "clickCount": 15, "likeCount": 10, "commentCount": 5, "shareCount": 2}}
                ]
            })
        elif "facebook" in url_str or "instagram" in url_str:
            mock_resp.json = MagicMock(return_value={
                "data": [
                    {"name": "post_impressions_unique", "values": [{"value": 2000}]},
                    {"name": "post_engaged_users", "values": [{"value": 150}]},
                    {"name": "impressions", "values": [{"value": 2000}]},
                    {"name": "reach", "values": [{"value": 2000}]},
                    {"name": "engagement", "values": [{"value": 150}]},
                    {"insights": {"data": [
                        {"name": "impressions", "values": [{"value": 2000}]},
                        {"name": "reach", "values": [{"value": 2000}]},
                        {"name": "engagement", "values": [{"value": 150}]}
                    ]}}
                ],
                "likes": {"summary": {"total_count": 10}},
                "comments": {"summary": {"total_count": 5}},
                "shares": {"count": 2},
                "like_count": 10,
                "comments_count": 5
            })
        elif "twitter" in url_str or "x.com" in url_str:
            mock_resp.json = MagicMock(return_value={
                "data": {
                    "public_metrics": {
                        "impression_count": 2000,
                        "like_count": 10,
                        "reply_count": 5,
                        "retweet_count": 2
                    }
                }
            })
        else:
            mock_resp.json = MagicMock(return_value={
                "likes": 10, "comments": 5, "shares": 2, "impressions": 2000, "clicks": 15, "engagement": 150
            })
            
        await mock_get(self, *args, **kwargs)  # Record the call for assertions
        return mock_resp

    async def mock_post_side_effect(self, *args, **kwargs):
        if "testserver" in str(self.base_url):
            return await original_post(self, *args, **kwargs)
            
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json = MagicMock(return_value={"id": "mock_external_id_123"})
        
        await mock_post(self, *args, **kwargs)  # Record the call for assertions
        return mock_resp
            
    with patch("httpx.AsyncClient.post", new=mock_post_side_effect), \
         patch("httpx.AsyncClient.get", new=mock_get_side_effect):
        yield {"get": mock_get, "post": mock_post}
