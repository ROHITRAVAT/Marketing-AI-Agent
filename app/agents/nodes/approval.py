from typing import Any
from langgraph.types import interrupt
from langgraph.errors import GraphInterrupt
from sqlalchemy import select

from app.agents.state import MarketingAgentState
from app.agents.enums import AgentStatus, ApprovalStatus
from app.agents.utils.errors import handle_node_error
from app.database.connection import AsyncSessionLocal
from app.models.approval import ApprovalRequest


async def request_human_approval(state: MarketingAgentState, config: dict[str, Any]) -> dict:
    """
    Determine if human approval is required.
    If required, create an ApprovalRequest in the DB and interrupt the graph.
    """
    print("Checking for human approval...")
    try:
        # Determine if approval is required. 
        # For this logic, any social media content publishing requires approval.
        requires_approval = False
        action_type = "unknown"
        platform = state.platform
        
        # Check plan steps for social media actions
        for step in state.plan or []:
            description_lower = step.description.lower()
            if "social" in description_lower:
                requires_approval = True
                action_type = "publish_social"
                break
                
        # Also check if platform is social media
        if platform and platform.lower() in ["linkedin", "twitter", "facebook", "instagram", "social_media"]:
            requires_approval = True
            action_type = "publish_social"
            
        # If approval is NOT required.
        # We don't check state.approval_status == APPROVED here because the previous QA node
        # sets it to APPROVED in order to route to this node.
        if not requires_approval:
            return {
                "approval_required": False
            }

        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            raise ValueError("thread_id not found in config")

        # Create approval request in the database
        async with AsyncSessionLocal() as db:
            # Idempotency check
            existing = await db.execute(
                select(ApprovalRequest).where(
                    ApprovalRequest.thread_id == thread_id,
                    ApprovalRequest.status == ApprovalStatus.PENDING
                )
            )
            existing_request = existing.scalar_one_or_none()
            
            if existing_request:
                approval_id = existing_request.id
            else:
                # Prepare payload
                payload = {
                    "product": state.product,
                    "target_audience": state.target_audience,
                    "generated_content": state.generated_content.model_dump() if state.generated_content else None,
                }
                
                new_request = ApprovalRequest(
                    user_id=state.user_id,
                    thread_id=thread_id,
                    action_type=action_type,
                    platform=platform,
                    content=payload,
                    status=ApprovalStatus.PENDING
                )
                db.add(new_request)
                await db.commit()
                await db.refresh(new_request)
                approval_id = new_request.id

        # Update state and interrupt
        new_state = {
            "status": AgentStatus.WAITING_FOR_APPROVAL,
            "approval_required": True,
            "approval_request_id": approval_id,
            "approval_status": ApprovalStatus.PENDING,
        }
        
        # Using langgraph 0.3 interrupt mechanism
        # The graph will pause here and return to the caller.
        # It resumes from here when invoked again with a Command(resume=...)
        # We catch the return value of interrupt to get the human response if provided via resume.
        user_response = interrupt(f"Approval required for request {approval_id}")
        
        # When resumed, user_response will contain the approval decision
        if isinstance(user_response, dict):
            if user_response.get("action") == "approve":
                return {
                    "status": AgentStatus.COMPLETED, # will be overridden by execution node
                    "approval_status": ApprovalStatus.APPROVED
                }
            else:
                return {
                    "status": AgentStatus.FAILED,
                    "approval_status": ApprovalStatus.REJECTED,
                    "error_message": user_response.get("reason", "User rejected the action")
                }
        
        return new_state

    except GraphInterrupt as gi:
        # Re-raise GraphInterrupt so LangGraph can properly pause execution
        raise gi
    except Exception as error:
        return handle_node_error(
            state,
            error,
            "request_human_approval",
        )
