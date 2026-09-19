"""
Reusable test data factories for creating deterministic test records.
All factories return model instances without committing to the DB,
allowing callers to control transaction scope.
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

from app.models.user import User
from app.models.campaign import Campaign
from app.models.integration import IntegrationConnection
from app.models.scheduled_post import ScheduledPost
from app.models.approval import ApprovalRequest
from app.models.social_analytics import SocialAnalytics
from app.core.security import hash_password
from app.agents.enums import ApprovalStatus


# ─── Counters for unique IDs ───────────────────────────────────────────────
_counter = {"user": 100, "campaign": 100, "post": 100, "approval": 100, "analytics": 100}


def _next_id(category: str) -> int:
    _counter[category] += 1
    return _counter[category]


# ─── User Factory ──────────────────────────────────────────────────────────

def create_test_user(
    user_id: Optional[int] = None,
    email: Optional[str] = None,
    username: Optional[str] = None,
    password: str = "TestPass123!",
    is_active: bool = True,
    role: str = "user",
) -> User:
    uid = user_id or _next_id("user")
    return User(
        id=uid,
        email=email or f"testuser{uid}@example.com",
        username=username or f"testuser{uid}",
        hashed_password=hash_password(password),
        full_name=f"Test User {uid}",
        role=role,
        is_active=is_active,
        is_superuser=False,
    )


# ─── Campaign Factory ─────────────────────────────────────────────────────

def create_test_campaign(
    user_id: int,
    campaign_id: Optional[int] = None,
    name: Optional[str] = None,
    status: str = "active",
) -> Campaign:
    cid = campaign_id or _next_id("campaign")
    return Campaign(
        id=cid,
        user_id=user_id,
        name=name or f"Test Campaign {cid}",
        description=f"Test campaign description for campaign {cid}",
        status=status,
    )


# ─── Integration Connection Factory ───────────────────────────────────────

def create_test_integration(
    user_id: int,
    provider: str = "linkedin",
    access_token: str = "mock_access_token",
    refresh_token: Optional[str] = "mock_refresh_token",
    provider_user_id: str = "mock_provider_user_id",
    account_name: Optional[str] = None,
    expires_at: Optional[datetime] = None,
    scopes: Optional[str] = None,
) -> IntegrationConnection:
    return IntegrationConnection(
        user_id=user_id,
        provider=provider,
        access_token=access_token,
        refresh_token=refresh_token,
        provider_user_id=provider_user_id,
        account_name=account_name or f"{provider.capitalize()} Test Account",
        expires_at=expires_at or (datetime.now(timezone.utc) + timedelta(hours=1)),
        scopes=scopes,
    )


def create_expired_integration(
    user_id: int,
    provider: str = "linkedin",
    **kwargs,
) -> IntegrationConnection:
    """Creates an integration connection with an expired token."""
    return create_test_integration(
        user_id=user_id,
        provider=provider,
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        **kwargs,
    )


# ─── Scheduled Post Factory ───────────────────────────────────────────────

def create_test_scheduled_post(
    user_id: int,
    platform: str = "linkedin",
    content: str = "Test post content",
    status: str = "scheduled",
    scheduled_time: Optional[datetime] = None,
    campaign_id: Optional[int] = None,
    approval_request_id: Optional[int] = None,
    external_post_id: Optional[str] = None,
    account_id: Optional[str] = None,
    published_at: Optional[datetime] = None,
    attempt_count: int = 0,
    media_urls: Optional[list] = None,
) -> ScheduledPost:
    return ScheduledPost(
        user_id=user_id,
        platform=platform,
        content=content,
        status=status,
        scheduled_time=scheduled_time or (datetime.now(timezone.utc) - timedelta(minutes=5)),
        campaign_id=campaign_id,
        approval_request_id=approval_request_id,
        external_post_id=external_post_id,
        account_id=account_id,
        published_at=published_at,
        attempt_count=attempt_count,
        media_urls=media_urls,
    )


def create_future_scheduled_post(user_id: int, **kwargs) -> ScheduledPost:
    """Creates a post scheduled 1 day in the future."""
    return create_test_scheduled_post(
        user_id=user_id,
        scheduled_time=datetime.now(timezone.utc) + timedelta(days=1),
        **kwargs,
    )


def create_published_post(
    user_id: int,
    platform: str = "linkedin",
    external_post_id: Optional[str] = None,
    **kwargs,
) -> ScheduledPost:
    """Creates an already-published post (for analytics testing)."""
    return create_test_scheduled_post(
        user_id=user_id,
        platform=platform,
        status="published",
        external_post_id=external_post_id or f"ext_{platform}_{uuid.uuid4().hex[:8]}",
        account_id=f"urn:li:person:mock123" if platform == "linkedin" else None,
        published_at=datetime.now(timezone.utc) - timedelta(hours=2),
        **kwargs,
    )


# ─── Approval Request Factory ─────────────────────────────────────────────

def create_test_approval(
    user_id: int,
    thread_id: Optional[str] = None,
    action_type: str = "publish_social",
    platform: str = "linkedin",
    status: str = ApprovalStatus.PENDING,
    content: Optional[dict] = None,
) -> ApprovalRequest:
    return ApprovalRequest(
        user_id=user_id,
        thread_id=thread_id or str(uuid.uuid4()),
        action_type=action_type,
        platform=platform,
        status=status,
        content=content or {
            "product": "Test Product",
            "target_audience": "Test Audience",
            "generated_content": {"body": "Test generated content"},
        },
    )


# ─── Analytics Record Factory ─────────────────────────────────────────────

def create_test_analytics(
    user_id: int,
    platform: str = "linkedin",
    external_post_id: Optional[str] = None,
    metric_date=None,
    impressions: int = 1000,
    engagement: int = 100,
    clicks: int = 50,
    likes: int = 25,
    comments: int = 10,
    shares: int = 5,
    scheduled_post_id: Optional[int] = None,
    campaign_id: Optional[int] = None,
) -> SocialAnalytics:
    from datetime import date
    return SocialAnalytics(
        user_id=user_id,
        platform=platform,
        external_post_id=external_post_id or f"ext_{platform}_{uuid.uuid4().hex[:8]}",
        metric_date=metric_date or date.today(),
        impressions=impressions,
        engagement=engagement,
        clicks=clicks,
        likes=likes,
        comments=comments,
        shares=shares,
        scheduled_post_id=scheduled_post_id,
        campaign_id=campaign_id,
        collected_at=datetime.now(timezone.utc),
    )
