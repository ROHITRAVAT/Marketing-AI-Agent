from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import UserRegister


async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> User | None:
    """Find a user by email address."""

    result = await db.execute(
        select(User).where(User.email == email)
    )

    return result.scalar_one_or_none()


async def register_user(
    db: AsyncSession,
    user_data: UserRegister,
) -> User:
    """Create a new user with a securely hashed password."""

    existing_user = await get_user_by_email(
        db,
        user_data.email,
    )

    if existing_user:
        raise ValueError("Email already registered")

    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),
    )

    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user

async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    """Authenticate a user using email and password."""

    user = await get_user_by_email(db, email)

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if not user.is_active:
        return None

    return user

def create_user_access_token(user: User) -> str:
    """Create an access token for an authenticated user."""

    return create_access_token(
        user_id=user.id,
        role=user.role.value if hasattr(user.role, "value") else str(user.role),
    )