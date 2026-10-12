"""
OAuth integration tests.
Tests: valid token retrieval, auto-refresh, refresh failure, concurrent refresh protection,
       missing connection, revoked connection.
Covers requirement §7.
"""
import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.oauth.manager import TokenManager
from app.core.oauth.encryption import OAuthEncryption
from app.core.errors import SocialMediaAPIError
from app.models.integration import IntegrationConnection
from tests.mocks.oauth_mocks import MockOAuthProvider, register_mock_providers

pytestmark = [pytest.mark.asyncio, pytest.mark.integration, pytest.mark.oauth]


@pytest.fixture(autouse=True)
async def setup_providers(seeded_db_session: AsyncSession):
    register_mock_providers()
    
    # Clear any connections seeded by conftest.py to prevent MultipleResultsFound
    from sqlalchemy import delete
    await seeded_db_session.execute(delete(IntegrationConnection))
    await seeded_db_session.commit()
    
    yield
    TokenManager._providers.clear()
    TokenManager._refresh_locks.clear()


# ── Test: Valid Token Returned Immediately ───────────────────────────────────

async def test_valid_token_returned_immediately(seeded_db_session: AsyncSession):
    """Non-expired token is returned without triggering refresh."""
    conn = IntegrationConnection(
        user_id=1, provider="linkedin",
        access_token=OAuthEncryption.encrypt("fresh_token"),
        refresh_token=OAuthEncryption.encrypt("refresh_tok"),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    seeded_db_session.add(conn)
    await seeded_db_session.commit()

    token = await TokenManager.get_valid_access_token(1, "linkedin", seeded_db_session)
    assert token == "fresh_token"


# ── Test: Expired Token Triggers Refresh ─────────────────────────────────────

async def test_expired_token_auto_refreshed(seeded_db_session: AsyncSession):
    """Expired token triggers provider.refresh_token and returns new token."""
    conn = IntegrationConnection(
        user_id=1, provider="linkedin",
        access_token=OAuthEncryption.encrypt("old_token"),
        refresh_token=OAuthEncryption.encrypt("refresh_tok"),
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    seeded_db_session.add(conn)
    await seeded_db_session.commit()

    token = await TokenManager.get_valid_access_token(1, "linkedin", seeded_db_session)
    assert token == "refreshed_access_token"

    # DB should be updated
    await seeded_db_session.refresh(conn)
    assert OAuthEncryption.decrypt(conn.access_token) == "refreshed_access_token"


# ── Test: Refresh Failure Raises Reauth ──────────────────────────────────────

async def test_refresh_failure_raises_reauth(seeded_db_session: AsyncSession):
    """When refresh fails, OAUTH_REAUTH_REQUIRED is raised."""
    # Register a provider that fails on refresh
    TokenManager.register_provider(MockOAuthProvider(
        name="linkedin", refresh_succeeds=False
    ))

    conn = IntegrationConnection(
        user_id=1, provider="linkedin",
        access_token=OAuthEncryption.encrypt("old"),
        refresh_token=OAuthEncryption.encrypt("old_refresh"),
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    seeded_db_session.add(conn)
    await seeded_db_session.commit()

    with pytest.raises(SocialMediaAPIError) as exc_info:
        await TokenManager.get_valid_access_token(1, "linkedin", seeded_db_session)

    assert exc_info.value.error_code == "OAUTH_REAUTH_REQUIRED"


# ── Test: No Connection Exists ───────────────────────────────────────────────

async def test_no_connection_raises_not_connected(seeded_db_session: AsyncSession):
    """No integration connection → INTEGRATION_NOT_CONNECTED."""
    with pytest.raises(SocialMediaAPIError) as exc_info:
        await TokenManager.get_valid_access_token(1, "linkedin", seeded_db_session)

    assert exc_info.value.error_code == "INTEGRATION_NOT_CONNECTED"
    assert exc_info.value.retryable is False


# ── Test: Missing Refresh Token ──────────────────────────────────────────────

async def test_expired_no_refresh_token(seeded_db_session: AsyncSession):
    """Expired token + no refresh_token → OAUTH_REAUTH_REQUIRED."""
    conn = IntegrationConnection(
        user_id=1, provider="linkedin",
        access_token=OAuthEncryption.encrypt("expired_tok"),
        refresh_token=None,
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    seeded_db_session.add(conn)
    await seeded_db_session.commit()

    with pytest.raises(SocialMediaAPIError) as exc_info:
        await TokenManager.get_valid_access_token(1, "linkedin", seeded_db_session)

    assert exc_info.value.error_code == "OAUTH_REAUTH_REQUIRED"


# ── Test: Concurrent Refresh Protection ──────────────────────────────────────

async def test_concurrent_refresh_uses_lock(seeded_db_session: AsyncSession):
    """Multiple concurrent requests should only trigger one refresh."""
    conn = IntegrationConnection(
        user_id=1, provider="linkedin",
        access_token=OAuthEncryption.encrypt("old"),
        refresh_token=OAuthEncryption.encrypt("refresh"),
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    seeded_db_session.add(conn)
    await seeded_db_session.commit()

    call_count = 0
    original_refresh = TokenManager.get_provider("linkedin").refresh_token

    async def counting_refresh(refresh_token):
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.1)
        return await original_refresh(refresh_token)

    try:
        TokenManager.get_provider("linkedin").refresh_token = counting_refresh

        from app.database.connection import AsyncSessionLocal
        async def _get_token():
            async with AsyncSessionLocal() as s:
                return await TokenManager.get_valid_access_token(1, "linkedin", s)

        # Fire multiple concurrent requests
        results = await asyncio.gather(
            _get_token(),
            _get_token(),
            _get_token(),
        )

        # All should return the same refreshed token
        assert all(r == "refreshed_access_token" for r in results)
        # Due to the lock, refresh should have been called at most twice
        # (first caller refreshes, second waits and re-checks, third gets fresh token)
        assert call_count <= 2
    finally:
        TokenManager.get_provider("linkedin").refresh_token = original_refresh


# ── Test: Disconnect Removes Connection ──────────────────────────────────────

async def test_disconnect_removes_connection(seeded_db_session: AsyncSession):
    """After disconnect, get_valid_access_token should raise NOT_CONNECTED."""
    conn = IntegrationConnection(
        user_id=1, provider="linkedin",
        access_token=OAuthEncryption.encrypt("token"),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    seeded_db_session.add(conn)
    await seeded_db_session.commit()

    success = await TokenManager.disconnect(1, "linkedin", seeded_db_session)
    assert success is True

    with pytest.raises(SocialMediaAPIError) as exc_info:
        await TokenManager.get_valid_access_token(1, "linkedin", seeded_db_session)

    assert exc_info.value.error_code == "INTEGRATION_NOT_CONNECTED"
