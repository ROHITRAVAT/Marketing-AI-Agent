from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CampaignStatus(str, Enum):
    """Campaign status enumeration."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class CampaignBase(BaseModel):
    """Base schema for campaign data."""

    name: str = Field(..., min_length=1, max_length=255, description="Name of the marketing campaign")
    description: Optional[str] = Field(None, description="Detailed description of the campaign goals and content")
    status: CampaignStatus = Field(default=CampaignStatus.DRAFT, description="Current operational status of the campaign")
    target_audience: Optional[str] = Field(None, description="Target demographic, persona, or audience description")
    budget: Optional[float] = Field(None, ge=0.0, description="Allocated budget for the campaign (must be non-negative)")
    start_date: Optional[datetime] = Field(None, description="Planned or actual start date/time")
    end_date: Optional[datetime] = Field(None, description="Planned or actual end date/time")

    @model_validator(mode="after")
    def validate_dates(self) -> "CampaignBase":
        """Ensure end_date is after start_date if both are provided."""
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class CampaignCreate(CampaignBase):
    """Schema for creating a new campaign."""

    user_id: int = Field(..., gt=0, description="ID of the user who owns this campaign")


class CampaignUpdate(BaseModel):
    """Schema for updating an existing campaign. All fields are optional."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None
    target_audience: Optional[str] = None
    budget: Optional[float] = Field(None, ge=0.0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_dates(self) -> "CampaignUpdate":
        """Ensure end_date is after start_date if both are provided in update."""
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class CampaignStatusUpdate(BaseModel):
    """Schema for updating only campaign status."""

    status: CampaignStatus = Field(..., description="New campaign status")


class CampaignResponse(CampaignBase):
    """Schema for campaign responses."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CampaignListResponse(BaseModel):
    """Paginated list of campaigns response."""

    total: int = Field(..., description="Total number of matching campaigns")
    page: int = Field(..., description="Current page number (1-indexed)")
    size: int = Field(..., description="Number of items per page")
    items: List[CampaignResponse] = Field(..., description="List of campaigns")
