import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.api.deps import get_db_session, get_current_user
from app.models.approval import ApprovalRequest
from app.models.user import User
from app.agents.enums import ApprovalStatus


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    user = User(id=1, email="testuser@example.com", username="testuser", hashed_password="pw")
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


@pytest_asyncio.fixture
async def mock_approval(db_session, test_user):
    """Creates a mock pending approval request."""
    request = ApprovalRequest(
        user_id=test_user.id,
        thread_id="test_thread_123",
        action_type="publish_social",
        platform="linkedin",
        content={"generated_content": {"body": "Hello world"}},
        status=ApprovalStatus.PENDING
    )
    db_session.add(request)
    await db_session.commit()
    await db_session.refresh(request)
    return request


@pytest.mark.asyncio
async def test_get_pending_approvals(async_client: AsyncClient, mock_approval):
    response = await async_client.get("/api/v1/approvals/pending")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(item["id"] == mock_approval.id for item in data["items"])


@pytest.mark.asyncio
async def test_approve_request(async_client: AsyncClient, mock_approval):
    from unittest.mock import patch
    # Mock resume workflow to avoid actual graph execution in unit test
    with patch("app.services.approval_service.ApprovalService._resume_workflow", return_value=None):
        payload = {"reason": "Looks good"}
        response = await async_client.post(
            f"/api/v1/approvals/{mock_approval.id}/approve",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == ApprovalStatus.APPROVED.value
        assert data["reason"] == "Looks good"


@pytest.mark.asyncio
async def test_reject_request(async_client: AsyncClient, mock_approval):
    from unittest.mock import patch
    # Mock resume workflow
    with patch("app.services.approval_service.ApprovalService._resume_workflow", return_value=None):
        payload = {"reason": "Needs better tone"}
        response = await async_client.post(
            f"/api/v1/approvals/{mock_approval.id}/reject",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == ApprovalStatus.REJECTED.value
        assert data["rejection_reason"] == "Needs better tone"


@pytest.mark.asyncio
async def test_unauthorized_approval_access(async_client: AsyncClient, mock_approval):
    from fastapi import HTTPException
    
    async def _unauthorized_user():
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    app.dependency_overrides[get_current_user] = _unauthorized_user
    
    response = await async_client.get(f"/api/v1/approvals/{mock_approval.id}")
    assert response.status_code == 401
