"""
Integration tests for the Agent Chat API endpoint (POST /api/v1/agent/chat).
Tests: authentication, request validation, state creation, thread ID,
       graph invocation, response schema, workflow status.
Covers requirements §8, §9, §10, §11.
"""
import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, MagicMock, AsyncMock

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


# ── Shared chain mocks ──────────────────────────────────────────────────────

def _mock_chains():
    """Returns context managers that mock all LLM chains deterministically."""
    mock_text = MagicMock()
    mock_text.ainvoke = AsyncMock(return_value="Mocked AI Content for testing")

    mock_json = MagicMock()
    mock_json.ainvoke = AsyncMock(return_value={
        "steps": [{"step_id": 1, "description": "social media post on linkedin", "dependency": []}]
    })

    mock_review = MagicMock()
    mock_review.ainvoke = AsyncMock(return_value={
        "approved": True, "score": 9.5, "feedback": "Looks great", "issues": []
    })

    mock_extraction = MagicMock()
    # Return an object that has product, target_audience, platform, campaign_goal
    # Wait, the node does: result = await chain.ainvoke(...)
    # and then result.product etc. So it must be an object (RequestExtraction instance)
    class MockExtraction:
        def __init__(self):
            self.product = "AI Tester"
            self.target_audience = "Developers"
            self.platform = "LinkedIn"
            self.campaign_goal = "Launch"
    mock_extraction.ainvoke = AsyncMock(return_value=MockExtraction())

    return (
        patch("app.agents.nodes.strategy.build_text_chain", return_value=mock_text),
        patch("app.agents.nodes.content.build_text_chain", return_value=mock_text),
        patch("app.agents.nodes.planning.build_json_chain", return_value=mock_json),
        patch("app.agents.nodes.review.build_json_chain", return_value=mock_review),
        patch("app.agents.nodes.analyze.build_structured_chain", return_value=mock_extraction),
        patch("app.agents.nodes.retrieval.retrieve_documents", new_callable=AsyncMock),
    )


# ── Test: Response Schema ────────────────────────────────────────────────────

async def test_agent_chat_returns_correct_schema(
    integration_client: AsyncClient,
    seeded_db_session: AsyncSession,
):
    """Verify the response contains all fields required by the frontend."""
    p1, p2, p3, p4, p5, p6 = _mock_chains()
    with p1, p2, p3, p4, p5, p6:
        resp = await integration_client.post("/api/v1/agent/chat", json={
            "thread_id": str(uuid.uuid4()),
            "message": "Create a LinkedIn post for our new AI product",
            "platform": "LinkedIn",
            "product": "AI Tester",
            "target_audience": "Developers",
            "campaign_goal": "Launch"
        })
        assert resp.status_code == 202
        job_id = resp.json()["job_id"]
        from tests.conftest import poll_agent_job
        data = await poll_agent_job(integration_client, job_id)

    # Must have these fields per AgentChatResponse schema
    assert "status" in data
    assert "thread_id" in data
    assert "final_response" in data or data.get("approval_required") is True
    assert "approval_required" in data
    assert data["status"] in ("completed", "approval_pending", "failed")


# ── Test: Request Validation ─────────────────────────────────────────────────

async def test_agent_chat_rejects_empty_message(
    integration_client: AsyncClient,
    seeded_db_session: AsyncSession,
):
    """Agent chat should reject a request with an empty message."""
    resp = await integration_client.post("/api/v1/agent/chat", json={
        "thread_id": "test-thread",
        "message": "",
    })
    assert resp.status_code == 422  # Pydantic validation


async def test_agent_chat_rejects_missing_thread_id(
    integration_client: AsyncClient,
    seeded_db_session: AsyncSession,
):
    """thread_id is required."""
    resp = await integration_client.post("/api/v1/agent/chat", json={
        "message": "Test message without thread_id",
    })
    assert resp.status_code == 422


# ── Test: Thread ID Preservation ─────────────────────────────────────────────

