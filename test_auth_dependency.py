import asyncio

from sqlalchemy import select

from app.core.security import create_access_token, hash_password
from app.database.session import SessionLocal
from app.models.user import User


async def main():
    async with SessionLocal() as db:
        # Check whether the test user already exists.
        result = await db.execute(
            select(User).where(User.email == "auth-test@example.com")
        )

        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                email="auth-test@example.com",
                username="auth_test",
                hashed_password=hash_password("StrongPass123"),
                full_name="Authentication Test User",
                role="user",
                is_active=True,
                is_superuser=False,
            )

            db.add(user)
            await db.commit()
            await db.refresh(user)

            print(f"Test user created with ID: {user.id}")
        else:
            print(f"Test user already exists with ID: {user.id}")

        token = create_access_token(
            user_id=user.id,
            role=user.role,
        )

        print("JWT created successfully")
        print(f"Token prefix: {token[:20]}...")
        print(f"User ID: {user.id}")
        print(f"User role: {user.role}")


if __name__ == "__main__":
    asyncio.run(main())