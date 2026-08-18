import asyncio

from sqlalchemy import select

from app.core.security import create_access_token
from app.database.session import SessionLocal
from app.models.user import User


TEST_EMAIL = "inactive-test@example.com"


async def test():
    async with SessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == TEST_EMAIL)
        )

        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                email=TEST_EMAIL,
                username="inactive_test",
                hashed_password="test-hash",
                full_name="Inactive Test User",
                role="user",
                is_active=True,
                is_superuser=False,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

            print(f"Created test user with ID: {user.id}")
        else:
            print(f"Using existing test user with ID: {user.id}")

        token = create_access_token(
            user_id=user.id,
            role=user.role,
        )

        print("JWT created successfully")

        user.is_active = False
        await db.commit()

        print("User deactivated successfully")
        print(f"User ID: {user.id}")
        print(f"Active: {user.is_active}")
        print(f"Token prefix: {token[:20]}...")


if __name__ == "__main__":
    asyncio.run(test())