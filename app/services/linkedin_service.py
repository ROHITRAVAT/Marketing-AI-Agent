import httpx
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.integration import IntegrationConnection
from app.core.errors import SocialMediaAPIError
from app.core.oauth.manager import TokenManager

logger = logging.getLogger(__name__)

class LinkedInService:
    API_URL = "https://api.linkedin.com/v2"

    @classmethod
    async def get_connection(cls, user_id: int, db: AsyncSession) -> Optional[IntegrationConnection]:
        """Gets the raw connection metadata for LinkedIn (no decryption required)."""
        return await TokenManager.get_connection_status(user_id, "linkedin", db)
        
    @classmethod
    async def publish_post(cls, user_id: int, content: str, db: AsyncSession) -> str:
        """Publishes text content to LinkedIn."""
        # This implicitly checks connectivity, expiry, refreshes if needed, and returns decrypted access token.
        access_token = await TokenManager.get_valid_access_token(user_id, "linkedin", db)
        
        # We need the provider_user_id (LinkedIn URN id)
        connection = await cls.get_connection(user_id, db)
        if not connection or not connection.provider_user_id:
            raise SocialMediaAPIError(
                message="LinkedIn account is connected but missing user identity.",
                error_code="LINKEDIN_INVALID_CONNECTION",
                retryable=False,
                metadata={"platform": "linkedin"}
            )
            
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json"
            }
            
            urn = f"urn:li:person:{connection.provider_user_id}"
            
            payload = {
                "author": urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            logger.info(f"Publishing LinkedIn post for user {user_id}")
            try:
                response = await client.post(
                    f"{cls.API_URL}/ugcPosts",
                    headers=headers,
                    json=payload
                )
            except httpx.RequestError as e:
                logger.error(f"LinkedIn request error: {str(e)}")
                raise SocialMediaAPIError(
                    message=f"Network error communicating with LinkedIn: {str(e)}",
                    error_code="LINKEDIN_NETWORK_ERROR",
                    retryable=True,
                    metadata={"platform": "linkedin"}
                )
            
            if response.status_code not in (200, 201):
                err = response.text
                logger.error(f"LinkedIn API error: {err}")
                retryable = response.status_code in (429, 500, 502, 503, 504)
                if response.status_code in (401, 403):
                    raise SocialMediaAPIError(
                        message=f"LinkedIn authorization error: {err}",
                        error_code="OAUTH_REAUTH_REQUIRED",
                        retryable=False,
                        user_message="LinkedIn authorization failed. Please reconnect your account.",
                        metadata={"platform": "linkedin"}
                    )
                raise SocialMediaAPIError(
                    message=f"LinkedIn API error ({response.status_code}): {err}",
                    error_code="LINKEDIN_API_ERROR",
                    retryable=retryable,
                    metadata={"platform": "linkedin"}
                )
                
            data = response.json()
            post_id = data.get("id")
            logger.info(f"Successfully published LinkedIn post: {post_id}")
            return post_id
