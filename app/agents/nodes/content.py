import uuid

from app.agents.state import MarketingAgentState
from app.agents.utils.errors import handle_node_error
from app.agents.schemas import GeneratedContent, LLMExecution
from app.agents.enums import AgentStatus
from app.langchain.prompts import CONTENT_GENERATION_PROMPT
from app.langchain.chains import build_text_chain


async def generate_content(state: MarketingAgentState) -> dict:
    """
    Generate marketing content based on the strategy.
    """

    print("Generating marketing content...")

    try:
        retrieved_context = "\n\n".join(
            doc.content for doc in state.retrieved_documents
        ) if state.retrieved_documents else "No additional knowledge retrieved."

        plan_str = "\n".join(f"{s.step_id}. {s.description}" for s in state.plan) if state.plan else "No plan provided."

        prompt_kwargs = {
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

        # Build prompt
        prompt_val = await CONTENT_GENERATION_PROMPT.ainvoke(prompt_kwargs)

        execution_id = str(uuid.uuid4())
        llm_execution = LLMExecution(
            llm_called=True,
            provider="ollama", # LangChain ChatOllama default provider here
            model="ollama", # Fallback since chain abstracts model
            prompt_sent=prompt_val.to_string(),
            execution_id=execution_id,
            node_name="generate_content",
        )

        chain = build_text_chain(prompt=CONTENT_GENERATION_PROMPT)

        # Call chain directly to capture response
        try:
            content = await chain.ainvoke(prompt_kwargs)
            llm_execution.response_received = True
            llm_execution.raw_llm_response = content
            llm_execution.response_used_as_final = True
        except Exception as e:
            llm_execution.response_received = False
            llm_execution.raw_llm_response = None
            llm_execution.response_used_as_final = False
            # Re-raise to trigger handle_node_error but we still want to capture the failed execution if possible.
            # But wait, if we raise here, we don't return llm_execution in the dict.
            # So let's return a dict with failed status and llm_execution, OR let handle_node_error do it.
            # handle_node_error doesn't know about llm_execution. Let's just raise and not capture it in state for now, 
            # or better, just return the state update here directly for failure so we preserve llm_execution.
            # Let's use handle_node_error, but state isn't updated. We can update state by returning it.
            error_dict = handle_node_error(state, e, "generate_content")
            error_dict["llm_execution"] = llm_execution
            return error_dict

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
            "llm_execution": llm_execution,
            "status": AgentStatus.COMPLETED,
            "error_message": None,
        }

    except Exception as error:
        return handle_node_error(
            state,
            error,
            "generate_content",
        )

