import httpx
import logging
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.integration import IntegrationConnection
from app.core.errors import SocialMediaAPIError
from app.core.oauth.manager import TokenManager

logger = logging.getLogger(__name__)

class TwitterService:
    API_BASE = "https://api.twitter.com/2"

    @classmethod
    async def get_connection(cls, user_id: int, db: AsyncSession) -> Optional[IntegrationConnection]:
        """Retrieve the Twitter connection metadata for the user."""
        return await TokenManager.get_connection_status(user_id, "twitter", db)

    @classmethod
    async def publish_post(cls, user_id: int, content: str, db: AsyncSession) -> str:
        """Publish a tweet."""
        # Retrieves and auto-refreshes token via TokenManager
        access_token = await TokenManager.get_valid_access_token(user_id, "twitter", db)
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{cls.API_BASE}/tweets",
                json={"text": content},
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 429:
                raise SocialMediaAPIError(
                    message="Twitter API rate limit exceeded.",
                    error_code="TWITTER_RATE_LIMIT",
                    retryable=True,
                    user_message="Twitter rate limit exceeded. Please try again later.",
                    metadata={"platform": "twitter"}
                )
                
            if response.status_code not in (200, 201):
                logger.error(f"Twitter publish failed: {response.text}")
                if response.status_code in (401, 403):
                    raise SocialMediaAPIError(
                        message=f"Twitter authorization error: {response.text}",
                        error_code="OAUTH_REAUTH_REQUIRED",
                        retryable=False,
                        user_message="Twitter authorization failed. Please reconnect your account.",
                        metadata={"platform": "twitter"}
                    )
                raise SocialMediaAPIError(
                    message="Failed to publish to Twitter.",
                    error_code="TWITTER_PUBLISH_FAILED",
                    retryable=False,
                    user_message=f"X rejected this post. Please review the content. ({response.status_code})",
                    metadata={"platform": "twitter"}
                )
                
            data = response.json().get("data", {})
            return data.get("id")

    @classmethod
    async def get_analytics(cls, user_id: int, post_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Fetch engagement metrics for a specific tweet."""
        access_token = await TokenManager.get_valid_access_token(user_id, "twitter", db)
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{cls.API_BASE}/tweets/{post_id}",
                params={"tweet.fields": "public_metrics"},
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code == 429:
                raise SocialMediaAPIError(
                    message="Twitter API rate limit exceeded.",
                    error_code="TWITTER_RATE_LIMIT",
                    retryable=True,
                    metadata={"platform": "twitter"}
                )
                
            if response.status_code != 200:
                logger.error(f"Twitter analytics fetch failed: {response.text}")
                if response.status_code in (401, 403):
                    raise SocialMediaAPIError(
                        message=f"Twitter authorization error: {response.text}",
                        error_code="OAUTH_REAUTH_REQUIRED",
                        retryable=False,
                        user_message="Twitter authorization failed. Please reconnect your account.",
                        metadata={"platform": "twitter"}
                    )
                raise SocialMediaAPIError(
                    message="Failed to fetch Twitter analytics.",
                    error_code="TWITTER_ANALYTICS_FAILED",
                    retryable=False,
                    metadata={"platform": "twitter"}
                )
                
            data = response.json().get("data", {})
            metrics = data.get("public_metrics", {})
            
            return {
                "post_id": post_id,
                "likes": metrics.get("like_count", 0),
                "reposts": metrics.get("retweet_count", 0),
                "replies": metrics.get("reply_count", 0),
                "quotes": metrics.get("quote_count", 0),
                "bookmarks": metrics.get("bookmark_count", 0),
                "impressions": metrics.get("impression_count", 0),
            }
