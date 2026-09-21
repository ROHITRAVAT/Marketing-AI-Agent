import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.agent import AgentChatRequest, AgentChatResponse
from app.agents.graph import build_marketing_graph
from app.agents.checkpoint import get_checkpointer
from app.agents.enums import AgentStatus, ApprovalStatus
from app.models.approval import ApprovalRequest
from sqlalchemy import select

logger = logging.getLogger(__name__)

class AgentService:
    @staticmethod
    async def chat(db: AsyncSession, user_id: int, request: AgentChatRequest) -> AgentChatResponse:
        config = {"configurable": {"thread_id": request.thread_id}}
        
        async with get_checkpointer() as checkpointer:
            try:
                graph = build_marketing_graph()
                graph.checkpointer = checkpointer
                
                # Check current state to see if it's paused for approval
                state_snapshot = await graph.aget_state(config)
                
                if state_snapshot.values:
                    current_status = state_snapshot.values.get("status")
                    approval_id = state_snapshot.values.get("approval_request_id")
                    if not approval_id:
                        stmt = select(ApprovalRequest.id).where(
                            ApprovalRequest.thread_id == request.thread_id,
                            ApprovalRequest.status == ApprovalStatus.PENDING
                        )
                        result = await db.execute(stmt)
                        approval_id = result.scalar_one_or_none()
                        
                    if current_status == AgentStatus.WAITING_FOR_APPROVAL or approval_id:
                        logger.warning(f"Thread {request.thread_id} is waiting for approval.")
                        return AgentChatResponse(
                            status="approval_pending",
                            thread_id=request.thread_id,
                            final_response=None,
                            approval_required=True,
                            approval_request_id=approval_id
                        )

                # Prepare the input
                input_data = {
                    "user_input": request.message,
                    "user_id": user_id
                }
                
                if request.product:
                    input_data["product"] = request.product
                if request.target_audience:
                    input_data["target_audience"] = request.target_audience
                if request.platform:
                    input_data["platform"] = request.platform
                if request.campaign_goal:
                    input_data["campaign_goal"] = request.campaign_goal

                # Run the graph
                logger.info(f"Invoking graph for thread {request.thread_id}")
                result_state = await graph.ainvoke(input_data, config)
                
                # Check snapshot to see if interrupted
                post_snapshot = await graph.aget_state(config)
                
                # Check the result state to determine the response
                if post_snapshot.next and "request_human_approval" in post_snapshot.next:
                    approval_id = post_snapshot.values.get("approval_request_id")
                    if not approval_id:
                        stmt = select(ApprovalRequest.id).where(
                            ApprovalRequest.thread_id == request.thread_id,
                            ApprovalRequest.status == ApprovalStatus.PENDING
                        )
                        result = await db.execute(stmt)
                        approval_id = result.scalar_one_or_none()
                    
                    return AgentChatResponse(
                        status="approval_pending",
                        thread_id=request.thread_id,
                        final_response=None,
                        approval_required=True,
                        approval_request_id=approval_id
                    )
                elif result_state.get("status") == AgentStatus.WAITING_FOR_APPROVAL:
                    return AgentChatResponse(
                        status="approval_pending",
                        thread_id=request.thread_id,
                        final_response=None,
                        approval_required=True,
                        approval_request_id=result_state.get("approval_request_id")
                    )
                    
                if result_state.get("status") == AgentStatus.FAILED:
                    return AgentChatResponse(
                        status="failed",
                        thread_id=request.thread_id,
                        final_response=None,
                        error=result_state.get("error_message", "Unknown error")
                    )

                # Completed
                gen_content = result_state.get("generated_content")
                gen_body = gen_content.body if hasattr(gen_content, "body") else (gen_content.get("body") if isinstance(gen_content, dict) else None)
                
                verification_obj = result_state.get("verification")
                verification_dict = verification_obj.model_dump() if hasattr(verification_obj, "model_dump") else (verification_obj if isinstance(verification_obj, dict) else None)

                return AgentChatResponse(
                    status="completed",
                    thread_id=request.thread_id,
                    final_response=result_state.get("final_response"),
                    generated_content=gen_body,
                    verification=verification_dict
                )

            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Exception in process_request: {e}")
                logger.exception(f"Error executing agent workflow for thread {request.thread_id}: {str(e)}")
                return AgentChatResponse(
                    status="failed",
                    thread_id=request.thread_id,
                    final_response=None,
                    error=str(e)
                )
