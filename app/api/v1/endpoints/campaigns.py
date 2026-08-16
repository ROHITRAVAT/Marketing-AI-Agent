from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.campaign import (
    CampaignCreate,
    CampaignListResponse,
    CampaignResponse,
    CampaignStatus,
    CampaignStatusUpdate,
    CampaignUpdate,
)
from app.schemas.common import SuccessResponse
from app.services.campaign_service import CampaignService

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.post(
    "/",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a marketing campaign",
    description="Creates a new marketing campaign with specified budget, audience, dates, and status.",
)
async def create_campaign(
    campaign_in: CampaignCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new campaign."""
    try:
        return await CampaignService.create_campaign(db, campaign_in)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(err)}",
        )


@router.get(
    "/",
    response_model=CampaignListResponse,
    status_code=status.HTTP_200_OK,
    summary="List marketing campaigns",
    description="Retrieves a paginated list of campaigns with optional filters for user_id, status, and search query.",
)
async def list_campaigns(
    user_id: Optional[int] = Query(None, description="Filter campaigns by owner user ID"),
    status_filter: Optional[CampaignStatus] = Query(None, alias="status", description="Filter campaigns by status"),
    search: Optional[str] = Query(None, description="Search term for campaign name or description"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(20, ge=1, le=100, description="Page size (max 100)"),
    db: AsyncSession = Depends(get_db_session),
):
    """List campaigns with pagination and filtering."""
    skip = (page - 1) * size
    items, total = await CampaignService.get_campaigns(
        db,
        user_id=user_id,
        status=status_filter,
        search=search,
        skip=skip,
        limit=size,
    )
    return CampaignListResponse(
        total=total,
        page=page,
        size=size,
        items=[CampaignResponse.model_validate(item) for item in items],
    )


@router.get(
    "/{campaign_id}",
    response_model=CampaignResponse,
    status_code=status.HTTP_200_OK,
    summary="Get campaign by ID",
    description="Retrieves single campaign details by its unique integer ID.",
)
async def get_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get a campaign by ID."""
    campaign = await CampaignService.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID {campaign_id} not found",
        )
    return campaign


@router.put(
    "/{campaign_id}",
    response_model=CampaignResponse,
    status_code=status.HTTP_200_OK,
    summary="Update campaign (full)",
    description="Updates all editable attributes of a campaign.",
)
async def update_campaign(
    campaign_id: int,
    campaign_in: CampaignUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Update a campaign by ID."""
    updated_campaign = await CampaignService.update_campaign(db, campaign_id, campaign_in)
    if not updated_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID {campaign_id} not found",
        )
    return updated_campaign


@router.patch(
    "/{campaign_id}",
    response_model=CampaignResponse,
    status_code=status.HTTP_200_OK,
    summary="Update campaign (partial)",
    description="Partially updates specified attributes of a campaign.",
)
async def patch_campaign(
    campaign_id: int,
    campaign_in: CampaignUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Partially update a campaign by ID."""
    updated_campaign = await CampaignService.update_campaign(db, campaign_id, campaign_in)
    if not updated_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID {campaign_id} not found",
        )
    return updated_campaign


@router.patch(
    "/{campaign_id}/status",
    response_model=CampaignResponse,
    status_code=status.HTTP_200_OK,
    summary="Update campaign status",
    description="Updates only the operational status of a campaign.",
)
async def update_campaign_status(
    campaign_id: int,
    status_in: CampaignStatusUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Update status of a campaign."""
    updated_campaign = await CampaignService.update_campaign_status(db, campaign_id, status_in)
    if not updated_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID {campaign_id} not found",
        )
    return updated_campaign


@router.delete(
    "/{campaign_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete campaign",
    description="Deletes a campaign and its associated records by ID.",
)
async def delete_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a campaign by ID."""
    deleted = await CampaignService.delete_campaign(db, campaign_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID {campaign_id} not found",
        )
    return SuccessResponse(
        success=True,
        message=f"Campaign {campaign_id} successfully deleted",
        data={"id": campaign_id},
    )
