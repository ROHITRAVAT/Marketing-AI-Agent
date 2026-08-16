"""Schemas package."""

from app.schemas.common import BaseResponse, SuccessResponse, ErrorResponse
from app.schemas.campaign import (
    CampaignStatus,
    CampaignBase,
    CampaignCreate,
    CampaignUpdate,
    CampaignStatusUpdate,
    CampaignResponse,
    CampaignListResponse,
)

__all__ = [
    "BaseResponse",
    "SuccessResponse",
    "ErrorResponse",
    "CampaignStatus",
    "CampaignBase",
    "CampaignCreate",
    "CampaignUpdate",
    "CampaignStatusUpdate",
    "CampaignResponse",
    "CampaignListResponse",
]
