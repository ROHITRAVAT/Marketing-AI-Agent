import httpx
from typing import Dict, Any, Optional
from app.services.analytics.provider import AnalyticsProvider
from app.core.errors import SocialMediaAPIError
import logging

logger = logging.getLogger(__name__)

class InstagramAnalyticsProvider(AnalyticsProvider):
    API_BASE = "https://graph.facebook.com/v19.0"

    async def get_post_metrics(
        self,
        post_id: str,
        access_token: str,
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch engagement metrics for an Instagram media object."""
        async with httpx.AsyncClient() as client:
            # We first need to check the media_type because supported metrics vary
            media_info_url = f"{self.API_BASE}/{post_id}"
            media_info = await client.get(
                media_info_url,
                params={"fields": "media_type,comments_count,like_count", "access_token": access_token}
            )
            
            if media_info.status_code == 429:
                raise SocialMediaAPIError(
                    message="Instagram API rate limit exceeded.",
                    error_code="INSTAGRAM_RATE_LIMIT",
                    retryable=True,
                    metadata={"platform": "instagram"}
                )
                
            if media_info.status_code != 200:
                logger.error(f"Instagram media info fetch failed: {media_info.text}")
                if media_info.status_code in (401, 403):
                    raise SocialMediaAPIError(
                        message=f"Instagram authorization error: {media_info.text}",
                        error_code="OAUTH_REAUTH_REQUIRED",
                        retryable=False,
                        metadata={"platform": "instagram"}
                    )
                raise SocialMediaAPIError(
                    message="Failed to fetch Instagram media info.",
                    error_code="INSTAGRAM_ANALYTICS_FAILED",
                    retryable=True,
                    metadata={"platform": "instagram"}
                )

            media_data = media_info.json()
            media_type = media_data.get("media_type")
            likes = media_data.get("like_count", 0)
            comments = media_data.get("comments_count", 0)
            
            # Instagram metrics depend on the media type
            if media_type == "REELS":
                metrics = "plays,ig_reels_avg_watch_time,ig_reels_video_view_total_time,reach,saved,shares"
            elif media_type == "CAROUSEL_ALBUM":
                metrics = "carousel_album_engagement,carousel_album_impressions,carousel_album_reach,saved,video_views"
            else:
                # IMAGE or VIDEO (non-reels)
                metrics = "engagement,impressions,reach,saved,video_views"

            url = f"{self.API_BASE}/{post_id}/insights"
            response = await client.get(
                url,
                params={"metric": metrics, "access_token": access_token}
            )

            # Sometimes Insights fail if the media is too old, or metrics don't apply.
            # We'll just fall back to the basic info we already have if it fails, instead of blowing up.
            reach = 0
            impressions = 0
            engagement = likes + comments
            shares = 0
            saves = 0
            video_views = 0
            provider_data = media_data
            
            if response.status_code == 200:
                insight_data = response.json()
                provider_data["insights"] = insight_data
                insights_array = insight_data.get("data", [])
                
                for m in insights_array:
                    name = m.get("name")
                    values = m.get("values", [])
                    val = values[0].get("value", 0) if values else 0
                    
                    if name in ["reach", "carousel_album_reach"]:
                        reach = val
                    elif name in ["impressions", "carousel_album_impressions"]:
                        impressions = val
                    elif name in ["engagement", "carousel_album_engagement"]:
                        engagement = val
                    elif name == "saved":
                        saves = val
                    elif name == "shares":
                        shares = val
                    elif name in ["video_views", "plays"]:
                        video_views = val
            
            return {
                "impressions": impressions,
                "reach": reach,
                "engagement": engagement,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "saves": saves,
                "video_views": video_views,
                "provider_metrics": provider_data
            }

    async def get_account_metrics(
        self,
        account_id: str,
        access_token: str
    ) -> Dict[str, Any]:
        """Fetch account metrics for an Instagram Business Account."""
        async with httpx.AsyncClient() as client:
            url = f"{self.API_BASE}/{account_id}"
            response = await client.get(
                url,
                params={"fields": "followers_count", "access_token": access_token}
            )
            
            if response.status_code != 200:
                logger.error(f"Instagram account analytics fetch failed: {response.text}")
                if response.status_code in (401, 403):
                    raise SocialMediaAPIError(
                        message=f"Instagram authorization error: {response.text}",
                        error_code="OAUTH_REAUTH_REQUIRED",
                        retryable=False,
                        metadata={"platform": "instagram"}
                    )
                raise SocialMediaAPIError(
                    message="Failed to fetch Instagram account analytics.",
                    error_code="INSTAGRAM_ANALYTICS_FAILED",
                    retryable=True,
                    metadata={"platform": "instagram"}
                )

            data = response.json()
            followers = data.get("followers_count", 0)
            
            return {
                "followers": followers,
                "provider_metrics": data
            }
