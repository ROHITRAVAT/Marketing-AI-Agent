import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.agent import AgentChatRequest, AgentChatResponse
from app.agents.graph import build_marketing_graph
from app.agents.checkpoint import get_checkpointer
from app.agents.enums import AgentStatus, ApprovalStatus
from app.models.approval import ApprovalRequest
from app.models.agent_job import AgentJob
from app.database.connection import AsyncSessionLocal
from app.langchain.llm import build_chat_model
import asyncio
from sqlalchemy import select

logger = logging.getLogger(__name__)


def _is_casual_message(message: str) -> bool:
    normalized = message.strip().lower().rstrip("!?.")
    return normalized in {"hi", "hello", "hey", "hiya", "good morning", "good afternoon", "good evening"}

class AgentService:
    @staticmethod
    async def submit_chat_job(db: AsyncSession, user_id: int, request: AgentChatRequest) -> dict:
        from app.schemas.agent import AgentChatJobResponse
        job = AgentJob(
            user_id=user_id,
            thread_id=request.thread_id,
            status="queued"
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        # Schedule the background task
        asyncio.create_task(AgentService._run_chat_job(job.id, user_id, request))
        
        return AgentChatJobResponse(job_id=job.id, status="queued")

    @staticmethod
    async def get_job_status(db: AsyncSession, job_id: str):
        from app.schemas.agent import AgentJobStatusResponse, AgentChatResponse
        stmt = select(AgentJob).where(AgentJob.id == job_id)
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()
        if not job:
            return None
        
        result_obj = None
        if job.result:
            result_obj = AgentChatResponse(**job.result)
            
        return AgentJobStatusResponse(
            job_id=job.id,
            status=job.status,
            result=result_obj,
            error=job.error
        )

    @staticmethod
    async def _run_chat_job(job_id: str, user_id: int, request: AgentChatRequest):
        async with AsyncSessionLocal() as db:
            stmt = select(AgentJob).where(AgentJob.id == job_id)
            result = await db.execute(stmt)
            job = result.scalar_one_or_none()
            if not job:
                return
            job.status = "running"
            await db.commit()
            
            try:
                response = await AgentService._execute_chat(db, user_id, request)
                job.status = response.status
                job.result = response.model_dump()
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.exception(f"Error executing agent job {job_id}: {e}")
                job.status = "failed"
                job.error = str(e)
            finally:
                await db.commit()

    @staticmethod
    async def _execute_chat(db: AsyncSession, user_id: int, request: AgentChatRequest) -> AgentChatResponse:
        if request.mode == "copilot" or _is_casual_message(request.message):
            model = build_chat_model()
            response = await model.ainvoke([
                (
                    "system",
                    "You are Marketing Copilot, a helpful general-purpose AI assistant with strong marketing expertise. Answer every user question directly and naturally. You can discuss general topics, explain concepts, brainstorm, write and improve content, and create complete marketing plans. Do not require product, audience, platform, or campaign fields before answering. Ask a follow-up only when it genuinely improves the answer. Keep answers clear and practical.",
                ),
                ("human", request.message),
            ])
            return AgentChatResponse(
                status="completed",
                thread_id=request.thread_id,
                final_response=str(response.content),
            )

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
