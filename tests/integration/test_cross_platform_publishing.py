"""
Cross-platform publishing integration tests.
Verifies: multi-platform campaigns, one failure doesn't cascade,
          independent external IDs and status tracking.
Covers requirements §19, §41.
"""
import pytest
import uuid
import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from unittest.mock import patch, MagicMock, AsyncMock

from app.models.scheduled_post import ScheduledPost
from tests.fixtures.factories import create_test_scheduled_post, create_published_post

pytestmark = [pytest.mark.asyncio, pytest.mark.integration, pytest.mark.publishing]


async def test_multi_platform_independent_status(seeded_db_session: AsyncSession):
    """Each platform's post has its own status — LinkedIn published, Facebook failed."""
    now = datetime.datetime.now(datetime.timezone.utc)

    linkedin_post = create_test_scheduled_post(
        user_id=1, platform="linkedin", status="published",
        external_post_id="li_post_123", published_at=now,
    )
    facebook_post = create_test_scheduled_post(
        user_id=1, platform="facebook", status="failed",
    )
    facebook_post.error_message = "Facebook API returned 500"

    seeded_db_session.add_all([linkedin_post, facebook_post])
    await seeded_db_session.commit()

    # Verify they are independent in the DB
    posts = (await seeded_db_session.execute(select(ScheduledPost))).scalars().all()
    statuses = {p.platform: p.status for p in posts}

    assert statuses["linkedin"] == "published"
    assert statuses["facebook"] == "failed"


async def test_independent_external_ids(seeded_db_session: AsyncSession):
    """Each platform stores its own unique external_post_id."""
    platforms = ["linkedin", "facebook", "instagram", "twitter"]
    posts = []
    for plat in platforms:
        p = create_published_post(user_id=1, platform=plat)
        posts.append(p)

    seeded_db_session.add_all(posts)
    await seeded_db_session.commit()

    result = (await seeded_db_session.execute(select(ScheduledPost))).scalars().all()
    ext_ids = [p.external_post_id for p in result if p.external_post_id]

    # All external IDs should be unique
    assert len(set(ext_ids)) == len(ext_ids) == 4


async def test_one_failure_doesnt_cascade(
    integration_client: AsyncClient,
    seeded_db_session: AsyncSession,
    mock_social_platforms,
):
    """
    When one platform (Facebook) fails and another (LinkedIn) succeeds during
    scheduler processing, the LinkedIn post should still be published.
    """
    from app.scheduler.worker import poll_and_process_jobs
    from app.models.integration import IntegrationConnection

    now = datetime.datetime.now(datetime.timezone.utc)
    past = now - datetime.timedelta(minutes=10)

    # Seed Facebook connections (LinkedIn is already seeded by conftest)
    conn_fb = IntegrationConnection(
        user_id=1, provider="facebook", access_token="token",
        provider_user_id="uid_facebook"
    )
    conn_fb_page = IntegrationConnection(
        user_id=1, provider="facebook_page", access_token="token",
        provider_user_id="fb_page_id", scopes="selected"
    )
    seeded_db_session.add_all([conn_fb, conn_fb_page])

    linkedin_post = create_test_scheduled_post(
        user_id=1, platform="linkedin", status="scheduled",
        scheduled_time=past, content="LinkedIn OK"
    )
    facebook_post = create_test_scheduled_post(
        user_id=1, platform="facebook", status="scheduled",
        scheduled_time=past, content="Facebook FAIL"
    )
    facebook_post.attempt_count = 3  # Force it to fail permanently
    seeded_db_session.add_all([linkedin_post, facebook_post])
    await seeded_db_session.commit()
    await seeded_db_session.refresh(linkedin_post)
    await seeded_db_session.refresh(facebook_post)

    # Mock: LinkedIn succeeds, Facebook raises
    def mock_post_side_effect(url, *args, **kwargs):
        if "facebook" in url or "graph.facebook" in url:
            raise Exception("Facebook API is down!")
        # LinkedIn mock
        mock = MagicMock()
        mock.status_code = 201
        mock.json.return_value = {"id": "li_ext_123"}
        return mock

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="mock_token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, side_effect=mock_post_side_effect):
        await poll_and_process_jobs()

    await seeded_db_session.commit()
    await seeded_db_session.refresh(linkedin_post)
    await seeded_db_session.refresh(facebook_post)

    assert linkedin_post.status == "published"
    assert facebook_post.status == "failed"
    assert linkedin_post.external_post_id is not None
    assert facebook_post.external_post_id is None
