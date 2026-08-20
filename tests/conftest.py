import pytest_asyncio

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.core.security import hash_password
from app.models.user import User


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_engine() -> AsyncEngine:
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine):
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        active_user = User(
            id=1,
            email="auth-test@example.com",
            username="auth_test",
            hashed_password=hash_password("StrongPass123"),
            full_name="Auth Test User",
            role="user",
            is_active=True,
            is_superuser=False,
        )

        inactive_user = User(
            id=9,
            email="inactive-test@example.com",
            username="inactive_test",
            hashed_password=hash_password("StrongPass123"),
            full_name="Inactive Test User",
            role="user",
            is_active=False,
            is_superuser=False,
        )

        session.add_all([active_user, inactive_user])
        await session.commit()

        yield session