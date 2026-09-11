from typing import List, Optional
from pydantic import BaseModel, Field

class CampaignStrategyOutput(BaseModel):
    """Structured output for campaign strategy."""
    target_audience: str = Field(description="Detailed description of the target audience.")
    key_messages: List[str] = Field(description="Key messages to convey in the campaign.")
    channels: List[str] = Field(description="Recommended marketing channels.")
    success_metrics: List[str] = Field(description="Metrics to measure campaign success.")
    budget_allocation: Optional[str] = Field(None, description="Suggested budget allocation.")

class ContentOutput(BaseModel):
    """Structured output for generated content."""
    headline: str = Field(description="The main headline or hook.")
    body_copy: str = Field(description="The main body text of the content.")
    call_to_action: str = Field(description="The call to action phrase.")
    hashtags: Optional[List[str]] = Field(None, description="Relevant hashtags.")

class HashtagOutput(BaseModel):
    """Structured output for generated hashtags."""
    hashtags: List[str] = Field(description="Optimized hashtags for the given platform and industry.")
    trending_note: Optional[str] = Field(None, description="Brief note on trending or high-reach tags, if any.")
