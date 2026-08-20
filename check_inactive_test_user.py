import asyncio

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.user import User


async def main() -> None:
    async with SessionLocal() as db:
        result = await db.execute(
            select(User).where(
                User.email == "inactive-test@example.com"
            )
        )

        user = result.scalar_one_or_none()

        if user is None:
            print("Inactive test user does not exist.")
            return

        print("User ID:", user.id)
        print("Email:", user.email)
        print("Active:", user.is_active)


if __name__ == "__main__":
    asyncio.run(main())