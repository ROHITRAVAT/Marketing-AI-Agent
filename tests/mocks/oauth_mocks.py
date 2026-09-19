"""
OAuth mock utilities for integration testing.
Provides mock token scenarios: valid, expired, no-refresh, revoked.
"""
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from contextlib import asynccontextmanager

from app.core.oauth.provider import OAuthProvider, TokenExchangeResult
from app.core.oauth.manager import TokenManager
from app.core.errors import SocialMediaAPIError


class MockOAuthProvider(OAuthProvider):
    """A mock OAuth provider for testing all token lifecycle flows."""
    
    def __init__(
        self,
        name: str = "mock_provider",
        requires_pkce: bool = False,
        refresh_succeeds: bool = True,
        new_access_token: str = "refreshed_access_token",
        new_refresh_token: str = "refreshed_refresh_token",
    ):
        self._name = name
        self._requires_pkce = requires_pkce
        self._refresh_succeeds = refresh_succeeds
        self._new_access_token = new_access_token
        self._new_refresh_token = new_refresh_token

    @property
    def name(self) -> str:
        return self._name

    @property
    def requires_pkce(self) -> bool:
        return self._requires_pkce

    def get_authorization_url(self, state: str, code_challenge: str = None) -> str:
        return f"https://mock.example.com/auth?state={state}"

    async def exchange_code(
        self, code: str, redirect_uri: str, code_verifier: str = None
    ) -> TokenExchangeResult:
        return TokenExchangeResult(
            access_token="mock_exchanged_access_token",
            expires_in=3600,
            refresh_token="mock_exchanged_refresh_token",
            provider_user_id="mock_provider_user_123",
            account_name="Mock Account",
            scopes="read,write"
        )

    async def refresh_token(self, refresh_token: str) -> TokenExchangeResult:
        if not self._refresh_succeeds:
            raise SocialMediaAPIError(
                message="Token refresh failed.",
                error_code="OAUTH_REFRESH_FAILED",
                retryable=False,
                metadata={"platform": self._name}
            )
        return TokenExchangeResult(
            access_token=self._new_access_token,
            expires_in=3600,
            refresh_token=self._new_refresh_token,
        )


def register_mock_providers(platforms=None):
    """Register mock OAuth providers for testing."""
    platforms = platforms or ["linkedin", "facebook", "instagram", "twitter"]
    for platform in platforms:
        TokenManager.register_provider(MockOAuthProvider(name=platform))


def mock_valid_token(token: str = "mock_valid_access_token"):
    """Returns a patch context manager that makes TokenManager always return a valid token."""
    return patch(
        "app.core.oauth.manager.TokenManager.get_valid_access_token",
        new_callable=AsyncMock,
        return_value=token,
    )


def mock_token_refresh_failure():
    """Returns a patch that simulates token refresh failure."""
    async def _fail(*args, **kwargs):
        raise SocialMediaAPIError(
            message="Token refresh failed.",
            error_code="OAUTH_REAUTH_REQUIRED",
            retryable=False,
            user_message="Please reconnect your account.",
            metadata={"platform": "mock"}
        )
    return patch(
        "app.core.oauth.manager.TokenManager.get_valid_access_token",
        side_effect=_fail,
    )


def mock_not_connected():
    """Returns a patch that simulates no OAuth connection existing."""
    async def _not_connected(*args, **kwargs):
        raise SocialMediaAPIError(
            message="Account not connected.",
            error_code="INTEGRATION_NOT_CONNECTED",
            retryable=False,
            metadata={"platform": "mock"}
        )
    return patch(
        "app.core.oauth.manager.TokenManager.get_valid_access_token",
        side_effect=_not_connected,
    )
