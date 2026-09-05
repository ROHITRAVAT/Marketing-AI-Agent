from app.agents.state import MarketingAgentState
from app.agents.utils.errors import handle_node_error
from app.agents.enums import ToolExecutionStatus
from app.agents.schemas import ToolResult
from app.langchain.chains import build_seo_chain, build_social_media_chain


async def execute_tools(state: MarketingAgentState) -> dict:
    """
    Execute real tools for each planned step.

    Currently dispatches SEO and social-media generation to their real
    LangChain chains when a plan step's description mentions them. Steps
    that don't match a known tool are recorded as skipped, not silently
    faked as successful.
    """

    print("Executing tools...")

    try:
        tool_results: list[ToolResult] = []

        content_body = state.generated_content.body if state.generated_content else ""

        for step in state.plan or []:
            description_lower = step.description.lower()

            try:
                if "seo" in description_lower:
                    chain = build_seo_chain()
                    result = await chain.ainvoke(
                        {
                            "product": state.product or "",
                            "target_audience": state.target_audience or "",
                            "generated_content": content_body,
                        }
                    )
                    tool_results.append(
                        ToolResult(
                            tool_name="seo_optimization",
                            status=ToolExecutionStatus.SUCCESS,
                            data={"output": result},
                        )
                    )

                elif "social" in description_lower:
                    chain = build_social_media_chain()
                    result = await chain.ainvoke(
                        {
                            "post_count": "3",
                            "platform": state.platform or "",
                            "brief": state.user_input,
                            "audience": state.target_audience or "",
                            "goal": state.campaign_goal or "",
                        }
                    )
                    tool_results.append(
                        ToolResult(
                            tool_name="social_media_generation",
                            status=ToolExecutionStatus.SUCCESS,
                            data={"output": result},
                        )
                    )

                else:
                    # No matching real tool for this step yet (e.g. ads, email,
                    # browser automation). Recorded honestly as skipped rather
                    # than faked as successful.
                    tool_results.append(
                        ToolResult(
                            tool_name=f"unmatched_step_{step.step_id}",
                            status=ToolExecutionStatus.FAILED,
                            error=f"No tool implemented for step: {step.description}",
                        )
                    )

            except Exception as tool_error:
                tool_results.append(
                    ToolResult(
                        tool_name=f"step_{step.step_id}",
                        status=ToolExecutionStatus.FAILED,
                        error=str(tool_error),
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