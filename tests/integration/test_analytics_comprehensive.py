"""
Comprehensive analytics integration tests.
Tests: per-platform collection, normalization, idempotency, date range filtering,
       campaign aggregation, API response schema, agent tool query.
Covers requirements §29–§39.
"""
import pytest
import datetime
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from unittest.mock import patch, AsyncMock

from app.models.scheduled_post import ScheduledPost
from app.models.social_analytics import SocialAnalytics
from app.scheduler.worker import poll_and_collect_analytics
from app.services.analytics.service import AnalyticsService
from app.agents.tools.analytics_tool import get_analytics_summary_for_agent
from tests.fixtures.factories import create_published_post, create_test_analytics

pytestmark = [pytest.mark.asyncio, pytest.mark.integration, pytest.mark.analytics]


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _seed_published_posts(db, platforms=None, user_id=1):
    platforms = platforms or ["linkedin", "facebook", "instagram", "twitter"]
    posts = []
    for plat in platforms:
        p = create_published_post(user_id=user_id, platform=plat)
        posts.append(p)
    db.add_all(posts)
    await db.commit()
    return posts


# ── Test: Per-Platform Collection ────────────────────────────────────────────

async def test_linkedin_analytics_collected(seeded_db_session: AsyncSession, mock_social_platforms):
    """LinkedIn analytics are fetched and normalized correctly."""
    posts = await _seed_published_posts(seeded_db_session, ["linkedin"])

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="token"):
        await poll_and_collect_analytics()

    await seeded_db_session.commit()
    records = (await seeded_db_session.execute(
        select(SocialAnalytics).where(SocialAnalytics.platform == "linkedin")
    )).scalars().all()
    assert len(records) >= 1
    assert records[0].impressions is not None


async def test_facebook_analytics_collected(seeded_db_session: AsyncSession, mock_social_platforms):
    """Facebook analytics are fetched and normalized."""
    await _seed_published_posts(seeded_db_session, ["facebook"])

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="token"):
        await poll_and_collect_analytics()

    await seeded_db_session.commit()
    records = (await seeded_db_session.execute(
        select(SocialAnalytics).where(SocialAnalytics.platform == "facebook")
    )).scalars().all()
    assert len(records) >= 1


async def test_instagram_analytics_collected(seeded_db_session: AsyncSession, mock_social_platforms):
    """Instagram analytics are fetched and normalized."""
    await _seed_published_posts(seeded_db_session, ["instagram"])

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="token"):
        await poll_and_collect_analytics()

    await seeded_db_session.commit()
    records = (await seeded_db_session.execute(
        select(SocialAnalytics).where(SocialAnalytics.platform == "instagram")
    )).scalars().all()
    assert len(records) >= 1


async def test_twitter_analytics_collected(seeded_db_session: AsyncSession, mock_social_platforms):
    """Twitter analytics are fetched and normalized."""
    await _seed_published_posts(seeded_db_session, ["twitter"])

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="token"):
        await poll_and_collect_analytics()

    await seeded_db_session.commit()
    records = (await seeded_db_session.execute(
        select(SocialAnalytics).where(SocialAnalytics.platform == "twitter")
    )).scalars().all()
    assert len(records) >= 1


# ── Test: Idempotency ───────────────────────────────────────────────────────

async def test_analytics_idempotency(seeded_db_session: AsyncSession, mock_social_platforms):
    """Running analytics collection twice doesn't create duplicate rows."""
    await _seed_published_posts(seeded_db_session, ["linkedin"])

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="token"):
        await poll_and_collect_analytics()
        await poll_and_collect_analytics()

    await seeded_db_session.commit()
    count = (await seeded_db_session.execute(
        select(func.count(SocialAnalytics.id))
    )).scalar()
    assert count == 1  # Only 1 record, not 2


# ── Test: Date Range Filtering ───────────────────────────────────────────────

