import asyncio

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.user import User


async def main():
    async with SessionLocal() as db:

        # Active test user
        result = await db.execute(
            select(User).where(
                User.email == "auth-test@example.com"
            )
        )

        active_user = result.scalar_one_or_none()

        if active_user is None:
            active_user = User(
                email="auth-test@example.com",
                username="auth_test",
                hashed_password="test-hash",
                full_name="Auth Test User",
                role="user",
                is_active=True,
                is_superuser=False,
            )

            db.add(active_user)
            print("Created auth-test@example.com")
        else:
            active_user.is_active = True
            print("auth-test@example.com already exists")

        # Inactive test user
        result = await db.execute(
            select(User).where(
                User.email == "inactive-test@example.com"
            )
        )

        inactive_user = result.scalar_one_or_none()

        if inactive_user is None:
            inactive_user = User(
                email="inactive-test@example.com",
                username="inactive_test",
                hashed_password="test-hash",
                full_name="Inactive Test User",
                role="user",
                is_active=False,
                is_superuser=False,
            )

            db.add(inactive_user)
            print("Created inactive-test@example.com")
        else:
            inactive_user.is_active = False
            print("inactive-test@example.com already exists")

        await db.commit()

        print("Test users ready.")


if __name__ == "__main__":
    asyncio.run(main())