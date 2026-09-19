"""
X/Twitter publishing integration tests.
Tests: tweet creation, OAuth errors, rate limiting.
Covers requirement §18.
"""
import pytest
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.twitter_service import TwitterService
from app.core.errors import SocialMediaAPIError
from tests.mocks.social_providers import MockHTTPResponse, twitter_publish_response

pytestmark = [pytest.mark.asyncio, pytest.mark.integration, pytest.mark.publishing]


async def test_twitter_publish_success(seeded_db_session: AsyncSession):
    """Successful tweet creation returns tweet ID."""
    mock_response = MockHTTPResponse(201, twitter_publish_response("tweet_abc123"))

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="valid_token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        tweet_id = await TwitterService.publish_post(
            user_id=1, content="Test tweet content", db=seeded_db_session
        )

    assert tweet_id == "tweet_abc123"


async def test_twitter_publish_oauth_failure(seeded_db_session: AsyncSession):
    """401 from Twitter → OAUTH_REAUTH_REQUIRED."""
    mock_response = MockHTTPResponse(401, {}, "Unauthorized")

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="bad_token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await TwitterService.publish_post(
                user_id=1, content="Test", db=seeded_db_session
            )

    assert exc_info.value.error_code == "OAUTH_REAUTH_REQUIRED"
    assert exc_info.value.retryable is False


async def test_twitter_rate_limit(seeded_db_session: AsyncSession):
    """429 → TWITTER_RATE_LIMIT, retryable."""
    mock_response = MockHTTPResponse(429, {}, "Rate limited")

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await TwitterService.publish_post(
                user_id=1, content="Test", db=seeded_db_session
            )

    assert exc_info.value.error_code == "TWITTER_RATE_LIMIT"
    assert exc_info.value.retryable is True


async def test_twitter_api_failure(seeded_db_session: AsyncSession):
    """400 from Twitter → non-retryable."""
    mock_response = MockHTTPResponse(400, {}, "Invalid request")

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await TwitterService.publish_post(
                user_id=1, content="Test", db=seeded_db_session
            )

    assert exc_info.value.retryable is False


async def test_twitter_not_connected(seeded_db_session: AsyncSession):
    """No Twitter connection → INTEGRATION_NOT_CONNECTED."""
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock,
               side_effect=SocialMediaAPIError(
                   message="Not connected", error_code="INTEGRATION_NOT_CONNECTED",
                   retryable=False
               )):
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await TwitterService.publish_post(
                user_id=1, content="Test", db=seeded_db_session
            )

    assert exc_info.value.error_code == "INTEGRATION_NOT_CONNECTED"
