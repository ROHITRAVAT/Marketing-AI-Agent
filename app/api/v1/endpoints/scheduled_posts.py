from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db_session
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.scheduled_post import ScheduledPost
from app.schemas.scheduled_post import ScheduledPostCreate, ScheduledPostResponse, ScheduledPostUpdate

router = APIRouter(prefix="/scheduled-posts", tags=["Scheduled Posts"])

@router.post("/", response_model=ScheduledPostResponse, status_code=status.HTTP_201_CREATED)
async def create_scheduled_post(
    post_in: ScheduledPostCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Schedule a new post."""
    # Ensure scheduled time is in the future
    if post_in.scheduled_time <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Scheduled time must be in the future.")
        
    db_post = ScheduledPost(
        user_id=current_user.id,
        platform=post_in.platform,
        account_id=post_in.account_id,
        content=post_in.content,
        media_urls=post_in.media_urls,
        scheduled_time=post_in.scheduled_time,
        timezone=post_in.timezone,
        campaign_id=post_in.campaign_id,
        approval_request_id=post_in.approval_request_id,
        status="scheduled"
    )
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post

@router.get("/", response_model=List[ScheduledPostResponse])
async def list_scheduled_posts(
    status_filter: Optional[str] = None,
    campaign_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """List scheduled posts for the current user."""
    stmt = select(ScheduledPost).where(ScheduledPost.user_id == current_user.id)
    if status_filter:
        stmt = stmt.where(ScheduledPost.status == status_filter)
    if campaign_id:
        stmt = stmt.where(ScheduledPost.campaign_id == campaign_id)
        
    stmt = stmt.order_by(ScheduledPost.scheduled_time.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{post_id}", response_model=ScheduledPostResponse)
async def get_scheduled_post(
    post_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific scheduled post."""
    result = await db.execute(
        select(ScheduledPost).where(ScheduledPost.id == post_id, ScheduledPost.user_id == current_user.id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Scheduled post not found")
    return post

@router.patch("/{post_id}", response_model=ScheduledPostResponse)
async def update_scheduled_post(
    post_id: int,
    post_in: ScheduledPostUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Reschedule a post."""
    result = await db.execute(
        select(ScheduledPost).where(ScheduledPost.id == post_id, ScheduledPost.user_id == current_user.id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Scheduled post not found")
        
    if post.status in ["processing", "published"]:
        raise HTTPException(status_code=400, detail=f"Cannot modify post in {post.status} status")
        
    if post_in.scheduled_time:
        if post_in.scheduled_time <= datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Scheduled time must be in the future.")
        post.scheduled_time = post_in.scheduled_time
    if post_in.timezone:
        post.timezone = post_in.timezone
        
    await db.commit()
    await db.refresh(post)
    return post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_scheduled_post(
    post_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Cancel a scheduled post."""
    result = await db.execute(
        select(ScheduledPost).where(ScheduledPost.id == post_id, ScheduledPost.user_id == current_user.id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Scheduled post not found")
        
    if post.status in ["processing", "published"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel post in {post.status} status")
        
    post.status = "cancelled"
    await db.commit()
    return None
