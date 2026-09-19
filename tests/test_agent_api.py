import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, MagicMock, AsyncMock

from app.main import app
from app.api.deps import get_db_session, get_current_user
from app.models.user import User
from app.agents.enums import AgentStatus

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    user = User(id=1, email="agentuser@example.com", username="agentuser", hashed_password="pw")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession, test_user: User):
    async def _get_test_db():
        yield db_session
        
    async def _get_current_user():
        return test_user

    app.dependency_overrides[get_db_session] = _get_test_db
    app.dependency_overrides[get_current_user] = _get_current_user
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_agent_chat_success(async_client: AsyncClient):
    with patch("app.services.agent_service.build_marketing_graph") as mock_build_graph, \
         patch("app.services.agent_service.get_checkpointer") as mock_get_checkpointer:
        
        # Mock checkpointer context manager
        mock_checkpointer = MagicMock()
        mock_get_checkpointer.return_value.__aenter__.return_value = mock_checkpointer
        
        # Mock graph
        mock_graph = MagicMock()
        mock_build_graph.return_value = mock_graph
        
        # Mock graph.aget_state
        mock_state = MagicMock()
        mock_state.values = {"status": AgentStatus.COMPLETED}
        mock_graph.aget_state = AsyncMock(return_value=mock_state)
        
        # Mock graph.ainvoke
        mock_graph.ainvoke = AsyncMock(return_value={
            "status": AgentStatus.COMPLETED,
            "final_response": "Here is your completed campaign."
        })
        
        payload = {
            "thread_id": "thread-success-123",
            "message": "Create a campaign"
        }
        
        response = await async_client.post("/api/v1/agent/chat", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["thread_id"] == "thread-success-123"
        assert data["final_response"] == "Here is your completed campaign."
        assert data["approval_required"] is False

@pytest.mark.asyncio
async def test_agent_chat_approval_pending(async_client: AsyncClient):
    with patch("app.services.agent_service.build_marketing_graph") as mock_build_graph, \
         patch("app.services.agent_service.get_checkpointer") as mock_get_checkpointer:
        
        # Mock checkpointer context manager
        mock_checkpointer = MagicMock()
        mock_get_checkpointer.return_value.__aenter__.return_value = mock_checkpointer
        
        # Mock graph
        mock_graph = MagicMock()
        mock_build_graph.return_value = mock_graph
        
        # Mock graph.aget_state
        mock_state = MagicMock()
        mock_state.values = {} # First run
        mock_graph.aget_state = AsyncMock(return_value=mock_state)
        
        # Mock graph.ainvoke
        mock_graph.ainvoke = AsyncMock(return_value={
            "status": AgentStatus.WAITING_FOR_APPROVAL,
            "approval_request_id": 999
        })
        
        payload = {
            "thread_id": "thread-approval-123",
            "message": "Create a social media post"
        }
        
        response = await async_client.post("/api/v1/agent/chat", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approval_pending"
        assert data["thread_id"] == "thread-approval-123"
        assert data["approval_required"] is True
        assert data["approval_request_id"] == 999

@pytest.mark.asyncio
async def test_agent_chat_already_approval_pending(async_client: AsyncClient):
    with patch("app.services.agent_service.build_marketing_graph") as mock_build_graph, \
         patch("app.services.agent_service.get_checkpointer") as mock_get_checkpointer:
        
        # Mock checkpointer context manager
        mock_checkpointer = MagicMock()
        mock_get_checkpointer.return_value.__aenter__.return_value = mock_checkpointer
        
        # Mock graph
        mock_graph = MagicMock()
        mock_build_graph.return_value = mock_graph
        
        # Mock graph.aget_state to simulate it's ALREADY paused
        mock_state = MagicMock()
        mock_state.values = {
            "status": AgentStatus.WAITING_FOR_APPROVAL,
            "approval_request_id": 888
        }
        mock_graph.aget_state = AsyncMock(return_value=mock_state)
        
        payload = {
            "thread_id": "thread-paused-123",
            "message": "Continue please"
        }
        
        response = await async_client.post("/api/v1/agent/chat", json=payload)
        
        # We shouldn't even call ainvoke
        mock_graph.ainvoke.assert_not_called()
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approval_pending"
        assert data["approval_required"] is True
        assert data["approval_request_id"] == 888
        assert data["final_response"] is None
