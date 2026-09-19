"""
Error handling integration tests.
Tests: API error propagation, timeouts, rate limits (429), server (5xx), client (4xx).
Covers requirements §42–§46.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.linkedin_service import LinkedInService
from app.core.errors import SocialMediaAPIError, ErrorCategory
from tests.mocks.social_providers import MockHTTPResponse

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


async def test_timeout_handling(seeded_db_session: AsyncSession):
    """Simulated timeout is wrapped in a retryable error."""
    import httpx
    
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock, return_value="token"), \
         patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Read timeout")):
        
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await LinkedInService.publish_post(user_id=1, content="Test", db=seeded_db_session)
            
    assert exc_info.value.retryable is True
    assert exc_info.value.error_code == "LINKEDIN_ANALYTICS_FAILED" or exc_info.value.category == ErrorCategory.API_ERROR


async def test_rate_limit_429_handling(seeded_db_session: AsyncSession):
    """429 Too Many Requests is correctly identified as retryable."""
    mock_resp = MockHTTPResponse(429, {}, "Too many requests")
    
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock, return_value="token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await LinkedInService.publish_post(user_id=1, content="Test", db=seeded_db_session)
            
    assert exc_info.value.retryable is True


async def test_server_5xx_retry(seeded_db_session: AsyncSession):
    """500 Internal Server Error from provider is retryable."""
    mock_resp = MockHTTPResponse(502, {}, "Bad Gateway")
    
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock, return_value="token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await LinkedInService.publish_post(user_id=1, content="Test", db=seeded_db_session)
            
    assert exc_info.value.retryable is True


async def test_client_4xx_no_retry(seeded_db_session: AsyncSession):
    """400 Bad Request is NOT retryable (unless it's a specific auth case we handle)."""
    mock_resp = MockHTTPResponse(400, {}, "Invalid input")
    
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock, return_value="token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await LinkedInService.publish_post(user_id=1, content="Test", db=seeded_db_session)
            
    assert exc_info.value.retryable is False


async def test_error_propagation_to_frontend(integration_client: AsyncClient, seeded_db_session: AsyncSession):
    """Ensure internal exceptions during API requests return clean, safe JSON to the frontend."""
    # We'll mock the campaign listing to throw an unhandled exception
    with patch("app.api.v1.endpoints.campaigns.CampaignService.get_campaigns", side_effect=ValueError("Deep internal failure")):
        resp = await integration_client.get("/api/v1/campaigns/")
        
    # FastAPI default exception handler returns 500 for unhandled exceptions
    assert resp.status_code == 500
    data = resp.json()
    error_msg = data.get("message") or data.get("detail") or ""
    assert "Deep internal failure" not in error_msg  # Assuming we don't leak ValueErrors to client
    assert "Internal server error" in error_msg.lower() or "internal server error" in str(data).lower()
