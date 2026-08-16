import asyncio

from sqlalchemy import select

from app.core.security import hash_password
from app.database.session import SessionLocal
from app.models.user import User, UserRole


async def create_test_users():
    async with SessionLocal() as db:

        test_users = [
            {
                "email": "rbac-manager@example.com",
                "username": "rbac_manager",
                "full_name": "RBAC Manager",
                "role": UserRole.MANAGER,
            },
            {
                "email": "rbac-admin@example.com",
                "username": "rbac_admin",
                "full_name": "RBAC Admin",
                "role": UserRole.ADMIN,
            },
        ]

        for data in test_users:
            result = await db.execute(
                select(User).where(User.email == data["email"])
            )

            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(
                    f"Already exists: "
                    f"{existing_user.email} "
                    f"(ID={existing_user.id}, role={existing_user.role})"
                )
                continue

            user = User(
                email=data["email"],
                username=data["username"],
                full_name=data["full_name"],
                hashed_password=hash_password("StrongPass123"),
                role=data["role"],
                is_active=True,
                is_superuser=(data["role"] == UserRole.ADMIN),
            )

            db.add(user)

        await db.commit()

        result = await db.execute(
            select(User).where(
                User.email.in_([
            "auth-test@example.com",
            "rbac-manager@example.com",
            "rbac-admin@example.com",
                ])
            )
        )

        users = result.scalars().all()

        for user in users:
            print(
                f"ID={user.id} | "
                f"email={user.email} | "
                f"role={user.role} | "
                f"is_superuser={user.is_superuser}"
            )

        print("RBAC test users created/verified successfully.")


if __name__ == "__main__":
    asyncio.run(create_test_users())