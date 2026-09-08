from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from app.core.config import DATABASE_URL

# psycopg doesn't support the "postgresql+asyncpg" scheme, so we need to replace it
# with "postgresql" or "postgres" for the pool connection string.
_pg_url = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

# Global pool for the checkpointer
_pool: AsyncConnectionPool | None = None

@asynccontextmanager
async def get_checkpointer():
    """
    Provide an AsyncPostgresSaver checkpointer for LangGraph.
    Manages the lifecycle of the connection pool.
    """
    global _pool
    if _pool is None:
        _pool = AsyncConnectionPool(
            conninfo=_pg_url,
            max_size=20,
            kwargs={
                "autocommit": True,
                "prepare_threshold": 0,
            }
        )
        await _pool.open()
        
        # Setup tables if they don't exist
        async with _pool.connection() as conn:
            # We must initialize the DB schema for checkpointer if not exists
            # We can use the async method 'setup' which is available on the saver.
            # However, initializing it here on every yield is a bit overkill, but setup() is idempotent.
            # To be safe, we do it.
            pass # We'll do setup in the app startup to avoid doing it per request.

    async with _pool.connection() as conn:
        saver = AsyncPostgresSaver(conn)
        yield saver

async def setup_checkpointer():
    """Run table creation for LangGraph checkpoints."""
    global _pool
    if _pool is None:
        _pool = AsyncConnectionPool(
            conninfo=_pg_url,
            max_size=20,
            kwargs={
                "autocommit": True,
                "prepare_threshold": 0,
            }
        )
        await _pool.open()
    
    async with _pool.connection() as conn:
        saver = AsyncPostgresSaver(conn)
        await saver.setup()
