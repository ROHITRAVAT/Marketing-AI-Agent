from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict, Field

from app.agents.enums import ApprovalStatus


class ApprovalResponse(BaseModel):
    """Schema for a human approval request."""
    id: int
    user_id: int
    thread_id: str
    action_type: str
    platform: Optional[str] = None
    content: dict[str, Any]
    status: ApprovalStatus
    reason: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ApprovalListResponse(BaseModel):
    """Schema for paginated approval list."""
    items: list[ApprovalResponse]
    total: int
    page: int
    size: int


class ApprovalDecisionRequest(BaseModel):
    """Schema for approving a request."""
    reason: Optional[str] = Field(None, description="Optional comment or reason for approval")


class RejectionDecisionRequest(BaseModel):
    """Schema for rejecting a request."""
    reason: str = Field(..., description="Reason for rejecting the request")
