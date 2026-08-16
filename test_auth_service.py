import asyncio

from app.core.security import decode_access_token
from app.database.session import SessionLocal
from app.services.auth_service import (
    authenticate_user,
    create_user_access_token,
)


async def test_authentication():
    async with SessionLocal() as db:

        # Test successful authentication
        user = await authenticate_user(
            db,
            "auth-test@example.com",
            "StrongPass123",
        )

        if user is None:
            print("FAIL: Valid credentials were rejected")
            return

        print("SUCCESS: User authenticated")
        print(f"User ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")

        # Create JWT
        token = create_user_access_token(user)

        print("SUCCESS: Access token created")
        print(f"Token prefix: {token[:20]}...")

        # Verify JWT
        payload = decode_access_token(token)

        print("SUCCESS: Access token decoded")
        print(f"Token user ID: {payload.sub}")
        print(f"Token role: {payload.role}")

        # Test incorrect password
        invalid_user = await authenticate_user(
            db,
            "auth-test@example.com",
            "WrongPassword123",
        )

        if invalid_user is None:
            print("SUCCESS: Incorrect password rejected")
        else:
            print("FAIL: Incorrect password was accepted")


if __name__ == "__main__":
    asyncio.run(test_authentication())