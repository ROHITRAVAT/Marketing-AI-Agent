import asyncio

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.user import User
from app.schemas.auth import UserResponse


async def test():
    async with SessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == "api-test-2@example.com")
        )

        user = result.scalar_one()

        response = UserResponse.model_validate(user)

        print("SUCCESS: SQLAlchemy User converted to UserResponse")
        print(response)
        print(response.model_dump())


if __name__ == "__main__":
    asyncio.run(test())