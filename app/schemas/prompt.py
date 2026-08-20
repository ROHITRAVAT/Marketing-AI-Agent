from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PromptType(str, Enum):
    """Prompt type enumeration for categorising AI prompt templates."""
    CONTENT_GENERATION = "content_generation"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    AD_COPY = "ad_copy"
    SEO = "seo"
    BLOG = "blog"
    CUSTOM = "custom"


class PromptBase(BaseModel):
    """Base schema shared by create and update prompt schemas."""
    title: str = Field(..., min_length=1, max_length=255, description="Short descriptive title for this prompt template")
    template_text: str = Field(..., min_length=1, description="The full prompt template text used by the AI agent")
    prompt_type: PromptType = Field(default=PromptType.CONTENT_GENERATION, description="Category of the prompt template")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Optional JSON parameters/variables used inside the prompt template")
    campaign_id: Optional[int] = Field(None, gt=0, description="Optional campaign this prompt template belongs to")


class PromptCreate(PromptBase):
    """Schema for creating a new prompt template."""
    user_id: int = Field(..., gt=0, description="ID of the user who owns this prompt template")


class PromptUpdate(BaseModel):
    """Schema for updating an existing prompt template. All fields are optional."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    template_text: Optional[str] = Field(None, min_length=1)
    prompt_type: Optional[PromptType] = None
    parameters: Optional[Dict[str, Any]] = None
    campaign_id: Optional[int] = Field(None, gt=0)


class PromptResponse(PromptBase):
    """Schema for prompt responses returned from the API."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PromptListResponse(BaseModel):
    """Paginated list of prompt templates."""
    total: int = Field(..., description="Total number of matching prompt templates")
    page: int = Field(..., description="Current page number (1-indexed)")
    size: int = Field(..., description="Number of items per page")
    items: List[PromptResponse] = Field(..., description="List of prompt templates")
