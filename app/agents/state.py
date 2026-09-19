from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

from app.agents.enums import AgentStatus, ApprovalStatus
from app.agents.schemas import (
    GeneratedContent,
    PlanStep,
    RetrievedDocument,
    ReviewResult,
    ToolResult,
    ErrorInfo,
)


class MarketingAgentState(BaseModel):
    # User / Request Information
    user_id: int | None = None
    campaign_id: int | None = None
    user_input: str = Field(default="", min_length=0)

    product: str | None = None
    target_audience: str | None = None
    platform: str | None = None
    campaign_goal: str | None = None

    # Conversation
    conversation_history: list[BaseMessage] = Field(
        default_factory=list
    )

    # Analysis / Strategy
    analysis: str | None = None
    strategy: str | None = None
    plan: list[PlanStep] = Field(
        default_factory=list
    )

    # RAG
    retrieved_documents: list[RetrievedDocument] = Field(
        default_factory=list
    )

    # Content Generation
    generated_content: GeneratedContent | None = None

    # Review / Approval
    review_result: ReviewResult | None = None
    approval_required: bool = False
    approval_request_id: int | None = None
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    revision_count: int = 0

    # Tool Execution
    tool_results: list[ToolResult] = Field(
        default_factory=list
    )

    # Clarification
    clarification_message: str | None = None

    # Workflow
    status: AgentStatus | None = None
    
    # Error Tracking & Recovery
    error: ErrorInfo | None = None
    error_message: str | None = None
    retry_count: int = 0
    last_failed_node: str | None = None
    last_failed_tool: str | None = None

    # Final Response
    final_response: str | None = None