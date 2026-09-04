from app.agents.state import MarketingAgentState
from app.agents.utils.errors import handle_node_error
from app.agents.enums import AgentStatus
from app.langchain.chains import build_text_chain
from app.langchain.prompts import CAMPAIGN_STRATEGY_PROMPT


async def generate_strategy(state: MarketingAgentState) -> dict:
    """
    Generate a basic marketing strategy from the analyzed request.
    """

    print("Generating marketing strategy...")

    try:
        retrieved_knowledge = "\n\n".join(
            doc.content for doc in state.retrieved_documents
        ) if state.retrieved_documents else "No additional knowledge retrieved."

        chain = build_text_chain(prompt=CAMPAIGN_STRATEGY_PROMPT)

        strategy = await chain.ainvoke(
            {
                "campaign_brief": state.user_input,
                "target_audience": state.target_audience or "",
                "campaign_goal": state.campaign_goal or "",
                "brand_context": "",
                "retrieved_knowledge": retrieved_knowledge,
                "output_format": "Markdown document with sections for Objective, Audience, Key Message, and Approach.",
            }
        )

        return {
            "strategy": strategy,
            "status": AgentStatus.COMPLETED,
            "error_message": None,
        }

    except Exception as error:
        return handle_node_error(
            state,
            error,
            "generate_strategy",
        )
