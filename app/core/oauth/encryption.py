import logging
from cryptography.fernet import Fernet, InvalidToken
from app.core.config import OAUTH_ENCRYPTION_KEY

logger = logging.getLogger(__name__)

class OAuthEncryption:
    """
    Utility for encrypting and decrypting OAuth tokens at rest using Fernet symmetric encryption.
    It transparently handles legacy plaintext tokens for seamless migration.
    """
    
    _fernet = None

    @classmethod
    def _get_fernet(cls) -> Fernet:
        if cls._fernet is None:
            if not OAUTH_ENCRYPTION_KEY:
                # In development, if key is missing, dynamically generate one for the session.
                # Tokens will be invalidated upon server restart!
                logger.warning("OAUTH_ENCRYPTION_KEY not set. Generating an ephemeral key. Tokens will not persist across restarts.")
                key = Fernet.generate_key()
                cls._fernet = Fernet(key)
            else:
                try:
                    cls._fernet = Fernet(OAUTH_ENCRYPTION_KEY.encode())
                except Exception as e:
                    logger.critical(f"Failed to initialize Fernet with provided OAUTH_ENCRYPTION_KEY. It must be 32 url-safe base64-encoded bytes. Error: {e}")
                    raise
        return cls._fernet

    @classmethod
    def encrypt(cls, token: str) -> str:
        """Encrypts a plaintext token."""
        if not token:
            return token
        f = cls._get_fernet()
        return f.encrypt(token.encode()).decode()

    @classmethod
    def decrypt(cls, token: str) -> str:
        """
        Decrypts an encrypted token.
        If decryption fails with InvalidToken, it assumes it's a legacy plaintext token
        and returns it as-is for backwards compatibility.
        """
        if not token:
            return token
            
        f = cls._get_fernet()
        try:
            return f.decrypt(token.encode()).decode()
        except InvalidToken:
            # Token is either corrupted, encrypted with a different key, or plaintext.
            # For backwards compatibility during migration, we assume it's plaintext.
            return token
