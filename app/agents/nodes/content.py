from app.agents.state import MarketingAgentState
from app.agents.utils.errors import handle_node_error
from app.langchain.chains import build_structured_chain
from app.langchain.schemas import ContentOutput
from app.langchain.prompts import CONTENT_GENERATION_PROMPT


async def generate_content(state: MarketingAgentState) -> MarketingAgentState:
    """
    Generate marketing content based on the strategy using LangChain.
    """

    print("Generating marketing content...")

    try:
        chain = build_structured_chain(
            schema=ContentOutput,
            prompt=CONTENT_GENERATION_PROMPT,
        )
        
        content_result = await chain.ainvoke({
            "content_type": f"{state.get('platform', 'Marketing')} Post",
            "brief": f"Product: {state.get('product', '')}\nGoal: {state.get('campaign_goal', '')}\nStrategy: {state.get('strategy', '')}",
            "tone": "Engaging and professional",
            "constraints": "JSON format according to schema",
        })

        content = content_result.model_dump_json(indent=2)

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