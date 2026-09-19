from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.instagram_service import InstagramService
from app.core.oauth.manager import TokenManager
from app.core.oauth.providers.instagram_provider import INSTAGRAM_REDIRECT_URI
from app.core.config import FRONTEND_URL
from app.schemas.integration import (
    InstagramAuthUrlResponse,
    InstagramStatusResponse,
    InstagramAccountInfo,
    InstagramAccountSelectRequest,
    InstagramPostRequest,
    InstagramPostResponse,
)
from app.core.errors import SocialMediaAPIError

router = APIRouter()

@router.get("/auth", response_model=InstagramAuthUrlResponse)
async def get_auth_url(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Generate the Meta OAuth authorization URL for Instagram."""
    url, _state = await TokenManager.generate_auth_url(current_user.id, "instagram", db)
    return InstagramAuthUrlResponse(url=url)

@router.get("/callback")
async def instagram_callback(
    code: str = "",
    state: str = "",
    error: str = "",
    error_reason: str = "",
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Handle the OAuth2 callback from Meta for Instagram."""
    if error:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/settings?instagram_error={error_reason or error}"
        )

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code.")

    try:
        # Base OAuth token exchange
        await TokenManager.handle_callback(
            state=state,
            code=code,
            provider_name="instagram",
            redirect_uri=INSTAGRAM_REDIRECT_URI,
            db=db
        )
        
        # Extract user_id from state for account syncing
        parts = state.split("_")
        user_id = int(parts[2])
        
        # Post-auth: Discover and save Instagram Business accounts
        await InstagramService.sync_ig_accounts(user_id=user_id, db=db)

    except SocialMediaAPIError as e:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/settings?instagram_error={e.error_code}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return RedirectResponse(
        url=f"{FRONTEND_URL}/settings?instagram_connected=true"
    )

@router.get("/status", response_model=InstagramStatusResponse)
async def get_instagram_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Check if the current user has connected Instagram accounts."""
    connection = await InstagramService.get_connection(current_user.id, db)
    if not connection:
        return InstagramStatusResponse(connected=False)

    accounts_raw = await InstagramService.get_user_accounts(current_user.id, db)
    accounts = [
        InstagramAccountInfo(
            id=acc["id"], 
            username=acc["username"],
        )
        for acc in accounts_raw
    ]

    selected = await InstagramService.get_selected_account(current_user.id, db)
    selected_account = None
    if selected:
        selected_account = InstagramAccountInfo(
            id=selected.provider_user_id,
            username=selected.account_name or "Unknown",
        )

    return InstagramStatusResponse(
        connected=True,
        accounts=accounts,
        selected_account=selected_account,
    )

@router.delete("")
async def disconnect_instagram(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Disconnect the user's Instagram accounts."""
    success_main = await TokenManager.disconnect(current_user.id, "instagram", db)
    success_accounts = await TokenManager.disconnect(current_user.id, "instagram_account", db)
    
    if not (success_main or success_accounts):
        raise HTTPException(status_code=404, detail="Instagram account not connected.")
    return {"message": "Instagram account disconnected successfully."}

@router.post("/accounts/select")
async def select_account(
    request: InstagramAccountSelectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Select an Instagram Account for publishing."""
    try:
        await InstagramService.select_account(
            user_id=current_user.id,
            account_id=request.account_id,
            db=db,
        )
        return {"success": True, "message": "Account selected successfully."}
    except SocialMediaAPIError as e:
        raise HTTPException(status_code=400, detail=e.message)

@router.post("/posts", response_model=InstagramPostResponse)
async def publish_post(
    request: InstagramPostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Publish a post to Instagram (manual test endpoint)."""
    try:
        media_id = await InstagramService.publish_post(
            user_id=current_user.id,
            image_url=request.image_url,
            caption=request.content,
            db=db,
        )
        
        selected = await InstagramService.get_selected_account(current_user.id, db)
        account_id_used = selected.provider_user_id if selected else ""

        return InstagramPostResponse(
            success=True,
            platform="instagram",
            account_id=account_id_used,
            media_id=media_id,
            message="Instagram post published successfully.",
        )
    except SocialMediaAPIError as e:
        raise HTTPException(status_code=400, detail=e.message)
