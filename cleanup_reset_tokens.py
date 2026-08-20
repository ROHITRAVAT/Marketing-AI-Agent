import asyncio

from sqlalchemy import delete

from app.database.session import SessionLocal
from app.models.password_reset_token import PasswordResetToken


async def main() -> None:
    async with SessionLocal() as db:
        result = await db.execute(
            delete(PasswordResetToken)
        )

        await db.commit()

        print(
            "Deleted password reset token records:",
            result.rowcount,
        )


if __name__ == "__main__":
    asyncio.run(main())