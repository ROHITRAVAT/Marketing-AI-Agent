import httpx
from typing import Dict, Any, Optional
from app.services.analytics.provider import AnalyticsProvider
from app.core.errors import SocialMediaAPIError
import logging

logger = logging.getLogger(__name__)

class FacebookAnalyticsProvider(AnalyticsProvider):
    API_BASE = "https://graph.facebook.com/v19.0"

    async def get_post_metrics(
        self,
        post_id: str,
        access_token: str,
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch engagement metrics for a specific Facebook Page post."""
        async with httpx.AsyncClient() as client:
            # For a post, we query insights for post_impressions, post_engagements
            metrics_to_fetch = "post_impressions_unique,post_engaged_users,post_reactions_by_type_total"
            url = f"{self.API_BASE}/{post_id}/insights"
            
            response = await client.get(
                url,
                params={"metric": metrics_to_fetch, "access_token": access_token}
            )
            
            if response.status_code == 429:
                raise SocialMediaAPIError(
                    message="Facebook API rate limit exceeded.",
                    error_code="FACEBOOK_RATE_LIMIT",
                    retryable=True,
                    metadata={"platform": "facebook"}
                )
                
            if response.status_code != 200:
                logger.error(f"Facebook post analytics fetch failed: {response.text}")
                if response.status_code in (401, 403):
                    raise SocialMediaAPIError(
                        message=f"Facebook authorization error: {response.text}",
                        error_code="OAUTH_REAUTH_REQUIRED",
                        retryable=False,
                        metadata={"platform": "facebook"}
                    )
                raise SocialMediaAPIError(
                    message="Failed to fetch Facebook post analytics.",
                    error_code="FACEBOOK_ANALYTICS_FAILED",
                    retryable=True,
                    metadata={"platform": "facebook"}
                )

            data = response.json()
            metrics_data = data.get("data", [])
            
            reach = 0
            engagement = 0
            likes = 0
            
            for m in metrics_data:
                name = m.get("name")
                values = m.get("values", [])
                val = values[0].get("value", 0) if values else 0
                
                if name == "post_impressions_unique":
                    reach = val
                elif name == "post_engaged_users":
                    engagement = val
                elif name == "post_reactions_by_type_total":
                    # For reactions, value is a dict like {"like": 10, "love": 2}
                    if isinstance(val, dict):
                        likes = sum(val.values())
                        
            # Also fetch comments and shares directly from the post object
            post_url = f"{self.API_BASE}/{post_id}"
            post_response = await client.get(
                post_url,
                params={"fields": "comments.summary(true),shares", "access_token": access_token}
            )
            
            comments = 0
            shares = 0
            if post_response.status_code == 200:
                p_data = post_response.json()
                comments = p_data.get("comments", {}).get("summary", {}).get("total_count", 0)
                shares = p_data.get("shares", {}).get("count", 0)

            return {
                "reach": reach,
                "engagement": engagement,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "provider_metrics": data
            }

    async def get_account_metrics(
        self,
        account_id: str,
        access_token: str
    ) -> Dict[str, Any]:
        """Fetch account metrics for a Facebook Page."""
        async with httpx.AsyncClient() as client:
            url = f"{self.API_BASE}/{account_id}"
            response = await client.get(
                url,
                params={"fields": "followers_count", "access_token": access_token}
            )
            
            if response.status_code != 200:
                logger.error(f"Facebook account analytics fetch failed: {response.text}")
                if response.status_code in (401, 403):
                    raise SocialMediaAPIError(
                        message=f"Facebook authorization error: {response.text}",
                        error_code="OAUTH_REAUTH_REQUIRED",
                        retryable=False,
                        metadata={"platform": "facebook"}
                    )
                raise SocialMediaAPIError(
                    message="Failed to fetch Facebook account analytics.",
                    error_code="FACEBOOK_ANALYTICS_FAILED",
                    retryable=True,
                    metadata={"platform": "facebook"}
                )

            data = response.json()
            followers = data.get("followers_count", 0)
            
            return {
                "followers": followers,
                "provider_metrics": data
            }
