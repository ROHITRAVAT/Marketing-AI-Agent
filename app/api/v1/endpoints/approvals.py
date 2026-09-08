from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_current_user
from app.models.user import User
from app.schemas.approval import (
    ApprovalResponse,
    ApprovalListResponse,
    ApprovalDecisionRequest,
    RejectionDecisionRequest
)
from app.services.approval_service import ApprovalService

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.get(
    "/pending",
    response_model=ApprovalListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get pending approvals",
    description="Retrieve a paginated list of pending approval requests for the authenticated user.",
)
async def get_pending_approvals(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(20, ge=1, le=100, description="Page size (max 100)"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    skip = (page - 1) * size
    items, total = await ApprovalService.get_pending_approvals(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=size,
    )
    return ApprovalListResponse(
        total=total,
        page=page,
        size=size,
        items=[ApprovalResponse.model_validate(item) for item in items],
    )


@router.get(
    "/{approval_id}",
    response_model=ApprovalResponse,
    status_code=status.HTTP_200_OK,
    summary="Get approval details",
    description="Retrieve details of a specific approval request.",
)
async def get_approval(
    approval_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    approval = await ApprovalService.get_approval(db, approval_id, current_user.id)
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found or not authorized.",
        )
    return approval


@router.post(
    "/{approval_id}/approve",
    response_model=ApprovalResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve a request",
    description="Approve a request and resume the associated workflow execution.",
)
async def approve_request(
    approval_id: int,
    request_data: ApprovalDecisionRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    approval = await ApprovalService.approve_request(
        db, approval_id, current_user.id, request_data.reason
    )
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found, not authorized, or already processed.",
        )
    return approval


@router.post(
    "/{approval_id}/reject",
    response_model=ApprovalResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject a request",
    description="Reject a request and terminate the associated workflow execution.",
)
async def reject_request(
    approval_id: int,
    request_data: RejectionDecisionRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    approval = await ApprovalService.reject_request(
        db, approval_id, current_user.id, request_data.reason
    )
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found, not authorized, or already processed.",
        )
    return approval
