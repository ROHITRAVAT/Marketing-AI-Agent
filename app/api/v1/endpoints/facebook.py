from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.facebook_service import FacebookService
from app.core.oauth.manager import TokenManager
from app.core.config import FRONTEND_URL, META_REDIRECT_URI
from app.schemas.integration import (
    FacebookAuthUrlResponse,
    FacebookStatusResponse,
    FacebookPageInfo,
    FacebookPageSelectRequest,
    FacebookPostRequest,
    FacebookPostResponse,
)
from app.core.errors import SocialMediaAPIError

router = APIRouter()

@router.get("/auth", response_model=FacebookAuthUrlResponse)
async def get_auth_url(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Generate the Facebook OAuth authorization URL."""
    url, _state = await TokenManager.generate_auth_url(current_user.id, "facebook", db)
    return FacebookAuthUrlResponse(url=url)

@router.get("/callback")
async def facebook_callback(
    code: str = "",
    state: str = "",
    error: str = "",
    error_reason: str = "",
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Handle the OAuth2 callback from Facebook."""
    # Handle authorization denial
    if error:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/settings?facebook_error={error_reason or error}"
        )

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code.")

    try:
        # Base OAuth token exchange
        await TokenManager.handle_callback(
            state=state,
            code=code,
            provider_name="facebook",
            redirect_uri=META_REDIRECT_URI,
            db=db
        )
        
        # Extract user_id from state for page syncing
        parts = state.split("_")
        user_id = int(parts[2])
        
        # Post-auth: Discover and save manageable Pages
        await FacebookService.sync_pages(user_id=user_id, db=db)

    except SocialMediaAPIError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return RedirectResponse(
        url=f"{FRONTEND_URL}/settings?facebook_connected=true"
    )

@router.get("/status", response_model=FacebookStatusResponse)
async def get_facebook_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Check if the current user has a connected Facebook account."""
    connection = await FacebookService.get_connection(current_user.id, db)
    if not connection:
        return FacebookStatusResponse(connected=False)

    pages_raw = await FacebookService.get_user_pages(current_user.id, db)
    pages = [FacebookPageInfo(id=p["id"], name=p["name"]) for p in pages_raw]

    selected = await FacebookService.get_selected_page(current_user.id, db)
    selected_page = None
    if selected:
        selected_page = FacebookPageInfo(
            id=selected.provider_user_id,
            name=selected.account_name or "Unnamed Page",
        )

    return FacebookStatusResponse(
        connected=True,
        account_name=connection.account_name,
        pages=pages,
        selected_page=selected_page,
    )

@router.delete("")
async def disconnect_facebook(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Disconnect the user's Facebook account."""
    success_main = await TokenManager.disconnect(current_user.id, "facebook", db)
    success_pages = await TokenManager.disconnect(current_user.id, "facebook_page", db)
    
    if not (success_main or success_pages):
        raise HTTPException(status_code=404, detail="Facebook account not connected.")
    return {"message": "Facebook account disconnected successfully."}

@router.get("/pages")
async def get_pages(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Return safe metadata for the user's manageable Facebook Pages."""
    pages = await FacebookService.get_user_pages(current_user.id, db)
    return {"pages": pages}

@router.post("/pages/select")
async def select_page(
    request: FacebookPageSelectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Select a Facebook Page for publishing."""
    try:
        await FacebookService.select_page(
            user_id=current_user.id,
            page_id=request.page_id,
            db=db,
        )
        return {"success": True, "message": "Page selected successfully."}
    except SocialMediaAPIError as e:
        raise HTTPException(status_code=400, detail=e.message)

@router.post("/posts", response_model=FacebookPostResponse)
async def publish_post(
    request: FacebookPostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Publish a post to a Facebook Page."""
    try:
        post_id = await FacebookService.publish_post(
            user_id=current_user.id,
            content=request.content,
            db=db,
        )
        
        selected = await FacebookService.get_selected_page(current_user.id, db)
        page_id_used = selected.provider_user_id if selected else ""

        return FacebookPostResponse(
            success=True,
            platform="facebook",
            page_id=page_id_used,
            post_id=post_id,
            message="Facebook post published successfully.",
        )
    except SocialMediaAPIError as e:
        raise HTTPException(status_code=400, detail=e.message)
