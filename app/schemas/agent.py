from typing import Optional
from pydantic import BaseModel, Field

class AgentChatRequest(BaseModel):
    thread_id: str = Field(..., description="Unique identifier for the conversation thread")
    message: str = Field(..., min_length=1, description="The user's input message")
    
    # Optional context overrides
    product: Optional[str] = Field(None, description="The product being marketed")
    target_audience: Optional[str] = Field(None, description="The target audience for the campaign")
    platform: Optional[str] = Field(None, description="The intended platform (e.g., LinkedIn, Twitter)")
    campaign_goal: Optional[str] = Field(None, description="The main goal of the campaign")

class AgentChatResponse(BaseModel):
    status: str = Field(..., description="Status of the request (e.g., 'completed', 'approval_pending', 'failed')")
    thread_id: str = Field(..., description="The conversation thread identifier")
    final_response: Optional[str] = Field(None, description="The final response or a message indicating approval is needed")
    approval_required: bool = Field(False, description="Whether human approval is required to continue")
    approval_request_id: Optional[int] = Field(None, description="The ID of the approval request if approval is required")
    error: Optional[str] = Field(None, description="Error message if the workflow failed")
