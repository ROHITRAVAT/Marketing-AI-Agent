import pytest
import uuid
import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from unittest.mock import patch, MagicMock, AsyncMock

from app.models.scheduled_post import ScheduledPost
from app.models.social_analytics import SocialAnalytics
from app.models.approval import ApprovalRequest
from app.models.user import User

pytestmark = pytest.mark.asyncio

async def test_full_agent_flow(integration_client: AsyncClient, seeded_db_session: AsyncSession, mock_social_platforms):
    """
    Test the complete end-to-end integration:
    Frontend Request -> Graph -> Wait for Approval -> Approve -> Schedule -> Publish -> Analytics -> Dashboard
    """
    
    # We will mock the LLM chains inside the LangGraph to make it deterministic
    # and fast. We don't want to test the LLM's creativity here, we want to test
    # the orchestration and database transitions.
    
    # Mocking chains
    mock_text_chain = MagicMock()
    mock_text_chain.ainvoke = AsyncMock(return_value="Mocked LLM Content")
    
    mock_planning_chain = MagicMock()
    # Mock a plan that will dispatch the LinkedIn tool
    mock_planning_chain.ainvoke = AsyncMock(return_value={
        "steps": [
            {"step_id": 1, "description": "social media post on linkedin", "dependency": []}
        ]
    })

    mock_review_chain = MagicMock()
    mock_review_chain.ainvoke = AsyncMock(return_value={
        "approved": True,
        "score": 10.0,
        "feedback": "Looks good",
        "issues": []
    })
    
    with patch("app.agents.nodes.strategy.build_text_chain", return_value=mock_text_chain), \
         patch("app.agents.nodes.content.build_text_chain", return_value=mock_text_chain), \
         patch("app.agents.nodes.planning.build_json_chain", return_value=mock_planning_chain), \
         patch("app.agents.nodes.review.build_json_chain", return_value=mock_review_chain), \
         patch("app.agents.nodes.retrieval.retrieve_documents", new_callable=AsyncMock) as mock_retrieve:
        
        pass
        
        # 1. Send chat request to start the agent
        chat_response = await integration_client.post(
            "/api/v1/agent/chat",
            json={
                "thread_id": "test-thread-id-123",
                "message": "Create a LinkedIn post",
                "platform": "LinkedIn",
                "product": "AI Tester",
                "target_audience": "Developers",
                "campaign_goal": "Launch"
            }
        )
        assert chat_response.status_code == 200
        chat_data = chat_response.json()
        print(f"\n\nCHAT DATA: {chat_data}\n\n")
        assert chat_data["status"] == "approval_pending"
        
        thread_id = chat_data["thread_id"]
        
    # 2. Get pending approvals
    approvals_response = await integration_client.get("/api/v1/approvals/pending")
    assert approvals_response.status_code == 200
    approvals_data = approvals_response.json()
    assert len(approvals_data["items"]) > 0
    
    approval_id = approvals_data["items"][0]["id"]
    
    # 3. Approve the content. The tools execute block in approval_service will call execute_tools.
    # execute_tools will see "social" and hit the LinkedInService.
    # We must mock the actual social APIs (already done via mock_social_platforms fixture).
    
    # We must ensure the TokenManager returns a valid token so the provider service doesn't fail.
    # We can inject a mock token into the DB for the user, or mock the TokenManager.
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_get_token:
        mock_get_token.return_value = "mock_valid_token"
        
        approve_response = await integration_client.post(
            f"/api/v1/approvals/{approval_id}/approve",
            json={"reason": "Approved by integration test"}
        )
        assert approve_response.status_code == 200
        
    # 4. Verify the post was scheduled
    # Since our mocked tools executed, they should have scheduled the post.
    scheduled_posts_response = await integration_client.get("/api/v1/scheduled-posts/")
    assert scheduled_posts_response.status_code == 200
    scheduled_posts = scheduled_posts_response.json()
    assert len(scheduled_posts) > 0
    assert scheduled_posts[0]["status"] == "published"
    
    post_id = scheduled_posts[0]["id"]
    
    # 5. The post is currently scheduled (or published if the scheduled_at was in the past and processed inline?
    # Wait, the tools.py schedules posts if no scheduled time is given, usually setting it to 'processing' or a scheduled time.
    # Let's invoke the scheduler manually to process any due posts.
    from app.scheduler.worker import poll_and_process_jobs
    
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_get_token:
        mock_get_token.return_value = "mock_valid_token"
        
        await poll_and_process_jobs()
        
    # Check the database to see if the post is published
    await seeded_db_session.commit() # Ensure we read fresh data
    stmt = select(ScheduledPost).where(ScheduledPost.id == post_id)
    post_db = (await seeded_db_session.execute(stmt)).scalar_one()
    assert post_db.status == "published"
    assert post_db.external_post_id == "mock_external_id_123"
    
    # 6. Run Analytics Collection
    from app.scheduler.worker import poll_and_collect_analytics
    
    # The analytics polling should hit the mock_get provided in mock_social_platforms
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_get_token:
        mock_get_token.return_value = "mock_valid_token"
        
        await poll_and_collect_analytics()
        
    # Verify analytics were collected
    await seeded_db_session.commit()
    analytics_stmt = select(SocialAnalytics).where(SocialAnalytics.external_post_id == "mock_external_id_123")
    analytics_record = (await seeded_db_session.execute(analytics_stmt)).scalar_one_or_none()
    assert analytics_record is not None
    assert analytics_record.impressions == 2000
    assert analytics_record.engagement == 32
    assert analytics_record.reach is None
    
    # 7. Check the frontend analytics API
    start_date = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    end_date = datetime.date.today().isoformat()
    analytics_api_response = await integration_client.get(
        f"/api/v1/analytics/summary?start_date={start_date}&end_date={end_date}"
    )
    
    assert analytics_api_response.status_code == 200
    analytics_data = analytics_api_response.json()
    assert analytics_data["overall_impressions"] == 2000
    assert analytics_data["overall_engagement"] == 32
    assert len(analytics_data["platforms"]) >= 1
    
    print("Full agent integration test passed successfully!")
