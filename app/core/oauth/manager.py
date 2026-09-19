import uuid
import logging
import secrets
import hashlib
import base64
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional, Dict, Any, Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete

from app.models.integration import IntegrationConnection
from app.core.errors import SocialMediaAPIError
from app.core.oauth.provider import OAuthProvider, TokenExchangeResult
from app.core.oauth.encryption import OAuthEncryption

logger = logging.getLogger(__name__)

class TokenManager:
    """
    Centralized Token Manager for all OAuth platforms.
    Handles CSRF state generation, PKCE verification, token storage, encryption,
    and automatic token refresh.
    """
    
    # Registry of providers
    _providers: Dict[str, OAuthProvider] = {}
    
    # Simple in-memory locking for concurrent refresh protection per user_provider combo
    _refresh_locks: Dict[str, asyncio.Lock] = {}

    @classmethod
    def register_provider(cls, provider: OAuthProvider):
        cls._providers[provider.name] = provider

    @classmethod
    def get_provider(cls, name: str) -> OAuthProvider:
        provider = cls._providers.get(name)
        if not provider:
            raise ValueError(f"OAuth provider '{name}' is not registered.")
        return provider

    @classmethod
    def _generate_pkce(cls) -> Tuple[str, str]:
        """Generates PKCE code_verifier and code_challenge."""
        code_verifier = secrets.token_urlsafe(64)
        hashed = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = base64.urlsafe_b64encode(hashed).decode("utf-8").rstrip("=")
        return code_verifier, code_challenge
        
    @classmethod
    def _get_refresh_lock(cls, key: str) -> asyncio.Lock:
        if key not in cls._refresh_locks:
            cls._refresh_locks[key] = asyncio.Lock()
        return cls._refresh_locks[key]

    @classmethod
    async def generate_auth_url(cls, user_id: int, provider_name: str, db: AsyncSession) -> Tuple[str, str]:
        """
        Generates OAuth URL with state protection.
        If PKCE is required, stores the code_verifier temporarily.
        """
        provider = cls.get_provider(provider_name)
        
        # Unique state tied to user
        state = f"{provider_name}_user_{user_id}_{uuid.uuid4().hex}"
        
        code_challenge = None
        code_verifier = None
        
        if provider.requires_pkce:
            code_verifier, code_challenge = cls._generate_pkce()
            
            # Persist the verifier securely and temporarily (expires in 15 mins)
            pkce_conn = IntegrationConnection(
                user_id=user_id,
                provider=f"{provider_name}_pkce",
                provider_user_id=state,
                access_token=OAuthEncryption.encrypt(code_verifier),
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=15)
            )
            db.add(pkce_conn)
            await db.commit()
            
        url = provider.get_authorization_url(state=state, code_challenge=code_challenge)
        return url, state

    @classmethod
    async def handle_callback(
        cls, 
        state: str, 
        code: str, 
        provider_name: str, 
        redirect_uri: str,
        db: AsyncSession
    ) -> IntegrationConnection:
        """
        Handles the OAuth callback, validates state, checks PKCE, exchanges token,
        encrypts it, and saves it.
        """
        # 1. State validation (must match "{provider_name}_user_{user_id}_{uuid}")
        if not state.startswith(f"{provider_name}_user_"):
            raise SocialMediaAPIError(
                message="Invalid OAuth state parameter.",
                error_code="OAUTH_STATE_INVALID",
                retryable=False,
                metadata={"platform": provider_name}
            )
            
        try:
            parts = state.split("_")
            user_id = int(parts[2])
        except (IndexError, ValueError):
            raise SocialMediaAPIError(
                message="Malformed OAuth state parameter.",
                error_code="OAUTH_STATE_INVALID",
                retryable=False,
                metadata={"platform": provider_name}
            )

        provider = cls.get_provider(provider_name)
        code_verifier = None

        # 2. PKCE verification
        if provider.requires_pkce:
            result = await db.execute(
                select(IntegrationConnection).where(
                    and_(
                        IntegrationConnection.user_id == user_id,
                        IntegrationConnection.provider == f"{provider_name}_pkce",
                        IntegrationConnection.provider_user_id == state
                    )
                )
            )
            pkce_conn = result.scalar_one_or_none()
            
            if not pkce_conn or not pkce_conn.access_token:
                raise SocialMediaAPIError(
                    message="Invalid or expired OAuth state/PKCE verifier.",
                    error_code="OAUTH_STATE_INVALID",
                    retryable=False,
                    metadata={"platform": provider_name}
                )
                
            code_verifier = OAuthEncryption.decrypt(pkce_conn.access_token)
            
            # Consume (delete) the PKCE record so state cannot be reused
            await db.delete(pkce_conn)
            await db.commit()

        # 3. Exchange Token via Provider
        try:
            exchange_result = await provider.exchange_code(
                code=code, 
                redirect_uri=redirect_uri,
                code_verifier=code_verifier
            )
        except Exception as e:
            logger.error(f"Failed to exchange code for {provider_name}: {str(e)}")
            raise SocialMediaAPIError(
                message=f"Failed to exchange {provider_name} authorization code.",
                error_code="OAUTH_TOKEN_EXCHANGE_FAILED",
                retryable=False,
                user_message=f"We couldn't connect your {provider_name.capitalize()} account. Please try again.",
                metadata={"platform": provider_name}
            )

        # 4. Save to Database
        # Clean up any existing connection for this provider and user
        await db.execute(
            delete(IntegrationConnection).where(
                and_(
                    IntegrationConnection.user_id == user_id,
                    IntegrationConnection.provider == provider_name
                )
            )
        )
        
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=exchange_result.expires_in)
        
        conn = IntegrationConnection(
            user_id=user_id,
            provider=provider_name,
            provider_user_id=exchange_result.provider_user_id,
            account_name=exchange_result.account_name,
            access_token=OAuthEncryption.encrypt(exchange_result.access_token),
            refresh_token=OAuthEncryption.encrypt(exchange_result.refresh_token) if exchange_result.refresh_token else None,
            expires_at=expires_at,
            scopes=exchange_result.scopes
        )
        db.add(conn)
        await db.commit()
        await db.refresh(conn)
        
        return conn

    @classmethod
    async def get_valid_access_token(cls, user_id: int, provider_name: str, db: AsyncSession) -> str:
        """
        Retrieves a valid access token for the given user and provider.
        Automatically refreshes if expired (with a 5 min safety buffer).
        Handles concurrency to prevent multiple simultaneous refreshes.
        Returns the decrypted access token.
        Raises SocialMediaAPIError if not connected or reauth required.
        """
        # Ensure UTC timezone awareness for comparison
        now = datetime.now(timezone.utc)
        
        def _get_conn():
            return select(IntegrationConnection).where(
                and_(
                    IntegrationConnection.user_id == user_id,
                    IntegrationConnection.provider == provider_name
                )
            )
            
        result = await db.execute(_get_conn())
        conn = result.scalar_one_or_none()
        
        if not conn:
            raise SocialMediaAPIError(
                message=f"{provider_name.capitalize()} account not connected.",
                error_code="INTEGRATION_NOT_CONNECTED",
                retryable=False,
                user_message=f"Please connect your {provider_name.capitalize()} account.",
                metadata={"platform": provider_name}
            )
            
        # Optional naive timezone fallback to avoid comparison errors
        expires_at = conn.expires_at
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        # Check if expired or expiring within 5 minutes
        if expires_at and expires_at < (now + timedelta(minutes=5)):
            lock_key = f"{provider_name}_{user_id}"
            lock = cls._get_refresh_lock(lock_key)
            
            async with lock:
                # Re-fetch after acquiring lock to check if another request already refreshed it
                result = await db.execute(_get_conn())
                conn = result.scalar_one_or_none()
                
                expires_at = conn.expires_at
                if expires_at and expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                    
                if expires_at and expires_at < (now + timedelta(minutes=5)):
                    # Needs refresh
                    decrypted_refresh = OAuthEncryption.decrypt(conn.refresh_token) if conn.refresh_token else None
                    if not decrypted_refresh:
                        raise SocialMediaAPIError(
                            message=f"{provider_name.capitalize()} token expired and no refresh token available.",
                            error_code="OAUTH_REAUTH_REQUIRED",
                            retryable=False,
                            user_message=f"Your {provider_name.capitalize()} connection expired. Please reconnect.",
                            metadata={"platform": provider_name}
                        )
                        
                    provider = cls.get_provider(provider_name)
                    try:
                        refresh_result = await provider.refresh_token(decrypted_refresh)
                        
                        # Update connection
                        conn.access_token = OAuthEncryption.encrypt(refresh_result.access_token)
                        if refresh_result.refresh_token:
                            conn.refresh_token = OAuthEncryption.encrypt(refresh_result.refresh_token)
                        
                        conn.expires_at = datetime.now(timezone.utc) + timedelta(seconds=refresh_result.expires_in)
                        
                        # Handle plaintext legacy token upgrades: 
                        # During refresh, we already replaced them with encrypted ones above.
                        # For existing legacy tokens that haven't been refreshed, they get decrypted normally.
                        
                        db.add(conn)
                        await db.commit()
                        await db.refresh(conn)
                        
                    except Exception as e:
                        logger.error(f"Failed to refresh token for {provider_name}, user {user_id}: {str(e)}")
                        raise SocialMediaAPIError(
                            message=f"Failed to refresh {provider_name} token.",
                            error_code="OAUTH_REAUTH_REQUIRED",
                            retryable=False,
                            user_message=f"Your {provider_name.capitalize()} session expired. Please reconnect.",
                            metadata={"platform": provider_name}
                        )

        # Token should be valid now. Return decrypted.
        return OAuthEncryption.decrypt(conn.access_token)

    @classmethod
    async def get_connection_status(cls, user_id: int, provider_name: str, db: AsyncSession) -> Optional[IntegrationConnection]:
        """Returns the connection status and metadata without decrypting tokens."""
        result = await db.execute(
            select(IntegrationConnection).where(
                and_(
                    IntegrationConnection.user_id == user_id,
                    IntegrationConnection.provider == provider_name
                )
            )
        )
        return result.scalar_one_or_none()

    @classmethod
    async def disconnect(cls, user_id: int, provider_name: str, db: AsyncSession) -> bool:
        """Removes the OAuth connection for the user."""
        result = await db.execute(
            delete(IntegrationConnection).where(
                and_(
                    IntegrationConnection.user_id == user_id,
                    IntegrationConnection.provider == provider_name
                )
            )
        )
        await db.commit()
        return result.rowcount > 0
