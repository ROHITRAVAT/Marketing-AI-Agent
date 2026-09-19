import pytest
import httpx
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.facebook_service import FacebookService
from app.models.integration import IntegrationConnection
from app.core.errors import SocialMediaAPIError
from datetime import datetime, timedelta, timezone

@pytest.mark.asyncio
async def test_publish_post_success():
    db_mock = AsyncMock(spec=AsyncSession)
    
    page_conn = IntegrationConnection(
        user_id=42,
        provider="facebook_page",
        access_token="page_access_token_real",
        provider_user_id="page_001",
        account_name="Marketing Page",
        scopes="selected",
    )
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_token, \
         patch.object(FacebookService, "get_selected_page", new_callable=AsyncMock) as mock_get_page:
         
        mock_token.return_value = "valid_user_token"
        mock_get_page.return_value = page_conn
         
        post_resp = MagicMock()
        post_resp.status_code = 200
        post_resp.json.return_value = {"id": "page_001_12345"}
        mock_post.return_value = post_resp

        post_id = await FacebookService.publish_post(42, "Hello Facebook!", db_mock)
        assert post_id == "page_001_12345"

@pytest.mark.asyncio
async def test_publish_post_expired_token():
    db_mock = AsyncMock(spec=AsyncSession)
    
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_token:
        mock_token.side_effect = SocialMediaAPIError(
            message="Facebook authorization error",
            error_code="OAUTH_REAUTH_REQUIRED",
            retryable=False,
            metadata={"platform": "facebook"}
        )
        
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await FacebookService.publish_post(42, "Test", db_mock)
            
        assert exc_info.value.error_code == "OAUTH_REAUTH_REQUIRED"

@pytest.mark.asyncio
async def test_publish_post_not_connected():
    db_mock = AsyncMock(spec=AsyncSession)
    
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_token, \
         patch.object(FacebookService, "get_selected_page", new_callable=AsyncMock) as mock_get_page:
         
        mock_token.return_value = "valid_user_token"
        mock_get_page.return_value = None
        
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await FacebookService.publish_post(42, "Test", db_mock)
            
        assert exc_info.value.error_code == "FACEBOOK_PAGE_NOT_SELECTED"
