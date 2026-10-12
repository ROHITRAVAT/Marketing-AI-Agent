"""
Integration tests for the Approval workflow.
Tests: approval pauses workflow, resume+publish, rejection stops everything,
       double-approval idempotency, user isolation.
Covers requirements §12, §13, §20.
"""
import pytest
import uuid
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from unittest.mock import patch, MagicMock, AsyncMock

from app.models.scheduled_post import ScheduledPost
from app.models.approval import ApprovalRequest

pytestmark = [pytest.mark.asyncio, pytest.mark.integration, pytest.mark.approval]


def _mock_chains():
    mock_text = MagicMock()
    mock_text.ainvoke = AsyncMock(return_value="Approval test content")
    mock_json = MagicMock()
    mock_json.ainvoke = AsyncMock(return_value={
        "steps": [{"step_id": 1, "description": "social media post on linkedin", "dependency": []}]
    })
    mock_review = MagicMock()
    mock_review.ainvoke = AsyncMock(return_value={
        "approved": True, "score": 9.5, "feedback": "Good", "issues": []
    })
    mock_extraction = MagicMock()
    class MockExtraction:
        def __init__(self):
            self.product = "AI"
            self.target_audience = "All"
            self.platform = "LinkedIn"
            self.campaign_goal = "Test"
    mock_extraction.ainvoke = AsyncMock(return_value=MockExtraction())

    return (
        patch("app.agents.nodes.strategy.build_text_chain", return_value=mock_text),
        patch("app.agents.nodes.content.build_text_chain", return_value=mock_text),
        patch("app.agents.nodes.planning.build_json_chain", return_value=mock_json),
        patch("app.agents.nodes.review.build_json_chain", return_value=mock_review),
        patch("app.agents.nodes.analyze.build_structured_chain", return_value=mock_extraction),
        patch("app.agents.nodes.retrieval.retrieve_documents", new_callable=AsyncMock),
    )


async def _start_agent_and_get_approval(client: AsyncClient, platform: str = "LinkedIn"):
    """Helper: Start agent, wait for approval, return approval_id."""
    p1, p2, p3, p4, p5, p6 = _mock_chains()
    with p1, p2, p3, p4, p5, p6:
        resp = await client.post("/api/v1/agent/chat", json={
            "thread_id": str(uuid.uuid4()),
            "message": f"Create a {platform} post",
            "platform": platform,
            "product": "Test Product",
            "target_audience": "Developers",
            "campaign_goal": "Engagement"
        })
        assert resp.status_code == 202
        job_id = resp.json()["job_id"]
        from tests.conftest import poll_agent_job
        data = await poll_agent_job(client, job_id)
    assert data["status"] == "approval_pending"

    approvals = await client.get("/api/v1/approvals/pending")
    items = approvals.json()["items"]
    assert len(items) > 0
    return items[0]["id"]


# ── Test: Approval Pauses Workflow ───────────────────────────────────────────

async def test_approval_pauses_workflow(
    integration_client: AsyncClient,
    seeded_db_session: AsyncSession,
):
    """Agent workflow must pause at approval node for social media content."""
    approval_id = await _start_agent_and_get_approval(integration_client)
    assert approval_id is not None

    # Verify status in DB
    result = await seeded_db_session.execute(
        select(ApprovalRequest).where(ApprovalRequest.id == approval_id)
    )
    approval = result.scalar_one()
    assert approval.status == "pending"


# ── Test: Approval Resumes and Triggers Execution ────────────────────────────

async def test_approve_resumes_workflow(
    integration_client: AsyncClient,
    seeded_db_session: AsyncSession,
    mock_social_platforms,
):
    """Approving a request resumes the graph and executes tools."""
    approval_id = await _start_agent_and_get_approval(integration_client)

    client = integration_client
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="mock_token"):
        resp = await integration_client.post(
            f"/api/v1/approvals/{approval_id}/approve",
            json={"reason": "Approved by test"}
        )
        assert resp.status_code == 200
        job_id = resp.json()["job_id"]
        from tests.conftest import poll_agent_job
        job_data = await poll_agent_job(integration_client, job_id)
        data = job_data.get("result") or job_data
        data["status"] = job_data["status"]
    await seeded_db_session.commit()
    result = await seeded_db_session.execute(
        select(ApprovalRequest).where(ApprovalRequest.id == approval_id)
    )
    approval = result.scalar_one()
    assert approval.status == "approved"


# ── Test: Rejection Prevents Publishing ──────────────────────────────────────

async def test_rejection_prevents_publishing(
    integration_client: AsyncClient,
    seeded_db_session: AsyncSession,
):
    """Rejecting a request must NOT trigger tool execution or create posts."""
    approval_id = await _start_agent_and_get_approval(integration_client, "Facebook")

    with patch("app.agents.nodes.tools.execute_tools") as mock_exec:
        resp = await integration_client.post(
            f"/api/v1/approvals/{approval_id}/reject",
            json={"reason": "Not appropriate for our brand"}
        )
        assert resp.status_code == 200

        await asyncio.sleep(0.3)
        mock_exec.assert_not_called()

    # DB should have no published posts
    await seeded_db_session.commit()
    posts = (await seeded_db_session.execute(
        select(ScheduledPost).where(ScheduledPost.user_id == 1)
    )).scalars().all()

    published = [p for p in posts if p.status == "published"]
    assert len(published) == 0

    # Approval status should be rejected
    result = await seeded_db_session.execute(
        select(ApprovalRequest).where(ApprovalRequest.id == approval_id)
    )
    approval = result.scalar_one()
    assert approval.status == "rejected"
    assert approval.rejection_reason == "Not appropriate for our brand"


# ── Test: Double Approval Is Idempotent ──────────────────────────────────────

async def test_double_approval_idempotent(
    integration_client: AsyncClient,
    seeded_db_session: AsyncSession,
    mock_social_platforms,
):
    """Approving an already-approved request should not crash or re-execute."""
    approval_id = await _start_agent_and_get_approval(integration_client)

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="mock_token"):
        resp1 = await integration_client.post(
            f"/api/v1/approvals/{approval_id}/approve",
            json={"reason": "First approval"}
        )
        assert resp1.status_code == 200

        # Second attempt
        resp2 = await integration_client.post(
            f"/api/v1/approvals/{approval_id}/approve",
            json={"reason": "Duplicate approval"}
        )
        # Should not crash — the service returns the existing approval or 404
        assert resp2.status_code in (200, 404)


# ── Test: Approval + Publishing End-to-End ───────────────────────────────────

async def test_approval_then_publish_creates_post(
    integration_client: AsyncClient,
    seeded_db_session: AsyncSession,
    mock_social_platforms,
):
    """
    Full flow: Generate content → Approval pending → User approves →
    execute_tools → Post created in DB with external ID.
    """
    approval_id = await _start_agent_and_get_approval(integration_client)

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="mock_token"):
        await integration_client.post(
            f"/api/v1/approvals/{approval_id}/approve",
            json={"reason": "Ship it"}
        )

    # Check that a ScheduledPost was created with published status
    await seeded_db_session.commit()
    posts = (await seeded_db_session.execute(
        select(ScheduledPost).where(ScheduledPost.user_id == 1, ScheduledPost.status == "published")
    )).scalars().all()

    assert len(posts) >= 1
    post = posts[0]
    assert post.external_post_id is not None
    assert post.platform.lower() == "linkedin"
