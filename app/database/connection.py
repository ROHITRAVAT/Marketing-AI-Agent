from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from app.core.config import DATABASE_URL, DB_ECHO


def create_db_engine() -> AsyncEngine:
    """Create the asynchronous SQLAlchemy engine.

    Uses a NullPool-free default pool with sensible production defaults:
    pool_size and max_overflow are tuned for asyncpg connections.
    """
    return create_async_engine(
        DATABASE_URL,
        echo=DB_ECHO,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )


engine: AsyncEngine = create_db_engine()