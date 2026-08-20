from datetime import datetime, timedelta, timezone
import hashlib
import secrets

import jwt
from pwdlib import PasswordHash

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)
from app.schemas.auth import TokenPayload

# Use Argon2 for secure password hashing.
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain-text password using Argon2."""

    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against an Argon2 hash."""

    return password_hash.verify(password, hashed_password)

def generate_password_reset_token() -> str:
    """Generate a cryptographically secure password reset token."""

    return secrets.token_urlsafe(32)


def hash_password_reset_token(token: str) -> str:
    """Hash a password reset token using SHA-256."""

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def create_access_token(
    user_id: int,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""

    if JWT_SECRET_KEY is None:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

def decode_access_token(token: str) -> TokenPayload:
    """Decode and validate a JWT access token."""

    if JWT_SECRET_KEY is None:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

        token_payload = TokenPayload(**payload)

        return token_payload

    except (jwt.InvalidTokenError, ValueError) as exc:
        raise ValueError("Invalid or expired access token") from exc