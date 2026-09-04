from app.agents.state import MarketingAgentState
from app.agents.utils.errors import handle_node_error
from app.agents.enums import ApprovalStatus
from app.agents.schemas import ReviewResult
from app.langchain.chains import build_json_chain
from app.langchain.prompts import REVIEW_PROMPT


async def review_content(state: MarketingAgentState) -> dict:
    """
    Review the generated content against the strategy and plan.
    """

    print("Reviewing generated content...")

    try:
        if not state.generated_content:
            return {
                "approval_status": ApprovalStatus.REJECTED,
                "review_result": ReviewResult(
                    approved=False,
                    score=0.0,
                    feedback="No content was generated.",
                    issues=["Missing content"],
                ),
            }

        chain = build_json_chain(prompt=REVIEW_PROMPT)
        
        plan_str = "\n".join(f"{s.step_id}. {s.description}" for s in state.plan) if state.plan else "No plan provided."

        response = await chain.ainvoke(
            {
                "strategy": state.strategy or "",
                "plan": plan_str,
                "content": state.generated_content.body,
                "platform": state.platform or "",
                "audience": state.target_audience or "",
            }
        )
        
        approved = False
        score = 0.0
        feedback = "Failed to parse review response."
        issues = []

        if isinstance(response, dict):
            approved = bool(response.get("approved", False))
            score = float(response.get("score", 0.0))
            feedback = str(response.get("feedback", ""))
            issues = response.get("issues", [])

        review_result = ReviewResult(
            approved=approved,
            score=score,
            feedback=feedback,
            issues=issues,
        )

        approval_status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        
        # Increment revision count
        revision_count = state.revision_count + 1

        return {
            "review_result": review_result,
            "approval_status": approval_status,
            "revision_count": revision_count,
        }

    except Exception as error:
        return handle_node_error(
            state,
            error,
            "review_content",
        )
