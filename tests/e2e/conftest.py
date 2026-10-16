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

import uuid
from sqlalchemy.pool import NullPool
from sqlalchemy import event

@pytest_asyncio.fixture
async def e2e_test_engine(test_db_dir):
    db_path = test_db_dir / f"test_e2e_{uuid.uuid4().hex}.sqlite"
    test_db_url = f"sqlite+aiosqlite:///{db_path.as_posix()}"

    engine = create_async_engine(
        test_db_url,
        poolclass=NullPool,
        echo=False,
    )

    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=10000")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    except Exception:
        pass

    await engine.dispose()

    # Clean up test database files safely
    for ext in ["", "-wal", "-shm"]:
        p = f"{db_path.as_posix()}{ext}"
        if os.path.exists(p):
            try:
                os.remove(p)
            except OSError:
                pass

@pytest_asyncio.fixture
async def e2e_db_session(e2e_test_engine):
    async_session = sessionmaker(
        e2e_test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session

@pytest_asyncio.fixture(autouse=True)
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
    from app.agents.schemas import ToolResult
    from app.agents.enums import ToolExecutionStatus

    default_result = {
        "tool_results": [
            ToolResult(
                tool_name="social_media",
                status=ToolExecutionStatus.SUCCESS,
                data={"output": "Post ID: e2e_mock_123"},
            )
        ]
    }
    mock_tools = AsyncMock(return_value=default_result)

    with patch("app.scheduler.processor.execute_tools", new=mock_tools), \
         patch("app.agents.nodes.tools.execute_tools", new=mock_tools), \
         patch("app.agents.graph.execute_tools", new=mock_tools):
        yield mock_tools

@pytest_asyncio.fixture(autouse=True)
def mock_worker_session(e2e_test_engine):
    """
    Bind AsyncSessionLocal to the isolated e2e_test_engine across all e2e tests.
    """
    e2e_sessionmaker = sessionmaker(
        e2e_test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    with patch("app.database.connection.AsyncSessionLocal", new=e2e_sessionmaker):
        yield e2e_sessionmaker
