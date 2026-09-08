from app.agents.state import MarketingAgentState
from app.agents.utils.errors import handle_node_error
from app.agents.enums import AgentStatus


def generate_final_response(state: MarketingAgentState) -> dict:
    """
    Format the internal state into a clean user-facing response.
    """

    print("Generating final response...")

    try:
        if state.status == AgentStatus.FAILED:
            final_response = f"Workflow failed: {state.error_message}"
        elif state.status == AgentStatus.NEEDS_CLARIFICATION:
            final_response = state.clarification_message or "Please provide more information."
        else:
            final_response_parts = []
            
            if state.generated_content:
                final_response_parts.append(
                    f"# Content Generated\n\n{state.generated_content.body}\n"
                )
            
            if state.strategy:
                final_response_parts.append(
                    f"# Strategy\n\n{state.strategy}\n"
                )
            
            if state.plan:
                plan_str = "\n".join(f"- {s.step_id}: {s.description}" for s in state.plan)
                final_response_parts.append(
                    f"# Plan Executed\n\n{plan_str}\n"
                )

            if state.tool_results:
                final_response_parts.append(
                    f"# Tools Executed\n\nSuccessfully executed {len(state.tool_results)} tools.\n"
                )
                
            final_response = "\n".join(final_response_parts) if final_response_parts else "Workflow completed successfully but no response was generated."

        preserve_statuses = [
            AgentStatus.FAILED, 
            AgentStatus.NEEDS_CLARIFICATION, 
            AgentStatus.REQUIRES_MANUAL_ACTION
        ]
        
        return {
            "final_response": final_response,
            "status": state.status if state.status in preserve_statuses else AgentStatus.COMPLETED,
        }

    except Exception as error:
        return handle_node_error(
            state,
            error,
            "generate_final_response",
        )
