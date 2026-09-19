from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class ScheduledPostBase(BaseModel):
    platform: str
    account_id: Optional[str] = None
    content: Optional[str] = None
    media_urls: Optional[List[str]] = None
    scheduled_time: datetime
    timezone: str = "UTC"
    campaign_id: Optional[int] = None
    approval_request_id: Optional[int] = None

class ScheduledPostCreate(ScheduledPostBase):
    pass

class ScheduledPostUpdate(BaseModel):
    scheduled_time: Optional[datetime] = None
    timezone: Optional[str] = None

class ScheduledPostResponse(ScheduledPostBase):
    id: int
    user_id: int
    status: str
    attempt_count: int
    last_attempt_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    external_post_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
