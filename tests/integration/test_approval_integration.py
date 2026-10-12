import pytest
import uuid
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, MagicMock, AsyncMock

pytestmark = pytest.mark.asyncio

async def test_approval_rejection_halts_graph(integration_client: AsyncClient, seeded_db_session: AsyncSession):
    # Mocking chains
    mock_text_chain = MagicMock()
    mock_text_chain.ainvoke = AsyncMock(return_value="Mocked LLM Content")
    
    mock_planning_chain = MagicMock()
    mock_planning_chain.ainvoke = AsyncMock(return_value={
        "steps": [
            {"step_id": 1, "description": "social media post on facebook", "dependency": []}
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
         patch("app.agents.nodes.analyze.build_structured_chain", return_value=mock_extraction), \
         patch("app.agents.nodes.retrieval.retrieve_documents", new_callable=AsyncMock) as mock_retrieve:
        
        mock_retrieve.return_value = {"retrieved_documents": []}
        
        # 1. Send chat request to start the agent
        chat_response = await integration_client.post("/api/v1/agent/chat",
            json={
                "thread_id": "test-thread-id-approval-123",
                "message": "Create a Facebook post",
                "platform": "Facebook",
                "product": "AI Tester",
                "target_audience": "Developers",
                "campaign_goal": "Launch"
            }
        )
        assert chat_response.status_code == 202
        job_id = chat_response.json()["job_id"]
        from tests.conftest import poll_agent_job
        data = await poll_agent_job(integration_client, job_id)
        print("\n\nCHAT RESPONSE:", chat_response.json(), "\n\n")
        
    approvals_response = await integration_client.get("/api/v1/approvals/pending")
    assert approvals_response.status_code == 200
    approvals_data = approvals_response.json()
    assert len(approvals_data["items"]) > 0
    
    approval_id = approvals_data["items"][0]["id"]
    
    # 3. Reject the content
    with patch("app.agents.nodes.tools.execute_tools") as mock_execute_tools:
        reject_response = await integration_client.post(
            f"/api/v1/approvals/{approval_id}/reject",
            json={"reason": "Rejected by integration test"}
        )
        assert reject_response.status_code == 200
        
        # Give some time for background tasks if any, then assert
        await asyncio.sleep(0.5)
        
        # execute_tools should never be called if rejected
        mock_execute_tools.assert_not_called()
        
    # Check scheduled posts, none should have been created
    scheduled_posts_response = await integration_client.get("/api/v1/scheduled-posts/")
    assert len(scheduled_posts_response.json()) == 0

async def test_thread_id_isolation(integration_client: AsyncClient, seeded_db_session: AsyncSession):
    thread_1_id = str(uuid.uuid4())
    thread_2_id = str(uuid.uuid4())
    
    # Mocking chains
    mock_text_chain = MagicMock()
    mock_text_chain.ainvoke = AsyncMock(return_value="Mocked LLM Content")
    
    mock_planning_chain = MagicMock()
    mock_planning_chain.ainvoke = AsyncMock(return_value={
        "steps": [
            {"step_id": 1, "description": "social media post", "dependency": []}
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
         patch("app.agents.nodes.analyze.build_structured_chain", return_value=mock_extraction), \
         patch("app.agents.nodes.retrieval.retrieve_documents", new_callable=AsyncMock) as mock_retrieve:
        
        mock_retrieve.return_value = {"retrieved_documents": []}
        
        # Start Thread 1
        chat_resp_1 = await integration_client.post("/api/v1/agent/chat",
            json={
                "thread_id": thread_1_id,
                "message": "Thread 1 post",
                "platform": "Twitter/X",
                "product": "Prod 1",
                "target_audience": "Aud 1",
                "campaign_goal": "Goal 1"
            }
        )
        assert chat_resp_1.status_code == 202
        job_id = chat_resp_1.json()["job_id"]
        from tests.conftest import poll_agent_job
        data = await poll_agent_job(integration_client, job_id)# Start Thread 2
        chat_resp_2 = await integration_client.post("/api/v1/agent/chat",
            json={
                "thread_id": thread_2_id,
                "message": "Thread 2 post",
                "platform": "Instagram",
                "product": "Prod 2",
                "target_audience": "Aud 2",
                "campaign_goal": "Goal 2"
            }
        )
        assert chat_resp_2.status_code == 202
        job_id = chat_resp_2.json()["job_id"]
        from tests.conftest import poll_agent_job
        data = await poll_agent_job(integration_client, job_id)# Both should be in waiting_for_approval state
        approvals_response = await integration_client.get("/api/v1/approvals/pending")
        approvals_data = approvals_response.json()["items"]
        assert len(approvals_data) >= 2
        
        # The approvals correspond to different threads, which proves isolated execution.
        threads_found = [a["thread_id"] for a in approvals_data if a["thread_id"] in [thread_1_id, thread_2_id]]
        assert thread_1_id in threads_found
        assert thread_2_id in threads_found
