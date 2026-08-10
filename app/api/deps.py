from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields a database session with automatic cleanup."""
    async for session in get_db():
        yield session


async def get_current_user():
    """Dependency that returns the currently authenticated user.

    TODO: Implement real authentication when security is added.
    """
    raise NotImplementedError("Authentication not implemented yet")