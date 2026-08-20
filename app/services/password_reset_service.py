"""Password reset business logic."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
from app.core.security import (
    generate_password_reset_token,
    hash_password_reset_token,
    hash_password,
)
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User

async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> User | None:
    """Find a user by email address."""

    result = await db.execute(
        select(User).where(User.email == email)
    )

    return result.scalar_one_or_none()

async def revoke_existing_reset_tokens(
    db: AsyncSession,
    user_id: int,
) -> None:
    """Revoke all unused password reset tokens for a user."""

    await db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.revoked_at.is_(None),
        )
        .values(
            revoked_at=datetime.now(timezone.utc),
        )
    )

async def create_password_reset_token(
    db: AsyncSession,
    user_id: int,
) -> str:
    """Create and store a password reset token for a user."""

    raw_token = generate_password_reset_token()

    token_hash = hash_password_reset_token(raw_token)

    now = datetime.now(timezone.utc)

    reset_token = PasswordResetToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=now + timedelta(
            minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
        ),
    )

    db.add(reset_token)

    return raw_token

async def request_password_reset(
    db: AsyncSession,
    email: str,
) -> str | None:
    """Create a password reset token for an existing active user.

    Returns the raw reset token when a reset should be processed.
    Returns None when the user does not exist or is inactive.
    """

    user = await get_user_by_email(
        db,
        email,
    )

    if user is None or not user.is_active:
        return None

    await revoke_existing_reset_tokens(
        db,
        user.id,
    )

    raw_token = await create_password_reset_token(
        db,
        user.id,
    )

    await db.commit()

    return raw_token

async def get_valid_password_reset_token(
    db: AsyncSession,
    raw_token: str,
) -> PasswordResetToken | None:
    """Return a valid password reset token record."""

    token_hash = hash_password_reset_token(raw_token)

    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash
        )
    )

    reset_token = result.scalar_one_or_none()

    if reset_token is None:
        return None

    now = datetime.now(timezone.utc)

    if reset_token.used_at is not None:
        return None

    if reset_token.revoked_at is not None:
        return None

    expires_at = reset_token.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= now:
        return None

    return reset_token

async def reset_password(
    db: AsyncSession,
    raw_token: str,
    new_password: str,
) -> bool:
    """Reset a user's password using a valid reset token."""

    reset_token = await get_valid_password_reset_token(
        db,
        raw_token,
    )

    if reset_token is None:
        return False

    result = await db.execute(
        select(User).where(
            User.id == reset_token.user_id
        )
    )

    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        return False

    user.hashed_password = hash_password(new_password)

    reset_token.used_at = datetime.now(timezone.utc)

    await db.commit()

    return True

async def validate_password_reset_token(
    db: AsyncSession,
    raw_token: str,
) -> PasswordResetToken | None:
    """Validate a password reset token.

    Returns the token record when valid.
    Returns None when the token is:
    - unknown
    - expired
    - already used
    - revoked
    """

    token_hash = hash_password_reset_token(raw_token)

    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash
        )
    )

    reset_token = result.scalar_one_or_none()

    if reset_token is None:
        return None

    # Token has already been used.
    if reset_token.used_at is not None:
        return None

    # Token was revoked by a newer reset request.
    if reset_token.revoked_at is not None:
        return None

    # Check expiration.
    now = datetime.now(timezone.utc)

    expires_at = reset_token.expires_at

    # SQLite may return timezone-aware DateTime values
    # as naive datetimes.
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= now:
        return None

    return reset_token

    now = datetime.now(timezone.utc)

    if reset_token.used_at is not None:
        return None

    if reset_token.revoked_at is not None:
        return None

    expires_at = reset_token.expires_at

    # SQLite may return DateTime(timezone=True) values as naive datetimes.
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= now:
        return None

    return reset_token

