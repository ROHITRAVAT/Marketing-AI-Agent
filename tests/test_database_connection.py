"""Database connectivity tests.

Requires the PostgreSQL container to be running and reachable.
Run with: pytest tests/test_database_connection.py -v
"""

import pytest
from sqlalchemy import text

from app.database.connection import engine
from app.database.session import SessionLocal


@pytest.fixture(autouse=True)
async def dispose_engine_after():
    """Dispose the shared engine after each test.

    pytest-asyncio runs each test on its own event loop. If pooled connections
    created on an earlier loop are reused on a later one, asyncpg raises
    ``RuntimeError: Event loop is closed``. Disposing the engine after every
    test releases those loop-bound connections before the loop is torn down.
    """
    yield
    await engine.dispose()


@pytest.mark.asyncio
async def test_sqlalchemy_engine_connect():
    """Verify the SQLAlchemy async engine can connect to PostgreSQL."""
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        value = result.scalar_one()
    assert value == 1


@pytest.mark.asyncio
async def test_async_session_works():
    """Verify AsyncSession can execute queries against PostgreSQL."""
    async with SessionLocal() as session:
        result = await session.execute(text("SELECT current_database()"))
        db_name = result.scalar_one()
    assert db_name is not None
    assert isinstance(db_name, str)