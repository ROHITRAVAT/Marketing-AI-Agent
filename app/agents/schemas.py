from typing import Any

from pydantic import BaseModel, Field

from app.agents.enums import (
    PlanStepStatus,
    ToolExecutionStatus,
)

class PlanStep(BaseModel):
    step_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    status: PlanStepStatus = PlanStepStatus.PENDING
    result: str | None = None

class RetrievedDocument(BaseModel):
    document_id: str = Field(min_length=1)
    content: str = Field(min_length=1)
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)

class ErrorInfo(BaseModel):
    error_code: str
    category: str
    message: str
    retryable: bool
    user_message: str | None = None

class ToolResult(BaseModel):
    tool_name: str = Field(min_length=1)
    status: ToolExecutionStatus
    idempotency_key: str | None = None
    data: dict[str, Any] | None = None
    error: str | None = None
    error_info: ErrorInfo | None = None

class GeneratedContent(BaseModel):
    content_type: str = Field(default="", min_length=0)
    title: str | None = None
    body: str = Field(default="", min_length=0)
    metadata: dict[str, Any] = Field(default_factory=dict)

class ReviewResult(BaseModel):
    approved: bool
    score: float = Field(ge=0, le=10)
    feedback: str | None = None
    issues: list[str] = Field(default_factory=list)