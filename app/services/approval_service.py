from datetime import datetime
from typing import Optional, Tuple, Sequence

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from langgraph.types import Command

from app.models.approval import ApprovalRequest
from app.models.agent_job import AgentJob
from app.agents.enums import ApprovalStatus, AgentStatus
from app.agents.graph import build_marketing_graph
from app.agents.checkpoint import get_checkpointer
from app.schemas.agent import AgentChatResponse


class ApprovalService:
    @staticmethod
    async def get_pending_approvals(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[Sequence[ApprovalRequest], int]:
        """Get pending approval requests for a user."""
        # Get total count
        count_query = select(func.count()).select_from(ApprovalRequest).where(
            ApprovalRequest.user_id == user_id,
            ApprovalRequest.status == ApprovalStatus.PENDING
        )
        total = await db.scalar(count_query) or 0

        # Get items
        query = select(ApprovalRequest).where(
            ApprovalRequest.user_id == user_id,
            ApprovalRequest.status == ApprovalStatus.PENDING
        ).order_by(ApprovalRequest.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total

    @staticmethod
    async def get_approval(
        db: AsyncSession,
        approval_id: int,
        user_id: int
    ) -> Optional[ApprovalRequest]:
        """Get a specific approval request for a user."""
        query = select(ApprovalRequest).where(
            ApprovalRequest.id == approval_id,
            ApprovalRequest.user_id == user_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def approve_request(
        db: AsyncSession,
        approval_id: int,
        user_id: int,
        reason: Optional[str] = None
    ) -> Optional[ApprovalRequest]:
        """Approve a request and resume the LangGraph workflow."""
        approval = await ApprovalService.get_approval(db, approval_id, user_id)
        if not approval:
            return None
        if approval.status != ApprovalStatus.PENDING:
            return approval

        # Update status
        approval.status = ApprovalStatus.APPROVED
        approval.reason = reason
        approval.approved_at = func.now()
        await db.commit()
        await db.refresh(approval)

        # Resume LangGraph Workflow
        result_state = await ApprovalService._resume_workflow(approval.thread_id, {"action": "approve", "reason": reason})
        if result_state:
            setattr(approval, "final_response", result_state.get("final_response"))

        # Find and update originating AgentJob
        target_job_id = approval.job_id
        job = None
        if target_job_id:
            job = await db.get(AgentJob, target_job_id)

        if not job:
            job_stmt = (
                select(AgentJob)
                .where(
                    AgentJob.thread_id == approval.thread_id,
                    AgentJob.user_id == user_id,
                )
                .order_by(AgentJob.created_at.desc())
            )
            job_res = await db.execute(job_stmt)
            job = job_res.scalars().first()
            if job:
                approval.job_id = job.id

        if job:
            if result_state and result_state.get("status") == AgentStatus.FAILED:
                job.status = "failed"
                job.error = result_state.get("error_message") or "Workflow execution failed"
            else:
                job.status = "completed"
                gen_content = result_state.get("generated_content") if result_state else None
                gen_body = gen_content.body if hasattr(gen_content, "body") else (gen_content.get("body") if isinstance(gen_content, dict) else None)
                verification_obj = result_state.get("verification") if result_state else None
                verification_dict = verification_obj.model_dump() if hasattr(verification_obj, "model_dump") else (verification_obj if isinstance(verification_obj, dict) else None)

                chat_res = AgentChatResponse(
                    status="completed",
                    thread_id=approval.thread_id,
                    final_response=result_state.get("final_response") if result_state else approval.final_response,
                    generated_content=gen_body,
                    verification=verification_dict
                )
                job.result = chat_res.model_dump()

            await db.commit()
            await db.refresh(approval)

        return approval

    @staticmethod
    async def reject_request(
        db: AsyncSession,
        approval_id: int,
        user_id: int,
        reason: str
    ) -> Optional[ApprovalRequest]:
        """Reject a request and terminate the LangGraph workflow."""
        approval = await ApprovalService.get_approval(db, approval_id, user_id)
        if not approval:
            return None
        if approval.status != ApprovalStatus.PENDING:
            return approval

        # Update status
        approval.status = ApprovalStatus.REJECTED
        approval.rejection_reason = reason
        approval.rejected_at = func.now()
        await db.commit()
        await db.refresh(approval)

        # Resume LangGraph Workflow
        result_state = await ApprovalService._resume_workflow(approval.thread_id, {"action": "reject", "reason": reason})
        if result_state:
            setattr(approval, "final_response", result_state.get("final_response"))

        # Find and update originating AgentJob
        target_job_id = approval.job_id
        job = None
        if target_job_id:
            job = await db.get(AgentJob, target_job_id)

        if not job:
            job_stmt = (
                select(AgentJob)
                .where(
                    AgentJob.thread_id == approval.thread_id,
                    AgentJob.user_id == user_id,
                )
                .order_by(AgentJob.created_at.desc())
            )
            job_res = await db.execute(job_stmt)
            job = job_res.scalars().first()
            if job:
                approval.job_id = job.id

        if job:
            job.status = "failed"
            job.error = reason or "Approval rejected by user"
            chat_res = AgentChatResponse(
                status="failed",
                thread_id=approval.thread_id,
                final_response=None,
                error=reason
            )
            job.result = chat_res.model_dump()
            await db.commit()
            await db.refresh(approval)

        return approval

    @staticmethod
    async def _resume_workflow(thread_id: str, resume_data: dict) -> dict:
        """Resume the LangGraph workflow given the thread_id and resume data."""
        config = {"configurable": {"thread_id": thread_id}}
        
        async with get_checkpointer() as checkpointer:
            # We must compile the graph with the checkpointer to be able to resume
            graph = build_marketing_graph()
            graph.checkpointer = checkpointer
            
            # Send the command to resume the graph
            # This executes the graph until completion or another interruption
            return await graph.ainvoke(Command(resume=resume_data), config)
