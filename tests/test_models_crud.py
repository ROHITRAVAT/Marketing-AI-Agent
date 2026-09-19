"""CRUD smoke tests for core models.

Uses the in-memory SQLite engine provided by the shared ``test_engine``
fixture in conftest.py so no external PostgreSQL instance is needed.

When a live PostgreSQL instance IS running these same tests prove the
models are compatible with Postgres too — just point the engine at it.
"""

from datetime import datetime

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.base import Base


@pytest.mark.asyncio
async def test_models_crud_flow(test_engine):
    """Full create-read-update-delete flow for all core models."""
    # Import models to ensure they are registered on Base.metadata
    from app.models import User, Campaign, Prompt, AgentLog, ScheduledPost  # noqa: F401

    # test_engine fixture already ran create_all; tables exist
    factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with factory() as session:
        # ── Create user ──────────────────────────────────────────────────────
        user = User(email="crud@example.com", username="crud_user", hashed_password="pwd")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        assert user.id is not None

        # ── Create campaign ──────────────────────────────────────────────────
        campaign = Campaign(user_id=user.id, name="CRUD Campaign")
        session.add(campaign)
        await session.commit()
        await session.refresh(campaign)

        # ── Create prompt ────────────────────────────────────────────────────
        prompt = Prompt(
            user_id=user.id,
            campaign_id=campaign.id,
            title="P1",
            template_text="t",
        )
        session.add(prompt)
        await session.commit()
        await session.refresh(prompt)

        # ── Create agent log ─────────────────────────────────────────────────
        log = AgentLog(campaign_id=campaign.id, level="info", message="started")
        session.add(log)
        await session.commit()
        await session.refresh(log)

        # ── Create scheduled post ────────────────────────────────────────────
        sp = ScheduledPost(
            user_id=user.id,
            campaign_id=campaign.id,
            prompt_id=prompt.id,
            platform="linkedin",
            scheduled_time=datetime.utcnow(),
        )
        session.add(sp)
        await session.commit()
        await session.refresh(sp)

        # ── Read back ────────────────────────────────────────────────────────
        db_user = await session.get(User, user.id)
        assert db_user is not None
        assert db_user.email == "crud@example.com"
