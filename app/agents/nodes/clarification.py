from app.agents.state import MarketingAgentState


def request_clarification(state: MarketingAgentState) -> MarketingAgentState:
    """
    Identify missing marketing requirements and ask the user
    for the missing information.
    """

    print("Requesting clarification...")

    required_fields = {
        "product": "the product or service you want to promote",
        "target_audience": "the target audience",
        "platform": "the marketing platform",
        "campaign_goal": "the campaign goal",
    }

    missing_fields = []

    for field, description in required_fields.items():
        if not state.get(field):
            missing_fields.append(description)

    clarification_message = (
        "I need some additional information before I can create "
        "your marketing strategy. Please provide: "
        + ", ".join(missing_fields)
        + "."
    )

    return {
        **state,
        "clarification_message": clarification_message,
        "status": "needs_clarification",
    }