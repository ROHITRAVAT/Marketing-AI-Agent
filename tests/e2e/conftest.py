import os
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.base import Base
from app.api.deps import get_db_session, get_current_user
from app.models.user import User
from app.core.security import hash_password
from unittest.mock import patch, AsyncMock

# E2E Test DB URL - Isolated
E2E_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def e2e_test_engine():
    engine = create_async_engine(
        E2E_DATABASE_URL,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest_asyncio.fixture
async def e2e_db_session(e2e_test_engine):
    async_session = sessionmaker(
        e2e_test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session

@pytest_asyncio.fixture
async def e2e_seeded_user(e2e_db_session: AsyncSession):
    user = User(
        id=1,
        email="e2e-test@example.com",
        username="e2e_test",
        hashed_password=hash_password("E2ePass123"),
        full_name="E2E Test User",
        role="user",
        is_active=True,
        is_superuser=False,
    )

    e2e_db_session.add(user)
    await e2e_db_session.commit()
    await e2e_db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def e2e_client(e2e_db_session: AsyncSession, e2e_seeded_user: User):
    async def _get_test_db():
        yield e2e_db_session

    async def _get_current_user():
        return e2e_seeded_user

    app.dependency_overrides[get_db_session] = _get_test_db
    app.dependency_overrides[get_current_user] = _get_current_user
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client
        
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(autouse=True)
def mock_ollama_service():
    """Mock Ollama service so E2E tests can run without requiring a local LLM server."""
    from langchain_core.outputs import ChatResult, ChatGeneration
    from langchain_core.messages import AIMessage
    
    with patch("langchain_core.language_models.chat_models.BaseChatModel.ainvoke", new_callable=AsyncMock) as mock_ainvoke, \
         patch("app.ollama.service.OllamaService.embed", new_callable=AsyncMock) as mock_embed:
        
        async def mock_ainvoke_side_effect(input, *args, **kwargs):
            prompt_text = repr(input)
            if hasattr(input, "to_string"):
                prompt_text = input.to_string()
            elif hasattr(input, "messages"):
                prompt_text = " ".join([str(m.content) for m in input.messages])
                
            prompt = prompt_text.lower()
            content = "Mocked AI Content for tests."
            if "qa reviewer" in prompt or "evaluate the generated content" in prompt:
                content = '{"approved": true, "score": 9.5, "feedback": "Great", "issues": []}'
            elif "marketing execution planner" in prompt:
                content = '[{"step_id": "1", "description": "Write social draft", "platform": "LinkedIn"}]'
            
            return AIMessage(content=content)
            
        mock_ainvoke.side_effect = mock_ainvoke_side_effect
        mock_embed.return_value = [0.1] * 384
        
        yield mock_ainvoke

@pytest_asyncio.fixture(autouse=True)
def mock_social_media():
    """Mock the social media tool executions to prevent actual posting during testing."""
    with patch("app.agents.graph.execute_tools") as mock_tools:
        mock_tools.return_value = {"tool_results": [{"tool": "social_media", "status": "success"}]}
        yield mock_tools

@pytest_asyncio.fixture(autouse=True)
def mock_approval_db():
    """Mock AsyncSessionLocal in approval node to avoid db errors in general e2e tests."""
    from unittest.mock import MagicMock, AsyncMock
    from contextlib import asynccontextmanager
    
    @asynccontextmanager
    async def mock_session():
        mock_db = MagicMock()
        
        # db.execute is awaited, so it should return a mock result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        
        async def mock_execute(*args, **kwargs):
            return mock_result
            
        mock_db.execute = mock_execute
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        # Mock the new request id
        yield mock_db
        
    with patch("app.database.connection.AsyncSessionLocal", mock_session):
        yield
