import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.twitter_service import TwitterService
from app.core.oauth.manager import TokenManager
from app.core.config import FRONTEND_URL, TWITTER_REDIRECT_URI
from app.schemas.integration import (
    TwitterAuthUrlResponse,
    TwitterStatusResponse,
    TwitterPostRequest,
    TwitterPostResponse,
    TwitterAnalyticsResponse,
)
from app.core.errors import SocialMediaAPIError

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/auth", response_model=TwitterAuthUrlResponse)
async def get_auth_url(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate Twitter OAuth 2.0 authorization URL with PKCE.
    """
    try:
        url, _state = await TokenManager.generate_auth_url(current_user.id, "twitter", db)
        return {"url": url}
    except Exception as e:
        logger.error(f"Error generating Twitter auth URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate Twitter authentication.")

@router.get("/callback")
async def twitter_callback(
    code: str = Query(..., description="Authorization code from Twitter"),
    state: str = Query(..., description="CSRF state from Twitter"),
    db: AsyncSession = Depends(get_db),
):
    """
    Handle OAuth callback from Twitter.
    """
    try:
        if not state.startswith("twitter_user_"):
            raise HTTPException(status_code=400, detail="Invalid state parameter.")
            
        await TokenManager.handle_callback(
            state=state,
            code=code,
            provider_name="twitter",
            redirect_uri=TWITTER_REDIRECT_URI,
            db=db
        )
        
        # Redirect back to the frontend settings page after successful auth
        return RedirectResponse(url=f"{FRONTEND_URL}/settings?tab=integrations&status=success&platform=twitter")
        
    except SocialMediaAPIError as e:
        logger.error(f"SocialMediaAPIError during Twitter callback: {e.message}")
        return RedirectResponse(url=f"{FRONTEND_URL}/settings?tab=integrations&status=error&platform=twitter&message={e.error_code}")
    except Exception as e:
        logger.error(f"Unexpected error during Twitter callback: {e}")
        return RedirectResponse(url=f"{FRONTEND_URL}/settings?tab=integrations&status=error&platform=twitter")

@router.get("/status", response_model=TwitterStatusResponse)
async def get_twitter_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check if the current user has connected a Twitter account.
    """
    try:
        conn = await TwitterService.get_connection(current_user.id, db)
        if conn:
            return TwitterStatusResponse(connected=True, account_name=conn.account_name)
        return TwitterStatusResponse(connected=False)
    except Exception as e:
        logger.error(f"Error checking Twitter status: {e}")
        return TwitterStatusResponse(connected=False)

@router.delete("")
async def disconnect_twitter(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect the user's Twitter account."""
    success = await TokenManager.disconnect(current_user.id, "twitter", db)
    if not success:
        raise HTTPException(status_code=404, detail="Twitter account not connected.")
    return {"message": "Twitter account disconnected successfully."}

@router.post("/posts", response_model=TwitterPostResponse)
async def publish_twitter_post(
    request: TwitterPostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Manually publish a post to Twitter.
    """
    try:
        post_id = await TwitterService.publish_post(
            user_id=current_user.id,
            content=request.content,
            db=db
        )
        return TwitterPostResponse(
            success=True,
            post_id=post_id,
            message="Successfully published to Twitter."
        )
    except SocialMediaAPIError as e:
        raise HTTPException(status_code=400, detail=e.user_message or e.message)
    except Exception as e:
        logger.error(f"Error publishing Twitter post: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while publishing to Twitter.")

@router.get("/analytics/{post_id}", response_model=TwitterAnalyticsResponse)
async def get_twitter_analytics(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch analytics/engagement metrics for a specific Twitter post.
    """
    try:
        metrics = await TwitterService.get_analytics(
            user_id=current_user.id,
            post_id=post_id,
            db=db
        )
        return TwitterAnalyticsResponse(**metrics)
    except SocialMediaAPIError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Error fetching Twitter analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching analytics.")
