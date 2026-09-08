from app.agents.state import MarketingAgentState
from app.agents.enums import AgentStatus, ApprovalStatus

def route_after_analysis(state: MarketingAgentState) -> str:
    """
    Decide whether the request contains enough information
    to continue with strategy generation.
    """

    required_fields = [
        "product",
        "target_audience",
        "platform",
        "campaign_goal",
    ]

    for field in required_fields:
        if not getattr(state, field):
            return "needs_clarification"

    return "ready_for_retrieval"


def route_after_strategy(state: MarketingAgentState) -> str:
    """
    Decide whether to continue to planning
    or stop because strategy generation failed.
    """

    if state.status == AgentStatus.FAILED:
        return "failed"

    return "ready_for_planning"


def route_after_review(state: MarketingAgentState) -> str:
    """
    Decide whether to continue to tool execution,
    go back to content generation for revision,
    or fail if max revisions exceeded.
    """

    if state.status == AgentStatus.FAILED:
        return "failed"

    if state.approval_status == ApprovalStatus.APPROVED:
        return "approved"
    
    if state.revision_count >= 3:
        return "failed"
        
    return "needs_revision"


def route_after_human_approval(state: MarketingAgentState) -> str:
    """
    Decide whether to execute tools or fail based on human approval.
    """
    if state.status == AgentStatus.FAILED or state.approval_status == ApprovalStatus.REJECTED:
        return "failed"

    return "approved"