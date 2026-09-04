from app.agents.state import MarketingAgentState
from app.agents.utils.errors import handle_node_error
from app.agents.schemas import GeneratedContent
from app.agents.enums import AgentStatus
from app.langchain.chains import build_text_chain
from app.langchain.prompts import CONTENT_GENERATION_PROMPT


async def generate_content(state: MarketingAgentState) -> dict:
    """
    Generate marketing content based on the strategy.
    """

    print("Generating marketing content...")

    try:
        retrieved_context = "\n\n".join(
            doc.content for doc in state.retrieved_documents
        ) if state.retrieved_documents else "No additional knowledge retrieved."

        chain = build_text_chain(prompt=CONTENT_GENERATION_PROMPT)

        plan_str = "\n".join(f"{s.step_id}. {s.description}" for s in state.plan) if state.plan else "No plan provided."

        content = await chain.ainvoke(
            {
                "content_type": "marketing copy",
                "platform": state.platform or "",
                "audience": state.target_audience or "",
                "tone": "professional yet engaging",
                "brief": state.user_input,
                "strategy": state.strategy or "",
                "plan": plan_str,
                "retrieved_context": retrieved_context,
                "constraints": "Follow platform guidelines.",
            }
        )

        generated_content = GeneratedContent(
            content_type="marketing_copy",
            body=content,
            metadata={
                "platform": state.platform,
                "campaign_goal": state.campaign_goal,
            },
        )

        return {
            "generated_content": generated_content,
            "status": AgentStatus.COMPLETED,
            "error_message": None,
        }

    except Exception as error:
        return handle_node_error(
            state,
            error,
            "generate_content",
        )
