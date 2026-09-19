from datetime import date, datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class SocialAnalyticsBase(BaseModel):
    platform: str
    external_post_id: str
    metric_date: date
    impressions: Optional[int] = None
    reach: Optional[int] = None
    engagement: Optional[int] = None
    clicks: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    saves: Optional[int] = None
    video_views: Optional[int] = None
    followers: Optional[int] = None

class SocialAnalyticsResponse(SocialAnalyticsBase):
    id: int
    user_id: int
    campaign_id: Optional[int] = None
    scheduled_post_id: Optional[int] = None
    collected_at: datetime
    
    class Config:
        from_attributes = True

class AnalyticsSummaryRequest(BaseModel):
    start_date: date
    end_date: date
    platforms: Optional[List[str]] = None
    campaign_id: Optional[int] = None

class PlatformSummary(BaseModel):
    platform: str
    total_impressions: int
    total_engagement: int
    total_clicks: int
    total_likes: int
    total_comments: int

class AnalyticsSummaryResponse(BaseModel):
    start_date: date
    end_date: date
    platforms: List[PlatformSummary]
    total_posts_analyzed: int
    overall_impressions: int
    overall_engagement: int
