import pytest
import pytest_asyncio

from sqlalchemy import select
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_db
from app.database.base import Base
from app.main import app
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.core.security import hash_password, verify_password


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


TEST_EMAIL = "api-reset-test@example.com"


@pytest.fixture
async def db_session():
    async with SessionLocal() as db:
        yield db


@pytest.fixture
async def client(db_session: AsyncSession, monkeypatch):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async def mock_send_email(email: str, reset_token: str):
        return None

    monkeypatch.setattr(
        "app.api.v1.endpoints.auth.send_password_reset_email",
        mock_send_email,
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client

    app.dependency_overrides.clear()


async def create_test_user(
    db: AsyncSession,
    email: str = TEST_EMAIL,
) -> User:
    user = User(
        email=email,
        username=email.split("@")[0],
        hashed_password=hash_password("OldPassword123!"),
        full_name="Password Reset API Test",
        role="user",
        is_active=True,
        is_superuser=False,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@pytest.mark.asyncio
async def test_forgot_password_existing_user(client, db_session):
    """Existing active users should receive a generic 202 response."""

    await create_test_user(db_session)

    response = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": TEST_EMAIL},
    )

    assert response.status_code == 202
    assert "password reset link" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_forgot_password_unknown_email(client):
    """Unknown emails should receive the same generic response."""

    response = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "unknown-api@example.com"},
    )

    assert response.status_code == 202
    assert "password reset link" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_reset_password_success(client, db_session):
    """A valid reset token should reset the password."""

    user = await create_test_user(db_session)

    response = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": TEST_EMAIL},
    )

    assert response.status_code == 202

    result = await db_session.execute(
        select(PasswordResetToken)
        .where(PasswordResetToken.user_id == user.id)
        .order_by(PasswordResetToken.id.desc())
    )

    reset_token = result.scalars().first()

    assert reset_token is not None

    # API tests need the raw token. Generate a new valid token through
    # the service rather than attempting to recover it from the database.
    from app.services.password_reset_service import (
        request_password_reset,
    )

    raw_token = await request_password_reset(
        db_session,
        TEST_EMAIL,
    )

    assert raw_token is not None

    response = await client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": raw_token,
            "new_password": "NewPassword123!",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Password reset successfully"

    await db_session.refresh(user)

    assert verify_password(
        "NewPassword123!",
        user.hashed_password,
    )


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client):
    """An invalid token should return 400."""

    response = await client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": "invalid-token",
            "new_password": "NewPassword123!",
        },
    )

    assert response.status_code == 400
    assert response.json()["message"] == (
        "Invalid or expired password reset token"
    )

@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine):
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession, monkeypatch):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async def mock_send_password_reset_email(
        email: str,
        reset_token: str,
    ):
        pass

    monkeypatch.setattr(
        "app.api.v1.endpoints.auth.send_password_reset_email",
        mock_send_password_reset_email,
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client

    app.dependency_overrides.clear()