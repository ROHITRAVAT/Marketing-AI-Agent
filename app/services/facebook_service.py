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

class FacebookService:
    """Service layer for all Facebook / Meta Graph API interactions."""

    @classmethod
    async def get_connection(cls, user_id: int, db: AsyncSession) -> Optional[IntegrationConnection]:
        """Get the user's Facebook (user-level) connection metadata."""
        return await TokenManager.get_connection_status(user_id, "facebook", db)

    @classmethod
    async def get_selected_page(cls, user_id: int, db: AsyncSession) -> Optional[IntegrationConnection]:
        """Get the user's currently selected Facebook Page connection."""
        result = await db.execute(
            select(IntegrationConnection).where(
                and_(
                    IntegrationConnection.user_id == user_id,
                    IntegrationConnection.provider == "facebook_page",
                    IntegrationConnection.scopes == "selected",
                )
            )
        )
        return result.scalar_one_or_none()

    @classmethod
    async def sync_pages(cls, user_id: int, db: AsyncSession) -> None:
        """Fetch manageable Pages from Meta API and persist as facebook_page connections."""
        # Use TokenManager to ensure valid user access token
        user_access_token = await TokenManager.get_valid_access_token(user_id, "facebook", db)
        
        async with httpx.AsyncClient() as client:
            pages_resp = await client.get(
                f"{GRAPH_API_BASE}/me/accounts",
                params={
                    "fields": "id,name,access_token,tasks",
                    "access_token": user_access_token,
                },
            )

            if pages_resp.status_code != 200:
                logger.warning(f"Could not retrieve Facebook Pages: {pages_resp.text}")
                return

            pages_data = pages_resp.json().get("data", [])

            # Delete old page connections for this user before re-creating
            old_pages_result = await db.execute(
                select(IntegrationConnection).where(
                    and_(
                        IntegrationConnection.user_id == user_id,
                        IntegrationConnection.provider == "facebook_page",
                    )
                )
            )
            old_pages = old_pages_result.scalars().all()
            
            # Remember which page was previously selected
            previously_selected_page_id = None
            for op in old_pages:
                if op.scopes == "selected":
                    previously_selected_page_id = op.provider_user_id
                await db.delete(op)

            # Create new page connections
            first_page = True
            for page in pages_data:
                page_id = page.get("id")
                page_name = page.get("name")
                page_access_token = page.get("access_token")

                is_selected = False
                if previously_selected_page_id:
                    is_selected = (page_id == previously_selected_page_id)
                elif first_page:
                    is_selected = True

                page_conn = IntegrationConnection(
                    user_id=user_id,
                    provider="facebook_page",
                    access_token=OAuthEncryption.encrypt(page_access_token),
                    provider_user_id=page_id,
                    account_name=page_name,
                    scopes="selected" if is_selected else "available",
                )
                db.add(page_conn)
                first_page = False
                
            await db.commit()

    @classmethod
    async def get_user_pages(cls, user_id: int, db: AsyncSession) -> List[Dict[str, str]]:
        """Return safe metadata for all Facebook Pages the user manages."""
        result = await db.execute(
            select(IntegrationConnection).where(
                and_(
                    IntegrationConnection.user_id == user_id,
                    IntegrationConnection.provider == "facebook_page",
                )
            )
        )
        pages = result.scalars().all()
        return [
            {"id": p.provider_user_id, "name": p.account_name or "Unnamed Page"}
            for p in pages
        ]

    @classmethod
    async def select_page(cls, user_id: int, page_id: str, db: AsyncSession) -> None:
        """Select a Page for publishing. Validates ownership."""
        result = await db.execute(
            select(IntegrationConnection).where(
                and_(
                    IntegrationConnection.user_id == user_id,
                    IntegrationConnection.provider == "facebook_page",
                )
            )
        )
        pages = result.scalars().all()

        if not pages:
            raise SocialMediaAPIError(
                message="No Facebook Pages found for this user.",
                error_code="FACEBOOK_NO_PAGES",
                retryable=False,
                metadata={"platform": "facebook"},
            )

        page_found = False
        for p in pages:
            if p.provider_user_id == page_id:
                p.scopes = "selected"
                page_found = True
            else:
                p.scopes = "available"
            db.add(p)

        if not page_found:
            raise SocialMediaAPIError(
                message="Requested Page ID does not belong to this user.",
                error_code="FACEBOOK_PAGE_NOT_FOUND",
                retryable=False,
                metadata={"platform": "facebook"},
            )

        await db.commit()

    @classmethod
    async def publish_post(cls, user_id: int, content: str, db: AsyncSession) -> str:
        """Publish text content to the currently selected Facebook Page."""
        
        # Verify base connection still valid
        try:
            await TokenManager.get_valid_access_token(user_id, "facebook", db)
        except SocialMediaAPIError as e:
            # Pass it up
            raise e

        page_conn = await cls.get_selected_page(user_id, db)
        if not page_conn:
            raise SocialMediaAPIError(
                message="No Facebook Page selected for publishing.",
                error_code="FACEBOOK_PAGE_NOT_SELECTED",
                retryable=False,
                user_message="Please select a Facebook Page in your settings before publishing.",
                metadata={"platform": "facebook"},
            )

        # Page tokens don't generally expire if they are from a long-lived user token, 
        # but if we get an auth error, we know they are invalid.
        page_access_token = OAuthEncryption.decrypt(page_conn.access_token)

        async with httpx.AsyncClient() as client:
            logger.info(f"Publishing Facebook post for user {user_id} to page {page_conn.provider_user_id}")
            response = await client.post(
                f"{GRAPH_API_BASE}/{page_conn.provider_user_id}/feed",
                data={
                    "message": content,
                    "access_token": page_access_token,
                },
            )

            if response.status_code not in (200, 201):
                err = response.text
                logger.error(f"Facebook Graph API error: {err}")
                retryable = response.status_code in (429, 500, 502, 503, 504)
                if response.status_code in (401, 403):
                    raise SocialMediaAPIError(
                        message=f"Facebook authorization error: {err}",
                        error_code="FACEBOOK_AUTH_ERROR",
                        retryable=False,
                        user_message="Facebook authorization failed. Please reconnect your account.",
                        metadata={"platform": "facebook"}
                    )
                raise SocialMediaAPIError(
                    message=f"Facebook API error ({response.status_code}): {err}",
                    error_code="FACEBOOK_API_ERROR",
                    retryable=retryable,
                    metadata={"platform": "facebook"}
                )

            data = response.json()
            post_id = data.get("id")
            logger.info(f"Successfully published Facebook post: {post_id}")
            return post_id
