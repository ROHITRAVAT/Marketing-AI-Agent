import httpx
import logging
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.integration import IntegrationConnection
from app.core.errors import SocialMediaAPIError
from app.core.oauth.manager import TokenManager
from app.core.oauth.encryption import OAuthEncryption

logger = logging.getLogger(__name__)

GRAPH_API_VERSION = "v21.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

class InstagramService:
    """Service layer for Instagram Graph API interactions."""

    @classmethod
    async def get_connection(cls, user_id: int, db: AsyncSession) -> Optional[IntegrationConnection]:
        """Get the user's base Instagram connection."""
        return await TokenManager.get_connection_status(user_id, "instagram", db)

    @classmethod
    async def get_selected_account(cls, user_id: int, db: AsyncSession) -> Optional[IntegrationConnection]:
        """Get the user's currently selected Instagram account connection."""
        result = await db.execute(
            select(IntegrationConnection).where(
                and_(
                    IntegrationConnection.user_id == user_id,
                    IntegrationConnection.provider == "instagram_account",
                    IntegrationConnection.scopes == "selected",
                )
            )
        )
        return result.scalar_one_or_none()

    @classmethod
    async def sync_ig_accounts(cls, user_id: int, db: AsyncSession) -> None:
        """Fetch Instagram Business Accounts linked to the user's FB Pages."""
        
        # Ensures user token is valid
        user_access_token = await TokenManager.get_valid_access_token(user_id, "instagram", db)

        async with httpx.AsyncClient() as client:
            pages_resp = await client.get(
                f"{GRAPH_API_BASE}/me/accounts",
                params={
                    "fields": "id,name,access_token,instagram_business_account{id,username,profile_picture_url}",
                    "access_token": user_access_token,
                },
            )

            if pages_resp.status_code != 200:
                raise SocialMediaAPIError(
                    message="Could not retrieve Facebook Pages.",
                    error_code="INSTAGRAM_DISCOVERY_FAILED",
                    retryable=True,
                    metadata={"platform": "instagram"},
                )

            pages_data = pages_resp.json().get("data", [])
            ig_accounts = []

            for page in pages_data:
                ig_info = page.get("instagram_business_account")
                if not ig_info:
                    continue

                ig_id = ig_info.get("id")
                ig_username = ig_info.get("username")
                page_access_token = page.get("access_token")

                ig_accounts.append({
                    "ig_id": ig_id,
                    "ig_username": ig_username,
                    "page_access_token": page_access_token,
                })

            if not ig_accounts:
                raise SocialMediaAPIError(
                    message="No Instagram Business Accounts found linked to your Facebook Pages.",
                    error_code="INSTAGRAM_NO_ACCOUNTS",
                    retryable=False,
                    user_message="No Instagram Business accounts were found. Ensure your Instagram account is set to Professional/Business and linked to a Facebook Page you manage.",
                    metadata={"platform": "instagram"},
                )

            # Persist IG accounts
            old_ig_result = await db.execute(
                select(IntegrationConnection).where(
                    and_(
                        IntegrationConnection.user_id == user_id,
                        IntegrationConnection.provider == "instagram_account",
                    )
                )
            )
            old_ig_accounts = old_ig_result.scalars().all()
            
            previously_selected_id = None
            for op in old_ig_accounts:
                if op.scopes == "selected":
                    previously_selected_id = op.provider_user_id
                await db.delete(op)

            first = True
            for acc in ig_accounts:
                is_selected = False
                if previously_selected_id:
                    is_selected = (acc["ig_id"] == previously_selected_id)
                elif first:
                    is_selected = True

                conn = IntegrationConnection(
                    user_id=user_id,
                    provider="instagram_account",
                    access_token=OAuthEncryption.encrypt(acc["page_access_token"]),
                    provider_user_id=acc["ig_id"],
                    account_name=acc["ig_username"],
                    scopes="selected" if is_selected else "available",
                )
                db.add(conn)
                first = False

            await db.commit()

    @classmethod
    async def get_user_accounts(cls, user_id: int, db: AsyncSession) -> List[Dict[str, str]]:
        result = await db.execute(
            select(IntegrationConnection).where(
                and_(
                    IntegrationConnection.user_id == user_id,
                    IntegrationConnection.provider == "instagram_account",
                )
            )
        )
        accounts = result.scalars().all()
        return [
            {"id": a.provider_user_id, "username": a.account_name or "Unknown"}
            for a in accounts
        ]

    @classmethod
    async def select_account(cls, user_id: int, account_id: str, db: AsyncSession) -> None:
        result = await db.execute(
            select(IntegrationConnection).where(
                and_(
                    IntegrationConnection.user_id == user_id,
                    IntegrationConnection.provider == "instagram_account",
                )
            )
        )
        accounts = result.scalars().all()

        if not accounts:
            raise SocialMediaAPIError(
                message="No Instagram accounts found for this user.",
                error_code="INSTAGRAM_NO_ACCOUNTS",
                retryable=False,
                metadata={"platform": "instagram"},
            )

        account_found = False
        for a in accounts:
            if a.provider_user_id == account_id:
                a.scopes = "selected"
                account_found = True
            else:
                a.scopes = "available"
            db.add(a)

        if not account_found:
            raise SocialMediaAPIError(
                message="Requested Instagram Account ID does not belong to this user.",
                error_code="INSTAGRAM_ACCOUNT_NOT_FOUND",
                retryable=False,
                metadata={"platform": "instagram"},
            )

        await db.commit()

    @classmethod
    async def publish_post(cls, user_id: int, image_url: str, caption: str, db: AsyncSession) -> str:
        # Check base connection validity
        try:
            await TokenManager.get_valid_access_token(user_id, "instagram", db)
        except SocialMediaAPIError as e:
            raise e

        ig_conn = await cls.get_selected_account(user_id, db)
        if not ig_conn:
            raise SocialMediaAPIError(
                message="No Instagram account selected.",
                error_code="INSTAGRAM_ACCOUNT_NOT_SELECTED",
                retryable=False,
                user_message="Please select an Instagram account in your settings.",
                metadata={"platform": "instagram"},
            )

        access_token = OAuthEncryption.decrypt(ig_conn.access_token)

        async with httpx.AsyncClient() as client:
            # 1. Create Media Container
            container_resp = await client.post(
                f"{GRAPH_API_BASE}/{ig_conn.provider_user_id}/media",
                params={
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": access_token,
                },
            )

            if container_resp.status_code not in (200, 201):
                err = container_resp.text
                logger.error(f"Instagram API container creation error: {err}")
                if container_resp.status_code in (401, 403):
                    raise SocialMediaAPIError(
                        message=f"Instagram authorization error: {err}",
                        error_code="INSTAGRAM_AUTH_ERROR",
                        retryable=False,
                        user_message="Instagram authorization failed. Please reconnect.",
                        metadata={"platform": "instagram"}
                    )
                raise SocialMediaAPIError(
                    message=f"Failed to create Instagram media container: {err}",
                    error_code="INSTAGRAM_API_ERROR",
                    retryable=False,
                    metadata={"platform": "instagram"}
                )

            creation_id = container_resp.json().get("id")

            # 2. Publish Media Container
            publish_resp = await client.post(
                f"{GRAPH_API_BASE}/{ig_conn.provider_user_id}/media_publish",
                params={
                    "creation_id": creation_id,
                    "access_token": access_token,
                },
            )

            if publish_resp.status_code not in (200, 201):
                err = publish_resp.text
                logger.error(f"Instagram API publish error: {err}")
                raise SocialMediaAPIError(
                    message=f"Failed to publish Instagram post: {err}",
                    error_code="INSTAGRAM_API_ERROR",
                    retryable=False,
                    metadata={"platform": "instagram"}
                )

            post_id = publish_resp.json().get("id")
            logger.info(f"Successfully published Instagram post: {post_id}")
            return post_id
