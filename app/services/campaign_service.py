import logging
from typing import List, Optional, Tuple

from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign
from app.models.user import User
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignStatusUpdate

logger = logging.getLogger(__name__)


class CampaignService:
    """Service handling database operations for marketing campaigns."""

    @staticmethod
    async def create_campaign(db: AsyncSession, campaign_in: CampaignCreate) -> Campaign:
        """Create a new campaign in the database."""
        # Ensure user exists or create default user if user_id doesn't exist
        user = await db.get(User, campaign_in.user_id)
        if not user:
            # Fallback for dev environments: create default user if not found
            logger.info("User with id %s not found, auto-creating default user for campaign", campaign_in.user_id)
            user = User(
                id=campaign_in.user_id,
                email=f"user{campaign_in.user_id}@example.com",
                username=f"user_{campaign_in.user_id}",
                hashed_password="default_hashed_password",
            )
            db.add(user)
            await db.flush()

        campaign_data = campaign_in.model_dump()
        # Convert enum status to string value if needed
        if hasattr(campaign_data.get("status"), "value"):
            campaign_data["status"] = campaign_data["status"].value

        campaign = Campaign(**campaign_data)
        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)
        logger.info("Created campaign %s (id=%s) for user_id=%s", campaign.name, campaign.id, campaign.user_id)
        return campaign

    @staticmethod
    async def get_campaign(db: AsyncSession, campaign_id: int) -> Optional[Campaign]:
        """Fetch a campaign by its ID."""
        return await db.get(Campaign, campaign_id)

    @staticmethod
    async def get_campaigns(
        db: AsyncSession,
        *,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Campaign], int]:
        """Retrieve paginated campaigns with optional filtering and search."""
        query = select(Campaign)
        count_query = select(func.count(Campaign.id))

        filters = []
        if user_id is not None:
            filters.append(Campaign.user_id == user_id)
        if status is not None:
            status_val = status.value if hasattr(status, "value") else str(status)
            filters.append(Campaign.status == status_val)
        if search is not None and search.strip():
            search_pattern = f"%{search.strip()}%"
            filters.append(
                or_(
                    Campaign.name.ilike(search_pattern),
                    Campaign.description.ilike(search_pattern),
                    Campaign.target_audience.ilike(search_pattern),
                )
            )

        if filters:
            query = query.where(*filters)
            count_query = count_query.where(*filters)

        # Order by created_at descending
        query = query.order_by(Campaign.created_at.desc()).offset(skip).limit(limit)

        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        items_result = await db.execute(query)
        items = list(items_result.scalars().all())

        return items, total

    @staticmethod
    async def update_campaign(
        db: AsyncSession, campaign_id: int, campaign_in: CampaignUpdate
    ) -> Optional[Campaign]:
        """Update fields of an existing campaign."""
        campaign = await db.get(Campaign, campaign_id)
        if not campaign:
            return None

        update_data = campaign_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                if hasattr(value, "value"):
                    value = value.value
                setattr(campaign, field, value)

        await db.commit()
        await db.refresh(campaign)
        logger.info("Updated campaign id=%s", campaign_id)
        return campaign

    @staticmethod
    async def update_campaign_status(
        db: AsyncSession, campaign_id: int, status_in: CampaignStatusUpdate
    ) -> Optional[Campaign]:
        """Update only the status of a campaign."""
        campaign = await db.get(Campaign, campaign_id)
        if not campaign:
            return None

        status_val = status_in.status.value if hasattr(status_in.status, "value") else str(status_in.status)
        campaign.status = status_val

        await db.commit()
        await db.refresh(campaign)
        logger.info("Updated status of campaign id=%s to '%s'", campaign_id, status_val)
        return campaign

    @staticmethod
    async def delete_campaign(db: AsyncSession, campaign_id: int) -> bool:
        """Delete a campaign by ID."""
        campaign = await db.get(Campaign, campaign_id)
        if not campaign:
            return False

        await db.delete(campaign)
        await db.commit()
        logger.info("Deleted campaign id=%s", campaign_id)
        return True