async def test_thread_id_preserved_across_requests(
    integration_client: AsyncClient,
    seeded_db_session: AsyncSession,
):
    """Same thread_id across two requests should reuse the same conversation state."""
    thread_id = str(uuid.uuid4())
    p1, p2, p3, p4, p5, p6 = _mock_chains()

    with p1, p2, p3, p4, p5, p6:
        resp1 = await integration_client.post("/api/v1/agent/chat", json={
            "thread_id": thread_id,
            "message": "First message in thread",
            "platform": "LinkedIn",
            "product": "Product A",
            "target_audience": "Engineers",
            "campaign_goal": "Awareness"
        })
        assert resp1.status_code == 202
        job_id = resp1.json()["job_id"]
        from tests.conftest import poll_agent_job
        job_data = await poll_agent_job(integration_client, job_id)
        data1 = job_data.get("result") or job_data
        data1["status"] = job_data["status"]
    assert data1["thread_id"] == thread_id

    # Second request with same thread — if the first paused at approval,
    # the second should detect that and return approval_pending.
    with p1, p2, p3, p4, p5, p6:
        resp2 = await integration_client.post("/api/v1/agent/chat", json={
            "thread_id": thread_id,
            "message": "Follow up in same thread",
        })
        assert resp2.status_code == 202
        job_id = resp2.json()["job_id"]
        from tests.conftest import poll_agent_job
        job_data = await poll_agent_job(integration_client, job_id)
        data2 = job_data.get("result") or job_data
        data2["status"] = job_data["status"]
    assert data2["thread_id"] == thread_id


async def test_different_threads_are_isolated(
    integration_client: AsyncClient,
    seeded_db_session: AsyncSession,
):
    """Different thread_ids create isolated state."""
    thread_a = str(uuid.uuid4())
    thread_b = str(uuid.uuid4())

    p1, p2, p3, p4, p5, p6 = _mock_chains()
    with p1, p2, p3, p4, p5, p6:
        resp_a = await integration_client.post("/api/v1/agent/chat", json={
            "thread_id": thread_a,
            "message": "Thread A content",
            "platform": "LinkedIn",
            "product": "Prod A",
            "target_audience": "Aud A",
            "campaign_goal": "Goal A"
        })
        
        from tests.conftest import poll_agent_job
        job_id_a = resp_a.json()["job_id"]
        data_a = await poll_agent_job(integration_client, job_id_a)
        assert data_a["thread_id"] == thread_a

        resp_b = await integration_client.post("/api/v1/agent/chat", json={
            "thread_id": thread_b,
            "message": "Thread B content",
            "platform": "Twitter/X",
            "product": "Prod B",
            "target_audience": "Aud B",
            "campaign_goal": "Goal B"
        })

        job_id_b = resp_b.json()["job_id"]
        data_b = await poll_agent_job(integration_client, job_id_b)
        assert data_b["thread_id"] == thread_b

        # Both should have generated separate approval requests
        approvals_resp = await integration_client.get("/api/v1/approvals/pending")
        assert approvals_resp.status_code == 200
        threads = [a["thread_id"] for a in approvals_resp.json()["items"]]
        assert thread_a in threads
        assert thread_b in threads


# ── Test: Workflow Status ────────────────────────────────────────────────────

async def test_social_platform_triggers_approval(
    integration_client: AsyncClient,
    seeded_db_session: AsyncSession,
):
    """A social media request should pause at the approval node."""
    p1, p2, p3, p4, p5, p6 = _mock_chains()
    with p1, p2, p3, p4, p5, p6:
        resp = await integration_client.post("/api/v1/agent/chat", json={
            "thread_id": str(uuid.uuid4()),
            "message": "Write a Facebook post",
            "platform": "Facebook",
            "product": "Test Product",
            "target_audience": "Marketing teams",
            "campaign_goal": "Engagement"
        })
        assert resp.status_code == 202
        job_id = resp.json()["job_id"]
        from tests.conftest import poll_agent_job
        data = await poll_agent_job(integration_client, job_id)
        assert data["status"] == "approval_pending"
        assert data["approval_required"] is True
        assert data["approval_request_id"] is not None


# ── Test: Error Handling ─────────────────────────────────────────────────────

async def test_agent_chat_handles_internal_error(
    integration_client: AsyncClient,
    seeded_db_session: AsyncSession,
):
    """If the graph throws an unexpected error, the API should return a safe error."""
    with patch("app.services.agent_service.build_marketing_graph", side_effect=Exception("Unexpected boom")):
        resp = await integration_client.post("/api/v1/agent/chat", json={
            "thread_id": str(uuid.uuid4()),
            "message": "This should fail safely",
        })

        assert resp.status_code == 202
        job_id = resp.json()["job_id"]
        from tests.conftest import poll_agent_job
        data = await poll_agent_job(integration_client, job_id)
        assert data["status"] == "failed"
        assert data.get("error") is not None
        # Must not expose internal stack traces
        assert "Traceback" not in (data.get("error") or "")
