from app.agents.state import MarketingAgentState
from app.agents.utils.errors import handle_node_error
from app.prompts.manager import prompt_manager
from app.ollama.service import get_ollama_service

async def generate_strategy(state: MarketingAgentState) -> MarketingAgentState:
    """
    Generate a basic marketing strategy from the analyzed request.
    """

    print("Generating marketing strategy...")

    try:
        rendered_prompt = prompt_manager.get(
            "campaign_strategy",
            product=state.get("product", ""),
            target_audience=state.get("target_audience", ""),
            platform=state.get("platform", ""),
            campaign_goal=state.get("campaign_goal", ""),
            analysis=state.get("analysis", "")
        )

        ollama = get_ollama_service()
        strategy = await ollama.generate(prompt=rendered_prompt)

        return {
            **state,
            "strategy": strategy,
            "status": "success",
            "error_message": "",
        }

    except Exception as error:
        return handle_node_error(
            state,
            error,
            "generate_strategy",
        )