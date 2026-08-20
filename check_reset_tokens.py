import asyncio

from sqlalchemy import func, select

from app.database.session import SessionLocal
from app.models.password_reset_token import PasswordResetToken


async def main() -> None:
    async with SessionLocal() as db:
        result = await db.execute(
            select(func.count(PasswordResetToken.id))
        )

        count = result.scalar_one()

        print("Password reset token records:", count)


if __name__ == "__main__":
    asyncio.run(main())