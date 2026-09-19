from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import date

from app.api.deps import get_db_session, get_current_user
from app.models.user import User
from app.models.social_analytics import SocialAnalytics
from app.schemas.analytics import SocialAnalyticsResponse, AnalyticsSummaryResponse, PlatformSummary

router = APIRouter()

@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    start_date: date,
    end_date: date,
    platforms: Optional[str] = None, # comma separated
    campaign_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get aggregated analytics summary across platforms for a date range."""
    
    # Base query
    stmt = select(
        SocialAnalytics.platform,
        func.count(SocialAnalytics.id).label("post_count"),
        func.sum(SocialAnalytics.impressions).label("total_impressions"),
        func.sum(SocialAnalytics.engagement).label("total_engagement"),
        func.sum(SocialAnalytics.clicks).label("total_clicks"),
        func.sum(SocialAnalytics.likes).label("total_likes"),
        func.sum(SocialAnalytics.comments).label("total_comments")
    ).where(
        SocialAnalytics.user_id == current_user.id,
        SocialAnalytics.metric_date >= start_date,
        SocialAnalytics.metric_date <= end_date
    ).group_by(SocialAnalytics.platform)
    
    if platforms:
        platform_list = [p.strip().lower() for p in platforms.split(",")]
        stmt = stmt.where(SocialAnalytics.platform.in_(platform_list))
        
    if campaign_id:
        stmt = stmt.where(SocialAnalytics.campaign_id == campaign_id)
        
    result = await db.execute(stmt)
    rows = result.all()
    
    platform_summaries = []
    overall_impressions = 0
    overall_engagement = 0
    total_posts = 0
    
    for row in rows:
        p_impressions = row.total_impressions or 0
        p_engagement = row.total_engagement or 0
        p_count = row.post_count or 0
        
        platform_summaries.append(PlatformSummary(
            platform=row.platform,
            total_impressions=p_impressions,
            total_engagement=p_engagement,
            total_clicks=row.total_clicks or 0,
            total_likes=row.total_likes or 0,
            total_comments=row.total_comments or 0
        ))
        
        overall_impressions += p_impressions
        overall_engagement += p_engagement
        total_posts += p_count
        
    return AnalyticsSummaryResponse(
        start_date=start_date,
        end_date=end_date,
        platforms=platform_summaries,
        total_posts_analyzed=total_posts,
        overall_impressions=overall_impressions,
        overall_engagement=overall_engagement
    )

@router.get("/posts/{post_id}", response_model=List[SocialAnalyticsResponse])
async def get_post_analytics(
    post_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get analytics snapshots for a specific external post ID."""
    stmt = select(SocialAnalytics).where(
        SocialAnalytics.user_id == current_user.id,
        SocialAnalytics.external_post_id == post_id
    ).order_by(SocialAnalytics.metric_date.desc())
    
    result = await db.execute(stmt)
    records = result.scalars().all()
    
    if not records:
        raise HTTPException(status_code=404, detail="Analytics not found for this post")
        
    return records
