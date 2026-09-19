"""
Security integration tests.
Tests: user isolation for campaigns, posts, analytics, accounts, and authentication guards.
Covers requirements §47, §49.
"""
import pytest
from datetime import datetime, timezone, timedelta
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from unittest.mock import patch

from app.models.campaign import Campaign
from app.models.scheduled_post import ScheduledPost
from app.models.integration import IntegrationConnection
from app.models.social_analytics import SocialAnalytics
from tests.fixtures.factories import (
    create_test_campaign,
    create_test_scheduled_post,
    create_test_integration,
    create_test_analytics,
)

pytestmark = [pytest.mark.asyncio, pytest.mark.integration, pytest.mark.security]

@pytest.fixture(autouse=True)
async def setup_security_test(seeded_db_session: AsyncSession):
    """Ensure User 2 exists for isolation testing."""
    from app.models.user import User
    from sqlalchemy import select, delete
    
    # Also clean up any connections to avoid MultipleResultsFound
    await seeded_db_session.execute(delete(IntegrationConnection))
    
    user_2 = await seeded_db_session.get(User, 2)
    if not user_2:
        user_2 = User(id=2, email="user2@test.com", hashed_password="pw")
        seeded_db_session.add(user_2)
    
    await seeded_db_session.commit()
# ── Test: User Isolation ─────────────────────────────────────────────────────

async def test_user_isolation_campaigns(integration_client, seeded_db_session: AsyncSession):
    """User B cannot access User A's campaigns."""
    camp_a = create_test_campaign(user_id=1, campaign_id=101)
    # Assume user 2 exists or the DB doesn't enforce FK strictly for this test
    # (seeded_db_session should have user 1 from conftest)
    camp_b = create_test_campaign(user_id=2, campaign_id=102)
    seeded_db_session.add_all([camp_a, camp_b])
    await seeded_db_session.commit()

    # The client is authenticated as user 1 via dependency override
    resp = await integration_client.get("/api/v1/campaigns/")
    assert resp.status_code == 200
    data = resp.json()

    # Should only see user 1's campaign
    ids = [c["id"] for c in data.get("items", [])]
    assert 101 in ids
    assert 102 not in ids


async def test_user_isolation_scheduled_posts(integration_client, seeded_db_session: AsyncSession):
    """User B cannot access User A's scheduled posts."""
    post_a = create_test_scheduled_post(user_id=1)
    post_b = create_test_scheduled_post(user_id=2)
    seeded_db_session.add_all([post_a, post_b])
    await seeded_db_session.commit()
    await seeded_db_session.refresh(post_a)
    await seeded_db_session.refresh(post_b)

    # List endpoint
    resp = await integration_client.get("/api/v1/scheduled-posts/")
    assert resp.status_code == 200
    ids = [p["id"] for p in resp.json()]
    assert post_a.id in ids
    assert post_b.id not in ids

    # GET specific endpoint
    resp_b = await integration_client.get(f"/api/v1/scheduled-posts/{post_b.id}")
    assert resp_b.status_code == 404


async def test_user_isolation_analytics(integration_client, seeded_db_session: AsyncSession):
    """User B cannot see User A's analytics."""
    ana_a = create_test_analytics(user_id=1, impressions=1000)
    ana_b = create_test_analytics(user_id=2, impressions=2000)
    seeded_db_session.add_all([ana_a, ana_b])
    await seeded_db_session.commit()

    today = datetime.now(timezone.utc).date()
    start = (today - timedelta(days=1)).isoformat()
    end = (today + timedelta(days=1)).isoformat()

    resp = await integration_client.get(f"/api/v1/analytics/summary?start_date={start}&end_date={end}")
    assert resp.status_code == 200
    data = resp.json()
    # Should only aggregate User 1's 1000 impressions
    assert data["overall_impressions"] == 1000


async def test_user_isolation_oauth_connections(integration_client, seeded_db_session: AsyncSession):
    """User B cannot use User A's OAuth tokens."""
    conn_a = create_test_integration(user_id=1, provider="linkedin", provider_user_id="user_a_li")
    conn_b = create_test_integration(user_id=2, provider="twitter", provider_user_id="user_b_tw")
    seeded_db_session.add_all([conn_a, conn_b])
    await seeded_db_session.commit()

    # The client is User 1. If we try to check connection status for Twitter,
    # it should return nothing, because User 1 doesn't have a Twitter connection.
    from app.core.oauth.manager import TokenManager
    conn_status = await TokenManager.get_connection_status(1, "twitter", seeded_db_session)
    assert conn_status is None


# ── Test: Auth Guards ────────────────────────────────────────────────────────

# Note: Since auth isn't fully implemented in deps.py (raises NotImplementedError)
# and we mock it, we simulate what the real auth flow would do.

async def test_no_credentials_in_error_responses(integration_client, seeded_db_session: AsyncSession):
    """Ensure error messages never leak sensitive tokens."""
    # Simulate an error that might contain a token
    with patch("app.services.agent_service.AgentService.chat", side_effect=Exception("Failed with token: secret_xyz")):
        resp = await integration_client.post("/api/v1/agent/chat", json={
            "thread_id": "test",
            "message": "test",
        })
        
    assert resp.status_code == 500
    data = resp.json()
    assert "secret_xyz" not in data.get("message", "")
    assert "secret_xyz" not in str(data)
    assert "Traceback" not in data.get("error", "")
