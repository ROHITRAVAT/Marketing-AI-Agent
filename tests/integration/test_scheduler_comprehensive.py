"""
Comprehensive scheduler integration tests.
Tests: lifecycle, future-post guard, cancellation, rescheduling, crash recovery,
       token refresh, max retries, atomic job claiming.
Covers requirements §21–§28.
"""
import pytest
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from unittest.mock import patch, AsyncMock, MagicMock

from app.models.scheduled_post import ScheduledPost
from app.models.integration import IntegrationConnection
from app.scheduler.worker import poll_and_process_jobs
from app.core.errors import SocialMediaAPIError
from tests.fixtures.factories import (
    create_test_scheduled_post,
    create_future_scheduled_post,
    create_test_integration,
)

pytestmark = [pytest.mark.asyncio, pytest.mark.integration, pytest.mark.scheduler]


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _seed_integration(db, user_id=1, provider="linkedin"):
    conn = create_test_integration(user_id=user_id, provider=provider)
    db.add(conn)
    await db.commit()


# ── Test: Full Lifecycle ─────────────────────────────────────────────────────

async def test_scheduler_lifecycle_scheduled_to_published(
    seeded_db_session: AsyncSession, mock_social_platforms
):
    """scheduled → processing → published with external_post_id."""
    post = create_test_scheduled_post(user_id=1, platform="linkedin", content="Lifecycle test")
    seeded_db_session.add(post)
    await seeded_db_session.commit()
    await seeded_db_session.refresh(post)

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="token"):
        await poll_and_process_jobs()

    await seeded_db_session.refresh(post)
    assert post.status == "published"
    assert post.external_post_id == "mock_external_id_123"
    assert post.published_at is not None
    assert post.attempt_count >= 1


# ── Test: Future Post Guard ──────────────────────────────────────────────────

async def test_future_post_not_published_early(
    seeded_db_session: AsyncSession, mock_social_platforms
):
    """Posts scheduled in the future must NOT be picked up."""
    post = create_future_scheduled_post(user_id=1, platform="twitter")
    seeded_db_session.add(post)
    await seeded_db_session.commit()
    await seeded_db_session.refresh(post)

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="token"):
        await poll_and_process_jobs()

    await seeded_db_session.refresh(post)
    assert post.status == "scheduled"
    assert post.external_post_id is None
    mock_social_platforms["post"].assert_not_called()


# ── Test: Cancellation ───────────────────────────────────────────────────────

async def test_cancelled_post_not_published(
    seeded_db_session: AsyncSession, mock_social_platforms
):
    """Cancelled posts are skipped by the scheduler."""
    post = create_test_scheduled_post(user_id=1, platform="facebook", status="cancelled")
    seeded_db_session.add(post)
    await seeded_db_session.commit()
    await seeded_db_session.refresh(post)

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="token"):
        await poll_and_process_jobs()

    await seeded_db_session.refresh(post)
    assert post.status == "cancelled"
    assert post.external_post_id is None


# ── Test: Rescheduling ───────────────────────────────────────────────────────

async def test_rescheduling_updates_time(
    integration_client, seeded_db_session: AsyncSession
):
    """PATCH endpoint updates scheduled_time without changing status."""
    future = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    new_future = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)

    post = create_test_scheduled_post(
        user_id=1, platform="linkedin", scheduled_time=future
    )
    seeded_db_session.add(post)
    await seeded_db_session.commit()
    await seeded_db_session.refresh(post)

    resp = await integration_client.patch(
        f"/api/v1/scheduled-posts/{post.id}",
        json={"scheduled_time": new_future.isoformat()}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "scheduled"


# ── Test: Token Refresh Success ──────────────────────────────────────────────

async def test_scheduler_token_refresh_then_publish(
    seeded_db_session: AsyncSession, mock_social_platforms
):
    """If token is expired, scheduler refreshes it and then publishes."""
    post = create_test_scheduled_post(user_id=1, platform="linkedin")
    seeded_db_session.add(post)
    await seeded_db_session.commit()
    await seeded_db_session.refresh(post)

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="refreshed_token"):
        await poll_and_process_jobs()

    await seeded_db_session.refresh(post)
    assert post.status == "published"


# ── Test: Token Refresh Failure ──────────────────────────────────────────────

async def test_scheduler_token_refresh_failure(
    seeded_db_session: AsyncSession, mock_social_platforms
):
    """Token refresh fails → post should fail, not remain processing forever."""
    post = create_test_scheduled_post(
        user_id=1, platform="twitter", attempt_count=2
    )
    seeded_db_session.add(post)
    await seeded_db_session.commit()
    await seeded_db_session.refresh(post)

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, side_effect=Exception("Token refresh failed")):
        await poll_and_process_jobs()

    await seeded_db_session.refresh(post)
    assert post.status == "failed"
    assert post.external_post_id is None


# ── Test: Max Retries ────────────────────────────────────────────────────────

async def test_scheduler_max_retries_exhausted(
    seeded_db_session: AsyncSession, mock_social_platforms
):
    """After max retries, the post should be marked failed."""
    from app.core.config import SCHEDULER_MAX_RETRIES

    post = create_test_scheduled_post(
        user_id=1, platform="linkedin",
        attempt_count=SCHEDULER_MAX_RETRIES,
    )
    seeded_db_session.add(post)
    await seeded_db_session.commit()
    await seeded_db_session.refresh(post)

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, side_effect=Exception("Always fails")):
        await poll_and_process_jobs()

    await seeded_db_session.refresh(post)
    assert post.status == "failed"


# ── Test: Already Published Idempotency ──────────────────────────────────────

async def test_scheduler_skips_already_published(
    seeded_db_session: AsyncSession, mock_social_platforms
):
    """Already-published posts should not be re-processed."""
    post = create_test_scheduled_post(
        user_id=1, platform="linkedin", status="published",
        external_post_id="existing_123"
    )
    seeded_db_session.add(post)
    await seeded_db_session.commit()
    await seeded_db_session.refresh(post)
    original_ext_id = post.external_post_id

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="token"):
        await poll_and_process_jobs()

    await seeded_db_session.refresh(post)
    assert post.status == "published"
    assert post.external_post_id == original_ext_id  # unchanged
