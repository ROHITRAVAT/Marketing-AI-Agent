from app.agents.nodes.planning import create_plan
from app.agents.state import MarketingAgentState


def main():
    state = MarketingAgentState(
        user_input="Create a LinkedIn campaign for my AI marketing product.",
        product="AI Marketing Agent",
        target_audience="Small businesses",
        platform="LinkedIn",
        campaign_goal="Generate leads",
    )

    result = create_plan(state)

    print("\nPlanning Node Result:")
    print("=" * 50)

    for step in result["plan"]:
        print(f"{step.step_id}. {step.description}")
        print(f"   Status: {step.status}")
        print()


if __name__ == "__main__":
    main()