async def test_analytics_date_range_api(integration_client, seeded_db_session: AsyncSession):
    """Analytics summary API correctly filters by date range."""
    # Seed analytics records
    today = date.today()
    old_date = today - timedelta(days=30)

    record_today = create_test_analytics(user_id=1, metric_date=today, impressions=500)
    record_old = create_test_analytics(user_id=1, metric_date=old_date, impressions=1000)
    seeded_db_session.add_all([record_today, record_old])
    await seeded_db_session.commit()

    # Query only last 7 days
    start = (today - timedelta(days=7)).isoformat()
    end = today.isoformat()
    resp = await integration_client.get(f"/api/v1/analytics/summary?start_date={start}&end_date={end}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["overall_impressions"] == 500  # Only today's record


# ── Test: Campaign Aggregation ───────────────────────────────────────────────

async def test_analytics_campaign_filter(integration_client, seeded_db_session: AsyncSession):
    """Analytics summary can filter by campaign_id."""
    # Create campaigns first
    from tests.fixtures.factories import create_test_campaign
    camp_1 = create_test_campaign(user_id=1, campaign_id=42)
    camp_2 = create_test_campaign(user_id=1, campaign_id=99)
    seeded_db_session.add_all([camp_1, camp_2])
    await seeded_db_session.flush()

    today = date.today()
    camp_record = create_test_analytics(user_id=1, campaign_id=42, impressions=800)
    other_record = create_test_analytics(user_id=1, campaign_id=99, impressions=200)
    seeded_db_session.add_all([camp_record, other_record])
    await seeded_db_session.commit()

    start = (today - timedelta(days=1)).isoformat()
    end = today.isoformat()
    resp = await integration_client.get(
        f"/api/v1/analytics/summary?start_date={start}&end_date={end}&campaign_id=42"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["overall_impressions"] == 800


# ── Test: API Response Schema ────────────────────────────────────────────────

async def test_analytics_summary_response_schema(
    integration_client, seeded_db_session: AsyncSession
):
    """Analytics summary response matches the expected frontend schema."""
    record = create_test_analytics(user_id=1, impressions=1000, engagement=100)
    seeded_db_session.add(record)
    await seeded_db_session.commit()

    today = date.today()
    start = (today - timedelta(days=7)).isoformat()
    end = today.isoformat()
    resp = await integration_client.get(f"/api/v1/analytics/summary?start_date={start}&end_date={end}")
    assert resp.status_code == 200
    data = resp.json()

    assert "overall_impressions" in data
    assert "overall_engagement" in data
    assert "total_posts_analyzed" in data
    assert "platforms" in data
    assert isinstance(data["platforms"], list)
    if data["platforms"]:
        plat = data["platforms"][0]
        assert "platform" in plat
        assert "total_impressions" in plat
        assert "total_engagement" in plat


# ── Test: Agent Analytics Tool ───────────────────────────────────────────────

async def test_agent_analytics_tool(seeded_db_session: AsyncSession):
    """The agent analytics tool returns correct summary for the user."""
    record = create_test_analytics(user_id=1, impressions=5000, engagement=400)
    seeded_db_session.add(record)
    await seeded_db_session.commit()

    summary = await get_analytics_summary_for_agent(user_id=1, db=seeded_db_session, days=7)
    assert summary["overall_impressions"] == 5000
    assert summary["overall_engagement"] == 400
    assert len(summary["platforms"]) >= 1


# ── Test: Missing Fields Handled Gracefully ──────────────────────────────────

async def test_analytics_null_fields_dont_crash(seeded_db_session: AsyncSession):
    """Analytics records with null metric fields don't crash aggregation."""
    record = SocialAnalytics(
        user_id=1, platform="linkedin",
        external_post_id="ext_null_test",
        metric_date=date.today(),
        impressions=None, engagement=None,
        collected_at=datetime.datetime.now(datetime.timezone.utc),
    )
    seeded_db_session.add(record)
    await seeded_db_session.commit()

    summary = await get_analytics_summary_for_agent(user_id=1, db=seeded_db_session, days=7)
    # Should not crash — nulls are treated as 0
    assert summary["overall_impressions"] == 0
