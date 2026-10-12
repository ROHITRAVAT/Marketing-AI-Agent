import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from unittest.mock import patch, MagicMock, AsyncMock

from app.models.scheduled_post import ScheduledPost

pytestmark = pytest.mark.asyncio

async def test_multi_platform_isolation(integration_client: AsyncClient, seeded_db_session: AsyncSession, mock_social_platforms):
    
    # 1. Mocking chains to output multiple platforms
    mock_text_chain = MagicMock()
    mock_text_chain.ainvoke = AsyncMock(return_value="Multi-platform content")

    mock_planning_chain = MagicMock()
    mock_planning_chain.ainvoke = AsyncMock(return_value={
        "steps": [
            {"step_id": 1, "description": "social media post on linkedin", "dependency": []},
            {"step_id": 2, "description": "social media post on facebook", "dependency": []}
        ]
    })
    
    mock_review_chain = MagicMock()
    mock_review_chain.ainvoke = AsyncMock(return_value={
        "approved": True,
        "score": 10.0,
        "feedback": "Looks good",
        "issues": []
    })
    mock_extraction = MagicMock()
    class MockExtraction:
        def __init__(self):
            self.product = "AI Tester"
            self.target_audience = "All"
            self.platform = "LinkedIn"
            self.campaign_goal = "Test"
    mock_extraction.ainvoke = AsyncMock(return_value=MockExtraction())
    
    with patch("app.agents.nodes.strategy.build_text_chain", return_value=mock_text_chain), \
         patch("app.agents.nodes.content.build_text_chain", return_value=mock_text_chain), \
         patch("app.agents.nodes.planning.build_json_chain", return_value=mock_planning_chain), \
         patch("app.agents.nodes.review.build_json_chain", return_value=mock_review_chain), \
         patch("app.agents.nodes.tools.build_social_media_chain", return_value=mock_text_chain), \
         patch("app.agents.nodes.analyze.build_structured_chain", return_value=mock_extraction), \
         patch("app.agents.nodes.retrieval.retrieve_documents", new_callable=AsyncMock) as mock_retrieve:
        
        
        
        # Start agent
        chat_resp = await integration_client.post("/api/v1/agent/chat",
            json={
                "thread_id": "test-multi-platform-thread",
                "message": "Post this everywhere",
                "platform": "Multi",
                "product": "AI",
                "target_audience": "Everyone",
                "campaign_goal": "Brand Awareness"
            }
        )
        assert chat_resp.status_code == 202
        job_id = chat_resp.json()["job_id"]
        from tests.conftest import poll_agent_job
        data = await poll_agent_job(integration_client, job_id)# Get pending approval
    approvals_response = await integration_client.get("/api/v1/approvals/pending")
    approvals_data = approvals_response.json()["items"]
    # Usually one approval per thread
    approval_id = approvals_data[0]["id"]
    
    # We want one platform to fail during execution, one to succeed.
    # However, since they are just being scheduled, execute_tools just inserts ScheduledPost.
    # The actual external API call happens in the scheduler.
    
    # Approve
    approve_response = await integration_client.post(
        f"/api/v1/approvals/{approval_id}/approve",
        json={"reason": "Approved"}
    )
    assert approve_response.status_code == 200
    
    # Verify only one was scheduled (LinkedIn succeeds, Facebook fails)
    await seeded_db_session.commit()
    scheduled_posts_response = await integration_client.get("/api/v1/scheduled-posts/")
    scheduled_posts = scheduled_posts_response.json()
    
    assert len(scheduled_posts) == 2
    platforms = [p["platform"].lower() for p in scheduled_posts]
    assert "linkedin" in platforms
    assert "facebook" in platforms
    
    # Force them to be pending so the scheduler will process them
    from sqlalchemy import update
    from app.models.scheduled_post import ScheduledPost
    await seeded_db_session.execute(
        update(ScheduledPost).values(status="scheduled", external_post_id=None)
    )
    await seeded_db_session.commit()
    seeded_db_session.expire_all()
    
    # DEBUG PRINT
    debug_posts = (await seeded_db_session.execute(select(ScheduledPost))).scalars().all()
    for dp in debug_posts:
        print(f"DEBUG POST: {dp.id}, {dp.status}, {dp.scheduled_time}, {dp.platform}")

    # Now run scheduler. We will mock the social provider for facebook to throw an exception,
    # but linkedin to succeed.
    from app.scheduler.worker import poll_and_process_jobs
    
    class MockSideEffectResponse:
        def __init__(self, json_data, status_code):
            self._json_data = json_data
            self.status_code = status_code
        def json(self):
            return self._json_data
        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP Error: {self.status_code}")

    async def mock_post_side_effect(self, url, *args, **kwargs):
        if "facebook" in url or "graph.facebook" in url or "graph.meta" in url:
            raise Exception("Facebook API is down!")
        else:
            return MockSideEffectResponse({"id": "mock_external_id_linkedin"}, 200)

    # We override httpx.AsyncClient.post directly
    with patch("httpx.AsyncClient.post", new=mock_post_side_effect), \
         patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_get_token:
        mock_get_token.return_value = "mock_valid_token"

        await poll_and_process_jobs()
