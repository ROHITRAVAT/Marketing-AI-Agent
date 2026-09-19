import pytest
import httpx
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.instagram_service import InstagramService
from app.models.integration import IntegrationConnection
from app.core.errors import SocialMediaAPIError
from datetime import datetime, timedelta, timezone

@pytest.mark.asyncio
async def test_publish_post_success():
    db_mock = AsyncMock(spec=AsyncSession)
    
    page_conn = IntegrationConnection(
        user_id=42,
        provider="instagram",
        access_token="ig_access_token_real",
        provider_user_id="ig_123",
        account_name="Marketing IG",
        scopes="selected",
    )
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get, \
         patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_token, \
         patch.object(InstagramService, "get_selected_account", new_callable=AsyncMock) as mock_get_account:
         
        mock_token.return_value = "valid_user_token"
        mock_get_account.return_value = page_conn
         
        # Mock container creation
        create_resp = MagicMock()
        create_resp.status_code = 200
        create_resp.json.return_value = {"id": "container_123"}
        
        # Mock container status check
        status_resp = MagicMock()
        status_resp.status_code = 200
        status_resp.json.return_value = {"status_code": "FINISHED"}
        
        # Mock publish
        publish_resp = MagicMock()
        publish_resp.status_code = 200
        publish_resp.json.return_value = {"id": "post_123"}
        
        mock_post.side_effect = [create_resp, publish_resp]
        mock_get.return_value = status_resp

        post_id = await InstagramService.publish_post(42, "http://example.com/image.jpg", "Hello IG!", db_mock)
        assert post_id == "post_123"

@pytest.mark.asyncio
async def test_publish_post_expired_token():
    db_mock = AsyncMock(spec=AsyncSession)
    
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_token:
        mock_token.side_effect = SocialMediaAPIError(
            message="IG authorization error",
            error_code="OAUTH_REAUTH_REQUIRED",
            retryable=False,
            metadata={"platform": "instagram"}
        )
        
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await InstagramService.publish_post(42, "http://example.com/image.jpg", "Test", db_mock)
            
        assert exc_info.value.error_code == "OAUTH_REAUTH_REQUIRED"
