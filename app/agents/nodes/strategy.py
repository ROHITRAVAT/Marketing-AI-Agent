from app.agents.state import MarketingAgentState
from app.agents.utils.errors import handle_node_error
from app.langchain.chains import build_structured_chain
from app.langchain.schemas import CampaignStrategyOutput
from app.langchain.prompts import CAMPAIGN_STRATEGY_PROMPT

async def generate_strategy(state: MarketingAgentState) -> MarketingAgentState:
    """
    Generate a structured marketing strategy using LangChain.
    """

    print("Generating marketing strategy...")

    try:
        chain = build_structured_chain(
            schema=CampaignStrategyOutput,
            prompt=CAMPAIGN_STRATEGY_PROMPT,
        )
        
        # We need to map state variables to prompt variables
        strategy_result = await chain.ainvoke({
            "campaign_brief": f"Product: {state.get('product', '')}\nGoal: {state.get('campaign_goal', '')}\nAnalysis: {state.get('analysis', '')}",
            "brand_context": f"Targeting {state.get('target_audience', '')} on {state.get('platform', '')}",
            "output_format": "JSON according to the schema",
        })

        # strategy_result is a CampaignStrategyOutput model instance
        # we can serialize it to a string or dictionary to store in state
        strategy = strategy_result.model_dump_json(indent=2)

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