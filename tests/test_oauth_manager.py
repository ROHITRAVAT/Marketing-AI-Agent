import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.database.base import Base
from app.models.user import User
from app.models.integration import IntegrationConnection
from app.core.oauth.encryption import OAuthEncryption
from app.core.oauth.manager import TokenManager
from app.core.oauth.provider import OAuthProvider, TokenExchangeResult

class MockProvider(OAuthProvider):
    @property
    def name(self) -> str:
        return "mock"
        
    @property
    def requires_pkce(self) -> bool:
        return False
        
    def get_authorization_url(self, state: str, code_challenge: str = None) -> str:
        return f"https://mock.com/auth?state={state}"
        
    async def exchange_code(self, code: str, redirect_uri: str, code_verifier: str = None) -> TokenExchangeResult:
        return TokenExchangeResult(
            access_token="mock_access",
            expires_in=3600,
            refresh_token="mock_refresh",
            provider_user_id="mock123",
            account_name="Mock User",
            scopes="mock_scope"
        )
        
    async def refresh_token(self, refresh_token: str) -> TokenExchangeResult:
        return TokenExchangeResult(
            access_token="mock_access_new",
            expires_in=3600,
            refresh_token="mock_refresh_new"
        )

# SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
    async with TestingSessionLocal() as session:
        # Create a test user
        user = User(
            id=1,
            email="test@example.com",
            hashed_password="hash",
            full_name="Test User",
            is_active=True
        )
        session.add(user)
        await session.commit()
        yield session

@pytest.fixture(autouse=True)
def setup_mock_provider():
    TokenManager.register_provider(MockProvider())

@pytest.mark.asyncio
async def test_oauth_encryption():
    # Make sure we have a key
    import cryptography.fernet
    key = cryptography.fernet.Fernet.generate_key().decode()
    with patch("app.core.oauth.encryption.OAUTH_ENCRYPTION_KEY", key):
        # Force re-init
        OAuthEncryption._fernet = None
        
        token = "secret_token_123"
        encrypted = OAuthEncryption.encrypt(token)
        
        assert encrypted != token
        assert OAuthEncryption.decrypt(encrypted) == token
        
        # Legacy fallback
        assert OAuthEncryption.decrypt(token) == token

@pytest.mark.asyncio
async def test_oauth_generate_auth_url(db_session: AsyncSession):
    url, state = await TokenManager.generate_auth_url(user_id=1, provider_name="mock", db=db_session)
    
    assert "mock.com/auth" in url
    assert state.startswith("mock_user_1_")
    
@pytest.mark.asyncio
async def test_oauth_handle_callback(db_session: AsyncSession):
    _, state = await TokenManager.generate_auth_url(user_id=1, provider_name="mock", db=db_session)
    
    conn = await TokenManager.handle_callback(
        state=state,
        code="auth_code_123",
        provider_name="mock",
        redirect_uri="http://localhost",
        db=db_session
    )
    
    assert conn.provider == "mock"
    assert conn.provider_user_id == "mock123"
    assert conn.account_name == "Mock User"
    
    # Assert tokens are encrypted
    assert conn.access_token != "mock_access"
    assert OAuthEncryption.decrypt(conn.access_token) == "mock_access"
    assert OAuthEncryption.decrypt(conn.refresh_token) == "mock_refresh"

@pytest.mark.asyncio
async def test_oauth_refresh_token(db_session: AsyncSession):
    # Seed an expired connection
    conn = IntegrationConnection(
        user_id=1,
        provider="mock",
        access_token=OAuthEncryption.encrypt("old_access"),
        refresh_token=OAuthEncryption.encrypt("old_refresh"),
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        scopes="mock_scope"
    )
    db_session.add(conn)
    await db_session.commit()
    
    # Request valid token -> should trigger refresh
    new_token = await TokenManager.get_valid_access_token(1, "mock", db_session)
    
    assert new_token == "mock_access_new"
    
    # Check DB was updated
    await db_session.refresh(conn)
    assert OAuthEncryption.decrypt(conn.access_token) == "mock_access_new"
    assert OAuthEncryption.decrypt(conn.refresh_token) == "mock_refresh_new"

@pytest.mark.asyncio
async def test_oauth_disconnect(db_session: AsyncSession):
    conn = IntegrationConnection(
        user_id=1,
        provider="mock",
        access_token="...",
    )
    db_session.add(conn)
    await db_session.commit()
    
    success = await TokenManager.disconnect(1, "mock", db_session)
    assert success is True
    
    # Second time should return False
    success = await TokenManager.disconnect(1, "mock", db_session)
    assert success is False
