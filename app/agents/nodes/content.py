from app.agents.state import MarketingAgentState
from app.agents.utils.errors import handle_node_error
from app.prompts.manager import prompt_manager
from app.ollama.service import get_ollama_service


async def generate_content(state: MarketingAgentState) -> MarketingAgentState:
    """
    Generate marketing content based on the strategy.
    """

    print("Generating marketing content...")

    try:
        rendered_prompt = prompt_manager.get(
            "content_generation",
            product=state.get("product", ""),
            target_audience=state.get("target_audience", ""),
            platform=state.get("platform", ""),
            campaign_goal=state.get("campaign_goal", ""),
            strategy=state.get("strategy", "")
        )

        ollama = get_ollama_service()
        content = await ollama.generate(prompt=rendered_prompt)

        return {
            **state,
            "generated_content": content,
            "status": "completed",
        }

    except Exception as error:
        return handle_node_error(
            state,
            error,
            "generate_content",
        )