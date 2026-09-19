import pytest
import httpx
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.linkedin_service import LinkedInService
from app.models.integration import IntegrationConnection
from app.core.errors import SocialMediaAPIError
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_publish_post_success():
    db_mock = AsyncMock(spec=AsyncSession)
    
    # Mock existing connection
    connection = IntegrationConnection(
        user_id=1,
        provider="linkedin",
        access_token="valid_token",
        provider_user_id="li_user_123",
        expires_at=datetime.utcnow() + timedelta(days=1)
    )
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_token, \
         patch.object(LinkedInService, "get_connection", new_callable=AsyncMock) as mock_get_conn:
         
        mock_token.return_value = "valid_token"
        mock_get_conn.return_value = connection
         
        post_response = MagicMock()
        post_response.status_code = 201
        post_response.json.return_value = {"id": "urn:li:share:12345"}
        mock_post.return_value = post_response
        
        post_id = await LinkedInService.publish_post(1, "Hello LinkedIn!", db_mock)
        assert post_id == "urn:li:share:12345"
        
        # Verify post payload
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["author"] == "urn:li:person:li_user_123"
        assert kwargs["json"]["specificContent"]["com.linkedin.ugc.ShareContent"]["shareCommentary"]["text"] == "Hello LinkedIn!"

@pytest.mark.asyncio
async def test_publish_post_expired_token():
    db_mock = AsyncMock(spec=AsyncSession)
    
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_token:
        # TokenManager raises SocialMediaAPIError with OAUTH_REAUTH_REQUIRED when token is expired and cannot be refreshed
        mock_token.side_effect = SocialMediaAPIError(
            message="LinkedIn authorization error",
            error_code="OAUTH_REAUTH_REQUIRED",
            retryable=False,
            metadata={"platform": "linkedin"}
        )
        
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await LinkedInService.publish_post(1, "Test", db_mock)
            
        assert exc_info.value.error_code == "OAUTH_REAUTH_REQUIRED"
