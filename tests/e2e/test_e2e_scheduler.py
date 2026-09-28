import asyncio
import datetime
import pytest
from unittest.mock import patch
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.main import app
from app.models.scheduled_post import ScheduledPost
from app.models.user import User

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]

@pytest.fixture
def real_worker_session(e2e_test_engine):
    """
    Override the globally mocked AsyncSessionLocal from e2e/conftest.py
    with a real sessionmaker bound to the e2e test engine.
    This allows the background scheduler to actually read/write from the test DB.
    """
    async_session = sessionmaker(
        e2e_test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    with patch("app.database.connection.AsyncSessionLocal", new=async_session):
        yield async_session

async def test_scheduler_lifecycle_e2e(
    e2e_db_session: AsyncSession, 
    e2e_seeded_user: User, 
    real_worker_session,
    mock_social_media
):
    """
    Tests that the FastAPI application lifespan properly starts the scheduler
    background task, which polls the database and processes eligible jobs.
    """
    # 1. Create a job due in the past
    post = ScheduledPost(
        user_id=e2e_seeded_user.id,
        platform="linkedin",
        content="E2E Scheduler Test Content",
        scheduled_time=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10),
        status="scheduled",
        attempt_count=0,
    )
    e2e_db_session.add(post)
    await e2e_db_session.commit()
    await e2e_db_session.refresh(post)
    
    post_id = post.id
    
    # 2. Patch scheduler configuration so it runs fast and is enabled
    # Also patch TokenManager so token refresh doesn't fail
    with patch("app.scheduler.worker.SCHEDULER_ENABLED", True), \
         patch("app.scheduler.worker.SCHEDULER_INTERVAL_SECONDS", 0.1), \
         patch("app.core.oauth.manager.TokenManager.get_valid_access_token", return_value="mock_e2e_token"):
         
        # 3. Start the FastAPI lifespan (which launches run_scheduler)
        async with app.router.lifespan_context(app):
            # 4. Wait for the background scheduler to process the job
            deadline = asyncio.get_running_loop().time() + 2.0
            
            job_processed = False
            while asyncio.get_running_loop().time() < deadline:
                # Expire all cached objects to force a DB read
                e2e_db_session.expire_all()
                
                # Refresh job status
                result = await e2e_db_session.execute(
                    select(ScheduledPost).where(ScheduledPost.id == post_id)
                )
                refreshed_post = result.scalar_one()
                
                # In the worker, success marks status as 'published'
                # If mock_social_media worked or failed, status changes from 'scheduled' to 'published' or 'failed'
                if refreshed_post.status != "scheduled":
                    job_processed = True
                    break
                    
                await asyncio.sleep(0.1)
                
            # 5. Verify the result
            assert job_processed, "Scheduler did not process the job within the timeout."
            
            result = await e2e_db_session.execute(
                select(ScheduledPost).where(ScheduledPost.id == post_id)
            )
            final_post = result.scalar_one()
            assert final_post.status in ["published", "failed"], f"Unexpected final status: {final_post.status}"
