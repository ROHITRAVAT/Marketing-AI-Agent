import pytest
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from unittest.mock import patch, AsyncMock

from app.models.scheduled_post import ScheduledPost
from app.models.user import User
from app.scheduler.worker import poll_and_process_jobs

pytestmark = pytest.mark.asyncio

@pytest.fixture(autouse=True)
async def setup_scheduler_test(seeded_db_session: AsyncSession):
    """Clear default seeded connections to prevent test pollution."""
    from sqlalchemy import delete
    from app.models.integration import IntegrationConnection
    await seeded_db_session.execute(delete(IntegrationConnection))
    await seeded_db_session.commit()

async def test_scheduler_future_post_not_published(seeded_db_session: AsyncSession, mock_social_platforms):
    # Create a post scheduled in the future
    future_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    
    post = ScheduledPost(
        user_id=1,
        platform="twitter",
        content="Future post",
        scheduled_time=future_time,
        status="scheduled"
    )
    seeded_db_session.add(post)
    await seeded_db_session.commit()
    await seeded_db_session.refresh(post)
    
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_get_token:
        mock_get_token.return_value = "mock_valid_token"
        
        await poll_and_process_jobs()
        
    await seeded_db_session.refresh(post)
    assert post.status == "scheduled"
    assert post.external_post_id is None
    
    # Verify mock_social_platforms was NOT called for this post
    mock_social_platforms["post"].assert_not_called()

async def test_scheduler_past_post_published(seeded_db_session: AsyncSession, mock_social_platforms):
    # Create a post scheduled in the past
    past_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10)
    
    from app.models.integration import IntegrationConnection
    # Add an integration connection so publishing doesn't fail
    conn = IntegrationConnection(
        user_id=1,
        provider="linkedin",
        access_token="mock_token",
        provider_user_id="mock_user_id"
    )
    seeded_db_session.add(conn)
    
    post = ScheduledPost(
        user_id=1,
        platform="linkedin",
        content="Past post",
        scheduled_time=past_time,
        status="scheduled"
    )
    seeded_db_session.add(post)
    await seeded_db_session.commit()
    await seeded_db_session.refresh(post)
    
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_get_token:
        mock_get_token.return_value = "mock_valid_token"
        
        await poll_and_process_jobs()
        
    await seeded_db_session.refresh(post)
    assert post.status == "published"
    assert post.external_post_id == "mock_external_id_123"
    
async def test_scheduler_cancellation(seeded_db_session: AsyncSession, mock_social_platforms):
    past_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10)
    
    post = ScheduledPost(
        user_id=1,
        platform="facebook",
        content="Cancelled post",
        scheduled_time=past_time,
        status="cancelled" # It was cancelled before the scheduler got to it
    )
    seeded_db_session.add(post)
    await seeded_db_session.commit()
    await seeded_db_session.refresh(post)
    
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_get_token:
        mock_get_token.return_value = "mock_valid_token"
        
        await poll_and_process_jobs()
        
    await seeded_db_session.refresh(post)
    # Status should remain cancelled, NOT published
    assert post.status == "cancelled"
    assert post.external_post_id is None

async def test_scheduler_token_refresh_fails(seeded_db_session: AsyncSession, mock_social_platforms):
    past_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10)
    
    post = ScheduledPost(
        user_id=1,
        platform="twitter",
        content="Token fail post",
        scheduled_time=past_time,
        status="scheduled",
        attempt_count=2 # so it fails on this try
    )
    seeded_db_session.add(post)
    await seeded_db_session.commit()
    await seeded_db_session.refresh(post)
    
    # Simulate a token refresh failure
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_get_token:
        mock_get_token.side_effect = Exception("Failed to refresh token")
        
        await poll_and_process_jobs()
        
    await seeded_db_session.refresh(post)
    # The post should be marked as failed because of the token error
    assert post.status == "failed"
    assert "Tool execution did not report success" in post.error_message
    assert post.external_post_id is None
