"""CRUD smoke tests for core models.

These tests require a running PostgreSQL instance accessible via the
environment-configured `DATABASE_URL` and will create/drop tables during
their run. Run with: pytest tests/test_models_crud.py -v
"""

from datetime import datetime

import pytest

from sqlalchemy import text

from app.database.connection import engine
from app.database.session import SessionLocal
from app.database.base import Base


@pytest.mark.asyncio
async def test_models_crud_flow():
    # Import models to ensure they're registered on the Base metadata
    from app.models import User, Campaign, Prompt, AgentLog, ScheduledPost  # noqa: F401

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        # Create user
        user = User(email="crud@example.com", username="crud_user", hashed_password="pwd")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        assert user.id is not None

        # Create campaign
        campaign = Campaign(user_id=user.id, name="CRUD Campaign")
        session.add(campaign)
        await session.commit()
        await session.refresh(campaign)

        # Create prompt
        prompt = Prompt(user_id=user.id, campaign_id=campaign.id, title="P1", template_text="t")
        session.add(prompt)
        await session.commit()
        await session.refresh(prompt)

        # Create agent log
        log = AgentLog(campaign_id=campaign.id, level="info", message="started")
        session.add(log)
        await session.commit()
        await session.refresh(log)

        # Create scheduled post
        sp = ScheduledPost(campaign_id=campaign.id, prompt_id=prompt.id, scheduled_time=datetime.utcnow())
        session.add(sp)
        await session.commit()
        await session.refresh(sp)

        # Basic queries
        db_user = await session.get(User, user.id)
        assert db_user and db_user.email == "crud@example.com"

    # Drop tables and dispose engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
