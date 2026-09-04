from app.agents.state import MarketingAgentState
from app.agents.utils.errors import handle_node_error
from app.agents.enums import ToolExecutionStatus
from app.agents.schemas import ToolResult


def execute_tools(state: MarketingAgentState) -> dict:
    """
    Simulate tool execution for the generated plan.
    """

    print("Executing tools...")

    try:
        tool_results: list[ToolResult] = []

        if state.plan:
            for step in state.plan:
                # Simulate success for each planned step
                tool_results.append(
                    ToolResult(
                        tool_name=f"mock_tool_step_{step.step_id}",
                        status=ToolExecutionStatus.SUCCESS,
                        data={"message": f"Successfully executed step: {step.description}"}
                    )
                )

        return {
            "tool_results": tool_results,
        }

    except Exception as error:
        return handle_node_error(
            state,
            error,
            "execute_tools",
        )
