import logging
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prompt import Prompt
from app.models.user import User
from app.models.campaign import Campaign
from app.schemas.prompt import PromptCreate, PromptUpdate

logger = logging.getLogger(__name__)


class PromptService:
    """Service handling database operations for AI prompt templates."""

    @staticmethod
    async def create_prompt(db: AsyncSession, prompt_in: PromptCreate) -> Prompt:
        """Create a new prompt template in the database."""
        # Ensure user exists, auto-create for dev/test environments if missing
        user = await db.get(User, prompt_in.user_id)
        if not user:
            logger.info("User id=%s not found, auto-creating for prompt creation", prompt_in.user_id)
            user = User(
                id=prompt_in.user_id,
                email=f"user{prompt_in.user_id}@example.com",
                username=f"user_{prompt_in.user_id}",
                hashed_password="default_hashed_password",
            )
            db.add(user)
            await db.flush()

        # Validate campaign exists if provided
        if prompt_in.campaign_id is not None:
            campaign = await db.get(Campaign, prompt_in.campaign_id)
            if not campaign:
                raise ValueError(f"Campaign with id={prompt_in.campaign_id} does not exist")

        prompt_data = prompt_in.model_dump()
        if hasattr(prompt_data.get("prompt_type"), "value"):
            prompt_data["prompt_type"] = prompt_data["prompt_type"].value

        prompt = Prompt(**prompt_data)
        db.add(prompt)
        await db.commit()
        await db.refresh(prompt)
        logger.info("Created prompt '%s' (id=%s) for user_id=%s", prompt.title, prompt.id, prompt.user_id)
        return prompt

    @staticmethod
    async def get_prompt(db: AsyncSession, prompt_id: int) -> Optional[Prompt]:
        """Fetch a single prompt template by its ID."""
        return await db.get(Prompt, prompt_id)

    @staticmethod
    async def get_prompts(
        db: AsyncSession,
        *,
        user_id: Optional[int] = None,
        campaign_id: Optional[int] = None,
        prompt_type: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Prompt], int]:
        """Retrieve paginated prompt templates with optional filtering and search."""
        query = select(Prompt)
        count_query = select(func.count(Prompt.id))

        filters = []
        if user_id is not None:
            filters.append(Prompt.user_id == user_id)
        if campaign_id is not None:
            filters.append(Prompt.campaign_id == campaign_id)
        if prompt_type is not None:
            type_val = prompt_type.value if hasattr(prompt_type, "value") else str(prompt_type)
            filters.append(Prompt.prompt_type == type_val)
        if search is not None and search.strip():
            search_pattern = f"%{search.strip()}%"
            filters.append(
                or_(
                    Prompt.title.ilike(search_pattern),
                    Prompt.template_text.ilike(search_pattern),
                )
            )

        if filters:
            query = query.where(*filters)
            count_query = count_query.where(*filters)

        query = query.order_by(Prompt.created_at.desc()).offset(skip).limit(limit)

        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        items_result = await db.execute(query)
        items = list(items_result.scalars().all())

        return items, total

    @staticmethod
    async def update_prompt(
        db: AsyncSession, prompt_id: int, prompt_in: PromptUpdate
    ) -> Optional[Prompt]:
        """Update fields of an existing prompt template."""
        prompt = await db.get(Prompt, prompt_id)
        if not prompt:
            return None

        # Validate campaign exists if changing campaign_id
        update_data = prompt_in.model_dump(exclude_unset=True)
        if "campaign_id" in update_data and update_data["campaign_id"] is not None:
            campaign = await db.get(Campaign, update_data["campaign_id"])
            if not campaign:
                raise ValueError(f"Campaign with id={update_data['campaign_id']} does not exist")

        for field, value in update_data.items():
            if value is not None:
                if hasattr(value, "value"):
                    value = value.value
                setattr(prompt, field, value)

        await db.commit()
        await db.refresh(prompt)
        logger.info("Updated prompt id=%s", prompt_id)
        return prompt

    @staticmethod
    async def delete_prompt(db: AsyncSession, prompt_id: int) -> bool:
        """Delete a prompt template by ID."""
        prompt = await db.get(Prompt, prompt_id)
        if not prompt:
            return False

        await db.delete(prompt)
        await db.commit()
        logger.info("Deleted prompt id=%s", prompt_id)
        return True
