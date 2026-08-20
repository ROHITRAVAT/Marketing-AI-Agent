import asyncio

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.password_reset_token import PasswordResetToken
from app.services.password_reset_service import request_password_reset


async def main() -> None:
    async with SessionLocal() as db:
        # Find an existing user for testing.
        result = await db.execute(
            select(PasswordResetToken.user_id).limit(1)
        )

        user_id = result.scalar_one_or_none()

        if user_id is None:
            print("No existing reset token found.")
            print("Please use an existing user ID for the test.")
            return

        # Get the user's email.
        from app.models.user import User

        result = await db.execute(
            select(User).where(User.id == user_id)
        )

        user = result.scalar_one_or_none()

        if user is None:
            print("Test user not found.")
            return

        # First password reset request.
        first_token = await request_password_reset(
            db,
            user.email,
        )

        print("First token created:", first_token is not None)

        # Find the newest reset token.
        result = await db.execute(
            select(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user.id
            )
            .order_by(
                PasswordResetToken.id.desc()
            )
        )

        first_record = result.scalars().first()

        if first_record is None:
            print("First reset record was not created.")
            return

        print(
            "First token hash stored:",
            bool(first_record.token_hash),
        )
        print(
            "First token revoked:",
            first_record.revoked_at is not None,
        )

        # Second password reset request.
        second_token = await request_password_reset(
            db,
            user.email,
        )

        print("Second token created:", second_token is not None)

        # Get the two newest records.
        result = await db.execute(
            select(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user.id
            )
            .order_by(
                PasswordResetToken.id.desc()
            )
            .limit(2)
        )

        records = list(result.scalars().all())

        if len(records) < 2:
            print("Expected two reset-token records.")
            return

        newest_token = records[0]
        previous_token = records[1]

        print(
            "Previous token revoked:",
            previous_token.revoked_at is not None,
        )
        print(
            "Newest token revoked:",
            newest_token.revoked_at is not None,
        )

        # Unknown email test.
        unknown_token = await request_password_reset(
            db,
            "does-not-exist@example.com",
        )

        print(
            "Unknown email returns None:",
            unknown_token is None,
        )


if __name__ == "__main__":
    asyncio.run(main())