"""Tests for password reset service."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.core.security import (
    hash_password_reset_token,
    verify_password,
)
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.services.password_reset_service import (
    request_password_reset,
    reset_password,
    validate_password_reset_token,
)


@pytest.mark.asyncio
async def test_request_password_reset_creates_token(seeded_db_session):
    """An active user should receive a password reset token."""

    db = seeded_db_session

    raw_token = await request_password_reset(
        db,
        "auth-test@example.com",
    )

    assert raw_token is not None
    assert len(raw_token) > 0

    result = await db.execute(
        select(PasswordResetToken)
        .where(PasswordResetToken.user_id == 1)
        .order_by(PasswordResetToken.id.desc())
    )

    reset_token = result.scalars().first()

    assert reset_token is not None
    assert reset_token.token_hash is not None
    assert len(reset_token.token_hash) == 64
    assert reset_token.used_at is None
    assert reset_token.revoked_at is None
    assert reset_token.expires_at is not None


@pytest.mark.asyncio
async def test_request_password_reset_unknown_email(seeded_db_session):
    """An unknown email should not create a password reset token."""

    db = seeded_db_session

    raw_token = await request_password_reset(
        db,
        "does-not-exist@example.com",
    )

    assert raw_token is None


@pytest.mark.asyncio
async def test_request_password_reset_inactive_user(seeded_db_session):
    """An inactive user should not receive a password reset token."""

    db = seeded_db_session

    result = await db.execute(
        select(User).where(
            User.email == "inactive-test@example.com"
        )
    )

    user = result.scalar_one_or_none()

    assert user is not None
    assert user.is_active is False

    raw_token = await request_password_reset(
        db,
        user.email,
    )

    assert raw_token is None


@pytest.mark.asyncio
async def test_request_password_reset_revokes_previous_token(seeded_db_session):
    """A new reset request should revoke the previous active token."""

    db = seeded_db_session

    first_token = await request_password_reset(
        db,
        "auth-test@example.com",
    )

    assert first_token is not None

    result = await db.execute(
        select(PasswordResetToken)
        .where(PasswordResetToken.user_id == 1)
        .order_by(PasswordResetToken.id.desc())
    )

    first_record = result.scalars().first()

    assert first_record is not None
    assert first_record.revoked_at is None

    first_record_id = first_record.id

    second_token = await request_password_reset(
        db,
        "auth-test@example.com",
    )

    assert second_token is not None
    assert second_token != first_token

    result = await db.execute(
        select(PasswordResetToken)
        .where(PasswordResetToken.user_id == 1)
        .order_by(PasswordResetToken.id.desc())
    )

    records = list(result.scalars().all())

    assert len(records) == 2

    newest_record = records[0]
    previous_record = records[1]

    assert newest_record.id != first_record_id
    assert previous_record.revoked_at is not None
    assert newest_record.revoked_at is None


@pytest.mark.asyncio
async def test_password_reset_token_is_stored_as_hash(seeded_db_session):
    """The database should store only the hashed reset token."""

    db = seeded_db_session

    raw_token = await request_password_reset(
        db,
        "auth-test@example.com",
    )

    assert raw_token is not None

    result = await db.execute(
        select(PasswordResetToken)
        .where(PasswordResetToken.user_id == 1)
        .order_by(PasswordResetToken.id.desc())
    )

    reset_token = result.scalars().first()

    assert reset_token is not None

    # Raw token must never be stored.
    assert reset_token.token_hash != raw_token

    # SHA-256 produces a 64-character hexadecimal hash.
    assert len(reset_token.token_hash) == 64

    # The stored value should contain only hexadecimal characters.
    assert all(
        character in "0123456789abcdef"
        for character in reset_token.token_hash
    )

    # Verify the stored hash matches the raw token.
    assert reset_token.token_hash == hash_password_reset_token(
        raw_token
    )


@pytest.mark.asyncio
async def test_password_reset_token_has_future_expiration(seeded_db_session):
    """A password reset token should expire in the future."""

    db = seeded_db_session

    raw_token = await request_password_reset(
        db,
        "auth-test@example.com",
    )

    assert raw_token is not None

    result = await db.execute(
        select(PasswordResetToken)
        .where(PasswordResetToken.user_id == 1)
        .order_by(PasswordResetToken.id.desc())
    )

    reset_token = result.scalars().first()

    assert reset_token is not None

    now = datetime.now(timezone.utc)

    expires_at = reset_token.expires_at

    # SQLite may return timezone-aware columns as naive datetimes.
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    assert expires_at > now


@pytest.mark.asyncio
async def test_validate_password_reset_token(seeded_db_session):
    """A valid reset token should be accepted."""

    db = seeded_db_session

    raw_token = await request_password_reset(
        db,
        "auth-test@example.com",
    )

    assert raw_token is not None

    reset_token = await validate_password_reset_token(
        db,
        raw_token,
    )

    assert reset_token is not None
    assert reset_token.used_at is None
    assert reset_token.revoked_at is None


@pytest.mark.asyncio
async def test_validate_password_reset_token_invalid(seeded_db_session):
    """An unknown token should be rejected."""

    db = seeded_db_session

    reset_token = await validate_password_reset_token(
        db,
        "invalid-reset-token",
    )

    assert reset_token is None


@pytest.mark.asyncio
async def test_validate_password_reset_token_revoked(seeded_db_session):
    """A revoked token should be rejected."""

    db = seeded_db_session

    first_token = await request_password_reset(
        db,
        "auth-test@example.com",
    )

    assert first_token is not None

    second_token = await request_password_reset(
        db,
        "auth-test@example.com",
    )

    assert second_token is not None

    result = await validate_password_reset_token(
        db,
        first_token,
    )

    assert result is None


@pytest.mark.asyncio
async def test_validate_password_reset_token_expired(seeded_db_session):
    """An expired token should be rejected."""

    db = seeded_db_session

    raw_token = await request_password_reset(
        db,
        "auth-test@example.com",
    )

    assert raw_token is not None

    token_hash = hash_password_reset_token(raw_token)

    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash
        )
    )

    reset_token = result.scalar_one()

    reset_token.expires_at = (
        datetime.now(timezone.utc) - timedelta(minutes=1)
    )

    await db.commit()

    result = await validate_password_reset_token(
        db,
        raw_token,
    )

    assert result is None


@pytest.mark.asyncio
async def test_reset_password_success(seeded_db_session):
    """A valid reset token should allow the user to change password."""

    db = seeded_db_session

    raw_token = await request_password_reset(
        db,
        "auth-test@example.com",
    )

    assert raw_token is not None

    result = await db.execute(
        select(User).where(
            User.email == "auth-test@example.com"
        )
    )

    user = result.scalar_one()

    old_hash = user.hashed_password

    success = await reset_password(
        db,
        raw_token,
        "NewStrongPassword123!",
    )

    assert success is True

    await db.refresh(user)

    assert user.hashed_password != old_hash

    assert verify_password(
        "NewStrongPassword123!",
        user.hashed_password,
    )


@pytest.mark.asyncio
async def test_reset_password_marks_token_used(seeded_db_session):
    """A successful reset should mark the token as used."""

    db = seeded_db_session

    raw_token = await request_password_reset(
        db,
        "auth-test@example.com",
    )

    assert raw_token is not None

    success = await reset_password(
        db,
        raw_token,
        "AnotherStrongPassword123!",
    )

    assert success is True

    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash
            == hash_password_reset_token(raw_token)
        )
    )

    reset_token = result.scalar_one()

    assert reset_token.used_at is not None


@pytest.mark.asyncio
async def test_reset_password_cannot_reuse_token(seeded_db_session):
    """A reset token can only be used once."""

    db = seeded_db_session

    raw_token = await request_password_reset(
        db,
        "auth-test@example.com",
    )

    assert raw_token is not None

    first_reset = await reset_password(
        db,
        raw_token,
        "FirstPassword123!",
    )

    assert first_reset is True

    second_reset = await reset_password(
        db,
        raw_token,
        "SecondPassword123!",
    )

    assert second_reset is False
