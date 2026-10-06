import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch

from app.main import app
from app.api.deps import get_db_session
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.agent import AgentChatJobResponse, AgentJobStatusResponse, AgentChatResponse

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
    with patch("app.api.v1.endpoints.agent.AgentService._execute_chat") as mock_execute:
        mock_execute.return_value = AgentChatResponse(
            status="completed",
            thread_id="thread-123",
            final_response="Here is your completed campaign."
        )
        
        payload = {
            "thread_id": "thread-123",
            "message": "Create a campaign"
        }
        
        response = await async_client.post("/api/v1/agent/chat", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
        assert response.json()["final_response"] == "Here is your completed campaign."

@pytest.mark.asyncio
async def test_agent_chat_approval_pending(async_client: AsyncClient):
    with patch("app.api.v1.endpoints.agent.AgentService._execute_chat") as mock_execute:
        mock_execute.return_value = AgentChatResponse(
            status="approval_pending",
            thread_id="thread-456",
            approval_required=True,
            approval_request_id=999
        )
        
        payload = {
            "thread_id": "thread-456",
            "message": "Create a social media post"
        }
        
        response = await async_client.post("/api/v1/agent/chat", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "approval_pending"
        assert response.json()["approval_request_id"] == 999
