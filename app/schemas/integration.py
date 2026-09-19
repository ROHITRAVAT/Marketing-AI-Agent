from pydantic import BaseModel
from typing import Optional, List


# ── LinkedIn Schemas ──────────────────────────────────────────────────────────

class LinkedInStatusResponse(BaseModel):
    """Response schema for LinkedIn connection status."""
    connected: bool
    account_name: Optional[str] = None
    provider: str = "linkedin"

class LinkedInPostRequest(BaseModel):
    """Request schema for publishing a LinkedIn post."""
    content: str

class LinkedInPostResponse(BaseModel):
    """Response schema after successfully publishing a LinkedIn post."""
    success: bool
    platform: str = "linkedin"
    post_id: str
    message: str

class LinkedInAuthUrlResponse(BaseModel):
    """Response schema for LinkedIn authorization URL."""
    url: str


# ── Facebook / Meta Schemas ───────────────────────────────────────────────────

class FacebookAuthUrlResponse(BaseModel):
    """Response schema for Facebook authorization URL."""
    url: str

class FacebookPageInfo(BaseModel):
    """Safe metadata for a Facebook Page (never includes access tokens)."""
    id: str
    name: str

class FacebookStatusResponse(BaseModel):
    """Response schema for Facebook connection status."""
    connected: bool
    account_name: Optional[str] = None
    provider: str = "facebook"
    pages: List[FacebookPageInfo] = []
    selected_page: Optional[FacebookPageInfo] = None

class FacebookPageSelectRequest(BaseModel):
    """Request schema for selecting a Facebook Page."""
    page_id: str

class FacebookPostRequest(BaseModel):
    """Request schema for publishing a Facebook Page post."""
    page_id: Optional[str] = None
    content: str

class FacebookPostResponse(BaseModel):
    """Response schema after successfully publishing a Facebook post."""
    success: bool
    platform: str = "facebook"
    page_id: str
    post_id: str
    message: str


# ── Instagram Schemas ─────────────────────────────────────────────────────────

class InstagramAuthUrlResponse(BaseModel):
    """Response schema for Instagram authorization URL."""
    url: str

class InstagramAccountInfo(BaseModel):
    """Safe metadata for an Instagram Business Account."""
    id: str
    username: str
    profile_picture_url: Optional[str] = None

class InstagramStatusResponse(BaseModel):
    """Response schema for Instagram connection status."""
    connected: bool
    provider: str = "instagram"
    accounts: List[InstagramAccountInfo] = []
    selected_account: Optional[InstagramAccountInfo] = None

class InstagramAccountSelectRequest(BaseModel):
    """Request schema for selecting an Instagram Account."""
    account_id: str

class InstagramPostRequest(BaseModel):
    """Request schema for publishing an Instagram post."""
    account_id: Optional[str] = None
    content: str
    image_url: Optional[str] = None

class InstagramPostResponse(BaseModel):
    """Response schema after successfully publishing an Instagram post."""
    success: bool
    platform: str = "instagram"
    account_id: str
    media_id: str
    message: str


# ── Twitter / X Schemas ───────────────────────────────────────────────────────

class TwitterAuthUrlResponse(BaseModel):
    """Response schema for Twitter authorization URL."""
    url: str

class TwitterStatusResponse(BaseModel):
    """Response schema for Twitter connection status."""
    connected: bool
    account_name: Optional[str] = None
    provider: str = "twitter"

class TwitterPostRequest(BaseModel):
    """Request schema for publishing a Twitter post."""
    content: str

class TwitterPostResponse(BaseModel):
    """Response schema after successfully publishing a Twitter post."""
    success: bool
    platform: str = "twitter"
    post_id: str
    message: str

class TwitterAnalyticsResponse(BaseModel):
    """Response schema for Twitter engagement metrics."""
    post_id: str
    likes: int
    reposts: int
    replies: int
    quotes: int
    bookmarks: int
    impressions: int
