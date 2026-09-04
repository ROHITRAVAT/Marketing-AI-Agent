from app.agents.enums import PlanStepStatus
from app.agents.schemas import PlanStep
from app.agents.state import MarketingAgentState
from app.agents.utils.errors import handle_node_error
from app.langchain.chains import build_json_chain
from app.langchain.prompts import PLANNING_PROMPT


async def create_plan(state: MarketingAgentState) -> dict:
    """
    Create an execution plan for the marketing request using the LLM.
    """

    print("Creating marketing execution plan...")

    try:
        chain = build_json_chain(prompt=PLANNING_PROMPT)

        response = await chain.ainvoke(
            {
                "strategy": state.strategy or "No strategy available.",
                "campaign_goal": state.campaign_goal or "",
                "platform": state.platform or "",
            }
        )

        plan: list[PlanStep] = []

        if isinstance(response, list):
            for step in response:
                if isinstance(step, dict) and "step_id" in step and "description" in step:
                    plan.append(
                        PlanStep(
                            step_id=str(step["step_id"]),
                            description=str(step["description"]),
                            status=PlanStepStatus.PENDING,
                        )
                    )
        elif isinstance(response, dict) and "steps" in response:
            for step in response["steps"]:
                if isinstance(step, dict) and "step_id" in step and "description" in step:
                    plan.append(
                        PlanStep(
                            step_id=str(step["step_id"]),
                            description=str(step["description"]),
                            status=PlanStepStatus.PENDING,
                        )
                    )

        if not plan:
            # Fallback if parsing fails or returns empty
            plan.append(
                PlanStep(
                    step_id="1",
                    description="Execute the generated strategy.",
                    status=PlanStepStatus.PENDING,
                )
            )

        return {
            "plan": plan,
        }

    except Exception as error:
        return handle_node_error(
            state,
            error,
            "create_plan",
        )