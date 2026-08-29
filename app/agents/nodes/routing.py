from app.agents.state import MarketingAgentState


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
        if not state.get(field):
            return "needs_clarification"

    return "ready_for_strategy"

def route_after_strategy(state: MarketingAgentState) -> str:
    """
    Decide whether to continue to content generation
    or stop because strategy generation failed.
    """

    if state["status"] == "failed":
        return "failed"

    return "ready_for_content"