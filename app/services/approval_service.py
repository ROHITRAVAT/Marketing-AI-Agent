from datetime import datetime
from typing import Optional, Tuple, Sequence

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from langgraph.types import Command

from app.models.approval import ApprovalRequest
from app.agents.enums import ApprovalStatus
from app.agents.graph import build_marketing_graph
from app.agents.checkpoint import get_checkpointer


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
        if not approval or approval.status != ApprovalStatus.PENDING:
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
        if not approval or approval.status != ApprovalStatus.PENDING:
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