import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from unittest.mock import patch, MagicMock, AsyncMock

from app.models.scheduled_post import ScheduledPost

pytestmark = pytest.mark.asyncio

async def test_multi_platform_isolation(integration_client: AsyncClient, seeded_db_session: AsyncSession, mock_social_platforms):
    
    # 1. Mocking chains to output multiple platforms
    mock_text_chain = MagicMock()
    mock_text_chain.ainvoke = AsyncMock(return_value="Multi-platform content")

    mock_planning_chain = MagicMock()
    mock_planning_chain.ainvoke = AsyncMock(return_value={
        "steps": [
            {"step_id": 1, "description": "social media post on linkedin", "dependency": []},
            {"step_id": 2, "description": "social media post on facebook", "dependency": []}
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
         patch("app.agents.nodes.tools.build_social_media_chain", return_value=mock_text_chain), \
         patch("app.agents.nodes.retrieval.retrieve_documents", new_callable=AsyncMock) as mock_retrieve:
        
        
        
        # Start agent
        chat_resp = await integration_client.post("/api/v1/agent/chat",
            json={
                "thread_id": "test-multi-platform-thread",
                "message": "Post this everywhere",
                "platform": "Multi",
                "product": "AI",
                "target_audience": "Everyone",
                "campaign_goal": "Brand Awareness"
            }
        )
        assert chat_resp.status_code == 202
        job_id = chat_resp.json()["job_id"]
        from tests.conftest import poll_agent_job
        data = await poll_agent_job(integration_client, job_id)# Get pending approval
    approvals_response = await integration_client.get("/api/v1/approvals/pending")
    approvals_data = approvals_response.json()["items"]
    # Usually one approval per thread
    approval_id = approvals_data[0]["id"]
    
    # We want one platform to fail during execution, one to succeed.
    # However, since they are just being scheduled, execute_tools just inserts ScheduledPost.
    # The actual external API call happens in the scheduler.
    
    # Approve
    approve_response = await integration_client.post(
        f"/api/v1/approvals/{approval_id}/approve",
        json={"reason": "Approved"}
    )
    assert approve_response.status_code == 200
    
    # Verify only one was scheduled (LinkedIn succeeds, Facebook fails)
    await seeded_db_session.commit()
    scheduled_posts_response = await integration_client.get("/api/v1/scheduled-posts/")
    scheduled_posts = scheduled_posts_response.json()
    
    assert len(scheduled_posts) == 2
    platforms = [p["platform"].lower() for p in scheduled_posts]
    assert "linkedin" in platforms
    assert "facebook" in platforms
    
    # Force them to be pending so the scheduler will process them
    from sqlalchemy import update
    from app.models.scheduled_post import ScheduledPost
    await seeded_db_session.execute(
        update(ScheduledPost).values(status="scheduled", external_post_id=None)
    )
    await seeded_db_session.commit()
    seeded_db_session.expire_all()
    
    # DEBUG PRINT
    debug_posts = (await seeded_db_session.execute(select(ScheduledPost))).scalars().all()
    for dp in debug_posts:
        print(f"DEBUG POST: {dp.id}, {dp.status}, {dp.scheduled_time}, {dp.platform}")

    # Now run scheduler. We will mock the social provider for facebook to throw an exception,
    # but linkedin to succeed.
    from app.scheduler.worker import poll_and_process_jobs
    
    class MockSideEffectResponse:
        def __init__(self, json_data, status_code):
            self._json_data = json_data
            self.status_code = status_code
        def json(self):
            return self._json_data
        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP Error: {self.status_code}")

    async def mock_post_side_effect(self, url, *args, **kwargs):
        if "facebook" in url or "graph.facebook" in url or "graph.meta" in url:
            raise Exception("Facebook API is down!")
        else:
            return MockSideEffectResponse({"id": "mock_external_id_linkedin"}, 200)

    # We override httpx.AsyncClient.post directly
    with patch("httpx.AsyncClient.post", new=mock_post_side_effect), \
         patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_get_token:
        mock_get_token.return_value = "mock_valid_token"

        await poll_and_process_jobs()
        
    # Re-verify posts in DB
    await seeded_db_session.commit()
    seeded_db_session.expire_all()
    stmt = select(ScheduledPost)
    final_posts = (await seeded_db_session.execute(stmt)).scalars().all()
    
    for post in final_posts:
        if post.platform.lower() == "linkedin":
            assert post.status == "published"
            assert post.external_post_id == "mock_external_id_linkedin"
        elif post.platform.lower() == "facebook":
            assert post.status == "scheduled"
            assert post.attempt_count > 0
            assert "Tool execution did not report success" in post.error_message
            assert post.external_post_id is None
