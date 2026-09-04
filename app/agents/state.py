from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

from app.agents.enums import AgentStatus, ApprovalStatus
from app.agents.schemas import (
    GeneratedContent,
    PlanStep,
    RetrievedDocument,
    ReviewResult,
    ToolResult,
)


class MarketingAgentState(BaseModel):
    # User / Request Information
    user_id: int | None = None
    user_input: str = Field(min_length=1)

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
    error_message: str | None = None

    # Final Response
    final_response: str | None = None