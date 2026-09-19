"""
Critical Business Rules tests.
Explicit verification of the most important rules defined in the requirements.
Covers requirement §65.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from unittest.mock import patch, AsyncMock

from app.models.scheduled_post import ScheduledPost
from app.models.approval import ApprovalRequest
from app.agents.enums import ApprovalStatus
from app.scheduler.worker import poll_and_process_jobs
from tests.fixtures.factories import create_test_scheduled_post

pytestmark = [pytest.mark.asyncio, pytest.mark.integration, pytest.mark.critical]


async def test_rule_unapproved_content_not_published(seeded_db_session: AsyncSession):
    """Rule: Unapproved content must NEVER be published to social media."""
    # Ensure agent graph explicitly raises ToolExecutionError if status != APPROVED
    from app.agents.nodes.tools import execute_tools
    from app.agents.state import MarketingAgentState
    from app.core.errors import ToolExecutionError
    from app.agents.enums import ToolExecutionStatus
    
    appr = ApprovalRequest(
        user_id=1, thread_id="t_crit_1", action_type="publish_social",
        platform="linkedin", status=ApprovalStatus.PENDING, content={}
    )
    seeded_db_session.add(appr)
    await seeded_db_session.commit()
    
    state = MarketingAgentState(
        user_id=1,
        platform="linkedin",
        approval_required=True,
        approval_request_id=appr.id,
        plan=[{"step_id": "1", "description": "social media post on linkedin"}],
        generated_content={"body": "Test"}
    )
    
    result = await execute_tools(state)
    
    assert "tool_results" in result
    failed_results = [tr for tr in result["tool_results"] if tr.status == ToolExecutionStatus.FAILED]
    assert len(failed_results) == 1
    assert "Action not approved" in failed_results[0].error
    # Verify no posts created
    count = (await seeded_db_session.execute(select(ScheduledPost))).scalars().all()
    assert len(count) == 0


async def test_rule_cancelled_post_not_published(seeded_db_session: AsyncSession):
    """Rule: A cancelled post must not be published by the scheduler."""
    post = create_test_scheduled_post(user_id=1, status="cancelled")
    seeded_db_session.add(post)
    await seeded_db_session.commit()
    
    with patch("app.services.linkedin_service.LinkedInService.publish_post") as mock_pub:
        await poll_and_process_jobs()
        
    mock_pub.assert_not_called()
    await seeded_db_session.refresh(post)
    assert post.status == "cancelled"


async def test_rule_future_post_not_published_early(seeded_db_session: AsyncSession):
    """Rule: A post scheduled for the future must not be published yet."""
    import datetime
    future = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    post = create_test_scheduled_post(user_id=1, status="scheduled", scheduled_time=future)
    seeded_db_session.add(post)
    await seeded_db_session.commit()
    
    with patch("app.services.linkedin_service.LinkedInService.publish_post") as mock_pub:
        await poll_and_process_jobs()
        
    mock_pub.assert_not_called()
    await seeded_db_session.refresh(post)
    assert post.status == "scheduled"


async def test_rule_no_duplicate_publishing(seeded_db_session: AsyncSession):
    """Rule: A post marked 'published' must never be published again."""
    post = create_test_scheduled_post(user_id=1, status="published", external_post_id="ext_123")
    seeded_db_session.add(post)
    await seeded_db_session.commit()
    
    with patch("app.services.linkedin_service.LinkedInService.publish_post") as mock_pub:
        await poll_and_process_jobs()
        
    mock_pub.assert_not_called()


async def test_rule_user_isolation(integration_client, seeded_db_session: AsyncSession):
    """Rule: Users can only see and act upon their own resources."""
    from app.models.user import User
    user2 = User(id=2, email="user2@test.com", hashed_password="pw", is_active=True, full_name="User 2")
    seeded_db_session.add(user2)
    post_b = create_test_scheduled_post(user_id=2) # Belongs to user 2
    seeded_db_session.add(post_b)
    await seeded_db_session.commit()
    
    # Client is authenticated as user 1
    resp = await integration_client.get(f"/api/v1/scheduled-posts/{post_b.id}")
    assert resp.status_code == 404 # Should not exist from user 1's perspective
