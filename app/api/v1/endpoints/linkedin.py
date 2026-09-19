from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.linkedin_service import LinkedInService
from app.core.oauth.manager import TokenManager
from app.core.config import FRONTEND_URL, LINKEDIN_REDIRECT_URI
from app.schemas.integration import (
    LinkedInStatusResponse,
    LinkedInPostRequest,
    LinkedInPostResponse,
    LinkedInAuthUrlResponse
)
from app.core.errors import SocialMediaAPIError

router = APIRouter()

@router.get("/auth", response_model=LinkedInAuthUrlResponse)
async def get_auth_url(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Generate the LinkedIn OAuth2 URL."""
    url, state = await TokenManager.generate_auth_url(current_user.id, "linkedin", db)
    return LinkedInAuthUrlResponse(url=url)

@router.get("/callback")
async def linkedin_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Handle the OAuth2 callback from LinkedIn."""
    try:
        await TokenManager.handle_callback(
            state=state,
            code=code,
            provider_name="linkedin",
            redirect_uri=LINKEDIN_REDIRECT_URI,
            db=db
        )
    except SocialMediaAPIError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return RedirectResponse(url=f"{FRONTEND_URL}/settings?linkedin_connected=true")

@router.get("/status", response_model=LinkedInStatusResponse)
async def get_linkedin_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Check if the current user has a connected LinkedIn account."""
    connection = await LinkedInService.get_connection(current_user.id, db)
    if connection:
        return LinkedInStatusResponse(
            connected=True,
            account_name=connection.account_name,
            provider="linkedin"
        )
    return LinkedInStatusResponse(connected=False, provider="linkedin")

@router.delete("")
async def disconnect_linkedin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Disconnect the user's LinkedIn account."""
    success = await TokenManager.disconnect(current_user.id, "linkedin", db)
    if not success:
        raise HTTPException(status_code=404, detail="LinkedIn account not connected.")
    return {"message": "LinkedIn account disconnected successfully."}

@router.post("/posts", response_model=LinkedInPostResponse)
async def publish_post(
    request: LinkedInPostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Publish a LinkedIn post directly."""
    try:
        post_id = await LinkedInService.publish_post(
            user_id=current_user.id,
            content=request.content,
            db=db
        )
        return LinkedInPostResponse(
            success=True,
            platform="linkedin",
            post_id=post_id,
            message="LinkedIn post published successfully."
        )
    except SocialMediaAPIError as e:
        raise HTTPException(status_code=400, detail=e.message)

@router.get("/analytics")
async def get_linkedin_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve LinkedIn analytics."""
    raise HTTPException(
        status_code=501,
        detail="LinkedIn Analytics API product access not currently implemented due to API scope constraints."
    )
