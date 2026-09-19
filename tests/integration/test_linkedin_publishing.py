"""
LinkedIn publishing integration tests.
Tests the complete flow: execute_tools → LinkedInService → OAuth → API → DB.
Covers requirement §15.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.linkedin_service import LinkedInService
from app.core.errors import SocialMediaAPIError
from tests.mocks.social_providers import MockHTTPResponse, linkedin_publish_response
from tests.fixtures.factories import create_test_integration

pytestmark = [pytest.mark.asyncio, pytest.mark.integration, pytest.mark.publishing]


async def test_linkedin_publish_success(seeded_db_session: AsyncSession):
    """Full LinkedIn publishing flow: valid token → API call → returns post ID."""
    mock_response = MockHTTPResponse(201, linkedin_publish_response("urn:li:share:test123"))

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="valid_token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        post_id = await LinkedInService.publish_post(
            user_id=1, content="Test LinkedIn post", db=seeded_db_session
        )

    assert post_id == "urn:li:share:test123"


async def test_linkedin_publish_invalid_token(seeded_db_session: AsyncSession):
    """401 from LinkedIn → SocialMediaAPIError with OAUTH_REAUTH_REQUIRED."""
    mock_response = MockHTTPResponse(401, {}, "Unauthorized")

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="bad_token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await LinkedInService.publish_post(
                user_id=1, content="Test", db=seeded_db_session
            )

    assert exc_info.value.error_code == "OAUTH_REAUTH_REQUIRED"
    assert exc_info.value.retryable is False


async def test_linkedin_publish_rate_limit(seeded_db_session: AsyncSession):
    """429 from LinkedIn → retryable SocialMediaAPIError."""
    mock_response = MockHTTPResponse(429, {}, "Rate limited")

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await LinkedInService.publish_post(
                user_id=1, content="Test", db=seeded_db_session
            )

    assert exc_info.value.retryable is True


async def test_linkedin_publish_server_error(seeded_db_session: AsyncSession):
    """500 from LinkedIn → retryable error."""
    mock_response = MockHTTPResponse(500, {}, "Internal Server Error")

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await LinkedInService.publish_post(
                user_id=1, content="Test", db=seeded_db_session
            )

    assert exc_info.value.retryable is True


async def test_linkedin_publish_permission_error(seeded_db_session: AsyncSession):
    """403 from LinkedIn → non-retryable permission error."""
    mock_response = MockHTTPResponse(403, {}, "Forbidden")

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await LinkedInService.publish_post(
                user_id=1, content="Test", db=seeded_db_session
            )

    assert exc_info.value.error_code == "OAUTH_REAUTH_REQUIRED"
    assert exc_info.value.retryable is False


async def test_linkedin_not_connected(seeded_db_session: AsyncSession):
    """No LinkedIn connection → INTEGRATION_NOT_CONNECTED."""
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock,
               side_effect=SocialMediaAPIError(
                   message="Not connected", error_code="INTEGRATION_NOT_CONNECTED",
                   retryable=False
               )):
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await LinkedInService.publish_post(
                user_id=1, content="Test", db=seeded_db_session
            )

    assert exc_info.value.error_code == "INTEGRATION_NOT_CONNECTED"
