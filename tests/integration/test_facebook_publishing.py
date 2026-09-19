"""
Facebook publishing integration tests.
Tests the complete flow: FacebookService → page selection → Meta Graph API → DB.
Covers requirement §16.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.facebook_service import FacebookService
from app.core.errors import SocialMediaAPIError
from app.core.oauth.encryption import OAuthEncryption
from app.models.integration import IntegrationConnection
from tests.mocks.social_providers import MockHTTPResponse, facebook_publish_response

pytestmark = [pytest.mark.asyncio, pytest.mark.integration, pytest.mark.publishing]


@pytest.fixture(autouse=True)
async def setup_facebook_test(seeded_db_session: AsyncSession):
    """Clear default seeded connections to prevent test pollution."""
    from sqlalchemy import delete
    await seeded_db_session.execute(delete(IntegrationConnection))
    await seeded_db_session.commit()

async def _seed_facebook_page(db: AsyncSession, user_id: int = 1):
    """Seed a selected Facebook page connection for publishing."""
    page = IntegrationConnection(
        user_id=user_id,
        provider="facebook_page",
        access_token=OAuthEncryption.encrypt("mock_page_token"),
        provider_user_id="page_123",
        account_name="Test Page",
        scopes="selected",
    )
    db.add(page)
    await db.commit()
    return page


async def test_facebook_publish_success(seeded_db_session: AsyncSession):
    """Full Facebook publishing flow with valid page token."""
    await _seed_facebook_page(seeded_db_session)
    mock_response = MockHTTPResponse(200, facebook_publish_response("page123_post789"))

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="valid_user_token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        post_id = await FacebookService.publish_post(
            user_id=1, content="Test Facebook post", db=seeded_db_session
        )

    assert post_id == "page123_post789"


async def test_facebook_publish_no_page_selected(seeded_db_session: AsyncSession):
    """No Facebook page selected → FACEBOOK_PAGE_NOT_SELECTED."""
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="valid_token"):
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await FacebookService.publish_post(
                user_id=1, content="Test", db=seeded_db_session
            )

    assert exc_info.value.error_code == "FACEBOOK_PAGE_NOT_SELECTED"


async def test_facebook_publish_auth_error(seeded_db_session: AsyncSession):
    """401 from Facebook → non-retryable auth error."""
    await _seed_facebook_page(seeded_db_session)
    mock_response = MockHTTPResponse(401, {}, "Invalid token")

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="expired_token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await FacebookService.publish_post(
                user_id=1, content="Test", db=seeded_db_session
            )

    assert exc_info.value.error_code == "FACEBOOK_AUTH_ERROR"
    assert exc_info.value.retryable is False


async def test_facebook_publish_rate_limit(seeded_db_session: AsyncSession):
    """429 from Facebook → retryable."""
    await _seed_facebook_page(seeded_db_session)
    mock_response = MockHTTPResponse(429, {}, "Rate limited")

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await FacebookService.publish_post(
                user_id=1, content="Test", db=seeded_db_session
            )

    assert exc_info.value.retryable is True


async def test_facebook_publish_server_error(seeded_db_session: AsyncSession):
    """500 from Facebook → retryable."""
    await _seed_facebook_page(seeded_db_session)
    mock_response = MockHTTPResponse(500, {}, "Server error")

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await FacebookService.publish_post(
                user_id=1, content="Test", db=seeded_db_session
            )

    assert exc_info.value.retryable is True
