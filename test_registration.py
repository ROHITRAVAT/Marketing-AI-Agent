import asyncio

from sqlalchemy import select

from app.core.security import verify_password
from app.database.session import SessionLocal
from app.models.user import User, UserRole
from app.schemas.auth import UserRegister
from app.services.auth_service import register_user


TEST_EMAIL = "registration-test@example.com"


async def test_registration():
    async with SessionLocal() as db:

        # Clean up a previous test user if it exists.
        result = await db.execute(
            select(User).where(User.email == TEST_EMAIL)
        )

        existing_user = result.scalar_one_or_none()

        if existing_user:
            await db.delete(existing_user)
            await db.commit()

        # Test successful registration.
        user_data = UserRegister(
            email=TEST_EMAIL,
            username="registration_test",
            full_name="Registration Test",
            password="StrongPass123",
        )

        user = await register_user(db, user_data)

        print("SUCCESS: User registered")
        print(f"User ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Active: {user.is_active}")

        # Verify default role.
        if user.role == UserRole.USER:
            print("SUCCESS: Default role is user")
        else:
            print(f"FAIL: Unexpected role: {user.role}")

        # Verify password is hashed.
        if user.hashed_password != user_data.password:
            print("SUCCESS: Password is not stored as plaintext")
        else:
            print("FAIL: Password appears to be stored as plaintext")

        # Verify the stored hash can validate the original password.
        if verify_password(
            user_data.password,
            user.hashed_password,
        ):
            print("SUCCESS: Stored password hash verifies correctly")
        else:
            print("FAIL: Password hash verification failed")

        # Test duplicate email.
        try:
            await register_user(db, user_data)
        except ValueError as exc:
            print(f"SUCCESS: Duplicate registration rejected: {exc}")
        else:
            print("FAIL: Duplicate registration was accepted")


if __name__ == "__main__":
    asyncio.run(test_registration())