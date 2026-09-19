import httpx
from typing import Dict, Any, Optional
from urllib.parse import quote
from app.services.analytics.provider import AnalyticsProvider
from app.core.errors import SocialMediaAPIError
import logging

logger = logging.getLogger(__name__)

class LinkedInAnalyticsProvider(AnalyticsProvider):
    API_BASE = "https://api.linkedin.com/v2"

    async def get_post_metrics(
        self,
        post_id: str,
        access_token: str,
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch engagement metrics for a specific LinkedIn post.
        Requires the exact URN of the organization/person to query share statistics.
        """
        if not account_id:
            logger.warning(f"LinkedIn get_post_metrics requires an account_id (URN) to query statistics. Post: {post_id}")
            return {}

        async with httpx.AsyncClient() as client:
            # Query the organizationalEntityShareStatistics endpoint
            # We filter by organizationalEntity and share (the post_id)
            # URL encode the URNs
            org_urn = quote(account_id)
            share_urn = quote(post_id)
            
            url = f"{self.API_BASE}/organizationalEntityShareStatistics?q=organizationalEntity&organizationalEntity={org_urn}&shares[0]={share_urn}"
            
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {access_token}", "X-Restli-Protocol-Version": "2.0.0"}
            )
            
            if response.status_code == 429:
                raise SocialMediaAPIError(
                    message="LinkedIn API rate limit exceeded.",
                    error_code="LINKEDIN_RATE_LIMIT",
                    retryable=True,
                    metadata={"platform": "linkedin"}
                )
                
            if response.status_code != 200:
                logger.error(f"LinkedIn analytics fetch failed: {response.text}")
                if response.status_code in (401, 403):
                    # LinkedIn often returns 403 when the token lacks the correct scope for analytics (e.g., rw_organization_admin or r_organization_social)
                    raise SocialMediaAPIError(
                        message=f"LinkedIn authorization/permission error: {response.text}",
                        error_code="OAUTH_REAUTH_REQUIRED",
                        retryable=False,
                        metadata={"platform": "linkedin"}
                    )
                raise SocialMediaAPIError(
                    message="Failed to fetch LinkedIn analytics.",
                    error_code="LINKEDIN_ANALYTICS_FAILED",
                    retryable=True,
                    metadata={"platform": "linkedin"}
                )

            data = response.json()
            elements = data.get("elements", [])
            
            if not elements:
                return {
                    "impressions": 0,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "clicks": 0,
                    "engagement": 0,
                    "provider_metrics": {}
                }
                
            # LinkedIn returns totalShareStatistics
            metrics = elements[0].get("totalShareStatistics", {})
            
            impressions = metrics.get("impressionCount", 0)
            likes = metrics.get("likeCount", 0)
            comments = metrics.get("commentCount", 0)
            shares = metrics.get("shareCount", 0)
            clicks = metrics.get("clickCount", 0)
            
            return {
                "impressions": impressions,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "clicks": clicks,
                "engagement": likes + comments + shares + clicks,
                "provider_metrics": metrics
            }

    async def get_account_metrics(
        self,
        account_id: str,
        access_token: str
    ) -> Dict[str, Any]:
        """Fetch account metrics for LinkedIn (e.g. followers using networkSizes)."""
        async with httpx.AsyncClient() as client:
            org_urn = quote(account_id)
            url = f"{self.API_BASE}/networkSizes/{org_urn}?edgeType=CompanyFollowedByOrganization"
            
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {access_token}", "X-Restli-Protocol-Version": "2.0.0"}
            )
            
            if response.status_code != 200:
                logger.error(f"LinkedIn account analytics fetch failed: {response.text}")
                if response.status_code in (401, 403):
                    raise SocialMediaAPIError(
                        message=f"LinkedIn authorization/permission error: {response.text}",
                        error_code="OAUTH_REAUTH_REQUIRED",
                        retryable=False,
                        metadata={"platform": "linkedin"}
                    )
                raise SocialMediaAPIError(
                    message="Failed to fetch LinkedIn account analytics.",
                    error_code="LINKEDIN_ANALYTICS_FAILED",
                    retryable=True,
                    metadata={"platform": "linkedin"}
                )

            data = response.json()
            followers = data.get("firstDegreeSize", 0)
            
            return {
                "followers": followers,
                "provider_metrics": data
            }
