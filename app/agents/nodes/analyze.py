from app.agents.state import MarketingAgentState
from app.agents.utils.errors import handle_node_error


def analyze_request(state: MarketingAgentState) -> dict:
    """
    Analyze the marketing request and return the analysis
    as a state update.
    """

    print("Analyzing marketing request...")

    try:
        required_fields = {
            "product": "product or service",
            "target_audience": "target audience",
            "platform": "marketing platform",
            "campaign_goal": "campaign goal",
        }

        missing_fields = []

        for field, description in required_fields.items():
            if not getattr(state, field):
                missing_fields.append(description)

        if missing_fields:
            analysis = (
                "The marketing request is incomplete. "
                "The following information is missing: "
                + ", ".join(missing_fields)
                + "."
            )
        else:
            analysis = (
                f"The user wants to create a {state.platform} campaign "
                f"for {state.product}, targeting "
                f"{state.target_audience}, with the goal of "
                f"{state.campaign_goal}."
            )

        return {
            "analysis": analysis,
        }

    except Exception as error:
        return handle_node_error(
            state,
            error,
            "analyze_request",
        )