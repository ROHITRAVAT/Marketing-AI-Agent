import httpx
from typing import Dict, Any, Optional
from app.services.analytics.provider import AnalyticsProvider
from app.core.errors import SocialMediaAPIError
import logging

logger = logging.getLogger(__name__)

class TwitterAnalyticsProvider(AnalyticsProvider):
    API_BASE = "https://api.twitter.com/2"

    async def get_post_metrics(
        self,
        post_id: str,
        access_token: str,
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch engagement metrics for a specific tweet."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/tweets/{post_id}",
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
                    retryable=True,
                    metadata={"platform": "twitter"}
                )

            data = response.json()
            tweet = data.get("data", {})
            metrics = tweet.get("public_metrics", {})
            
            # Map Twitter public_metrics to normalized fields
            likes = metrics.get("like_count", 0)
            comments = metrics.get("reply_count", 0)
            shares = metrics.get("retweet_count", 0) + metrics.get("quote_count", 0)
            saves = metrics.get("bookmark_count", 0)
            impressions = metrics.get("impression_count", 0)
            
            return {
                "impressions": impressions,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "saves": saves,
                "engagement": likes + comments + shares + saves,
                "provider_metrics": metrics
            }

    async def get_account_metrics(
        self,
        account_id: str,
        access_token: str
    ) -> Dict[str, Any]:
        """Fetch account metrics for Twitter."""
        # Using /users/{id} to get public_metrics for the account
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/users/{account_id}",
                params={"user.fields": "public_metrics"},
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Twitter account analytics fetch failed: {response.text}")
                if response.status_code in (401, 403):
                    raise SocialMediaAPIError(
                        message=f"Twitter authorization error: {response.text}",
                        error_code="OAUTH_REAUTH_REQUIRED",
                        retryable=False,
                        metadata={"platform": "twitter"}
                    )
                raise SocialMediaAPIError(
                    message="Failed to fetch Twitter account analytics.",
                    error_code="TWITTER_ANALYTICS_FAILED",
                    retryable=True,
                    metadata={"platform": "twitter"}
                )

            data = response.json()
            user_data = data.get("data", {})
            metrics = user_data.get("public_metrics", {})
            
            followers = metrics.get("followers_count", 0)
            
            return {
                "followers": followers,
                "provider_metrics": metrics
            }
