import pytest
import httpx
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.twitter_service import TwitterService
from app.models.integration import IntegrationConnection
from app.core.errors import SocialMediaAPIError
from datetime import datetime, timedelta, timezone

@pytest.mark.asyncio
async def test_publish_post_success():
    db_mock = AsyncMock(spec=AsyncSession)
    
    conn = IntegrationConnection(
        user_id=42,
        provider="twitter",
        access_token="tw_access_token_real",
        provider_user_id="tw_123",
        account_name="Marketing Twitter",
    )
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_token, \
         patch.object(TwitterService, "get_connection", new_callable=AsyncMock) as mock_get_conn:
         
        mock_token.return_value = "tw_access_token_real"
        mock_get_conn.return_value = conn
         
        post_resp = MagicMock()
        post_resp.status_code = 201
        post_resp.json.return_value = {"data": {"id": "tweet_12345"}}
        mock_post.return_value = post_resp

        post_id = await TwitterService.publish_post(42, "Hello Twitter!", db_mock)
        assert post_id == "tweet_12345"

@pytest.mark.asyncio
async def test_publish_post_expired_token():
    db_mock = AsyncMock(spec=AsyncSession)
    
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_token:
        mock_token.side_effect = SocialMediaAPIError(
            message="Twitter authorization error",
            error_code="OAUTH_REAUTH_REQUIRED",
            retryable=False,
            metadata={"platform": "twitter"}
        )
        
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await TwitterService.publish_post(42, "Test", db_mock)
            
        assert exc_info.value.error_code == "OAUTH_REAUTH_REQUIRED"
        
@pytest.mark.asyncio
async def test_get_analytics_success():
    db_mock = AsyncMock(spec=AsyncSession)
    
    conn = IntegrationConnection(
        user_id=42,
        provider="twitter",
        access_token="tw_access_token_real",
        provider_user_id="tw_123",
        account_name="Marketing Twitter",
    )
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get, \
         patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_token, \
         patch.object(TwitterService, "get_connection", new_callable=AsyncMock) as mock_get_conn:
         
        mock_token.return_value = "tw_access_token_real"
        mock_get_conn.return_value = conn
        
        analytics_resp = MagicMock()
        analytics_resp.status_code = 200
        analytics_resp.json.return_value = {
            "data": {
                "id": "tweet_12345",
                "public_metrics": {
                    "like_count": 10,
                    "retweet_count": 5,
                    "reply_count": 2,
                    "quote_count": 1,
                    "bookmark_count": 3,
                    "impression_count": 1000
                }
            }
        }
        mock_get.return_value = analytics_resp
        
        metrics = await TwitterService.get_analytics(42, "tweet_12345", db_mock)
        assert metrics["likes"] == 10
        assert metrics["reposts"] == 5
