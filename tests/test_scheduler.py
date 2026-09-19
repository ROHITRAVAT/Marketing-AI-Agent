import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.user import User
from app.models.scheduled_post import ScheduledPost
from app.models.approval import ApprovalRequest, ApprovalStatus
from app.scheduler.worker import poll_and_process_jobs
from app.dependencies.auth import get_current_user
from app.api.deps import get_db_session
from sqlalchemy import select
import asyncio

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    user = User(id=999, email="scheduler@example.com", username="scheduler", hashed_password="pw")
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
async def approved_request(db_session: AsyncSession, test_user: User):
    req = ApprovalRequest(
        user_id=test_user.id,
        thread_id="test-thread",
        action_type="publish_social",
        platform="twitter",
        content={"body": "Test tweet"},
        status=ApprovalStatus.APPROVED
    )
    db_session.add(req)
    await db_session.commit()
    await db_session.refresh(req)
    return req

@pytest_asyncio.fixture
async def pending_request(db_session: AsyncSession, test_user: User):
    req = ApprovalRequest(
        user_id=test_user.id,
        thread_id="test-thread-2",
        action_type="publish_social",
        platform="twitter",
        content={"body": "Test tweet 2"},
        status=ApprovalStatus.PENDING
    )
    db_session.add(req)
    await db_session.commit()
    await db_session.refresh(req)
    return req

@pytest.mark.asyncio
async def test_create_scheduled_post_valid(async_client: AsyncClient, test_user: User, approved_request: ApprovalRequest):
    future_time = datetime.now(timezone.utc) + timedelta(days=1)
    
    payload = {
        "platform": "twitter",
        "account_id": "test_account",
        "content": "This is a test",
        "scheduled_time": future_time.isoformat(),
        "timezone": "UTC",
        "approval_request_id": approved_request.id
    }
    
    response = await async_client.post(
        "/api/v1/scheduled-posts/",
        json=payload,
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["platform"] == "twitter"
    assert data["status"] == "scheduled"
    assert data["user_id"] == test_user.id
    assert data["approval_request_id"] == approved_request.id

@pytest.mark.asyncio
async def test_create_scheduled_post_past_time(async_client: AsyncClient):
    past_time = datetime.now(timezone.utc) - timedelta(days=1)
    
    payload = {
        "platform": "twitter",
        "content": "This is a test",
        "scheduled_time": past_time.isoformat(),
    }
    
    response = await async_client.post(
        "/api/v1/scheduled-posts/",
        json=payload,
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_get_scheduled_posts(async_client: AsyncClient, db_session: AsyncSession, test_user: User):
    # Add a mock post
    post = ScheduledPost(
        user_id=test_user.id,
        platform="linkedin",
        content="Testing list",
        scheduled_time=datetime.now(timezone.utc) + timedelta(days=1),
        status="scheduled"
    )
    db_session.add(post)
    await db_session.commit()
    
    response = await async_client.get("/api/v1/scheduled-posts/", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["platform"] == "linkedin"

@pytest.mark.asyncio
async def test_update_scheduled_post(async_client: AsyncClient, db_session: AsyncSession, test_user: User):
    post = ScheduledPost(
        user_id=test_user.id,
        platform="facebook",
        content="Testing patch",
        scheduled_time=datetime.now(timezone.utc) + timedelta(days=1),
        status="scheduled"
    )
    db_session.add(post)
    await db_session.commit()
    
    future_time2 = datetime.now(timezone.utc) + timedelta(days=2)
    response = await async_client.patch(
        f"/api/v1/scheduled-posts/{post.id}",
        json={"scheduled_time": future_time2.isoformat()},
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
@pytest.mark.asyncio
async def test_cancel_scheduled_post(async_client: AsyncClient, db_session: AsyncSession, test_user: User):
    post = ScheduledPost(
        user_id=test_user.id,
        platform="instagram",
        content="Testing delete",
        scheduled_time=datetime.now(timezone.utc) + timedelta(days=1),
        status="scheduled"
    )
    db_session.add(post)
    await db_session.commit()
    
    response = await async_client.delete(
        f"/api/v1/scheduled-posts/{post.id}",
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 204
    
    # Check in DB
    result = await db_session.execute(select(ScheduledPost).where(ScheduledPost.id == post.id))
    db_post = result.scalar_one()
    assert db_post.status == "cancelled"

@pytest.mark.asyncio
async def test_poll_and_process_jobs_rejection(db_session: AsyncSession, test_user: User, pending_request: ApprovalRequest):
    # Setup a post that is due but its approval request is PENDING (not APPROVED)
    post = ScheduledPost(
        user_id=test_user.id,
        platform="twitter",
        content="Should fail verification",
        scheduled_time=datetime.now(timezone.utc) - timedelta(minutes=5),
        status="scheduled",
        approval_request_id=pending_request.id
    )
    db_session.add(post)
    await db_session.commit()
    
    # Mock AsyncSessionLocal so the worker uses our test session
    from unittest.mock import patch, MagicMock
    
    mock_session_context = MagicMock()
    mock_session_context.__aenter__.return_value = db_session
    mock_session_context.__aexit__.return_value = False
    
    with patch("app.database.connection.AsyncSessionLocal", return_value=mock_session_context):
        # Run the scheduler logic once
        await poll_and_process_jobs()
    
    # Refetch post to see what happened
    await db_session.refresh(post)
    
    # Should have failed because it wasn't approved
    assert post.status == "failed"
    assert "rejected or approval missing" in post.error_message
