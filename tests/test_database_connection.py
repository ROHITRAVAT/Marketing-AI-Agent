"""Database connectivity tests.

These tests verify SQLAlchemy async engine + session behaviour using an
in-memory SQLite database so they run without any external service.

When a live PostgreSQL instance IS available (e.g. inside Docker), the
postgres-specific tests in the ``test_database_connection_pg.py`` file
(if present) cover that layer instead.
"""

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


# ── Fixtures ──────────────────────────────────────────────────────────────────

SQLITE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def sqlite_engine():
    """Create a fresh async SQLite engine per test and dispose it afterwards."""
    engine = create_async_engine(SQLITE_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def sqlite_session(sqlite_engine):
    """Yield an AsyncSession bound to the per-test SQLite engine."""
    factory = async_sessionmaker(
        bind=sqlite_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with factory() as session:
        yield session


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_sqlalchemy_engine_connect(sqlite_engine):
    """Verify the SQLAlchemy async engine can connect and execute a query."""
    async with sqlite_engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        value = result.scalar_one()
    assert value == 1


@pytest.mark.asyncio
async def test_async_session_works(sqlite_session):
    """Verify AsyncSession can execute queries and return results."""
    result = await sqlite_session.execute(text("SELECT sqlite_version()"))
    db_version = result.scalar_one()
    assert db_version is not None
    assert isinstance(db_version, str)
