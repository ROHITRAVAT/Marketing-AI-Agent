import asyncio

from sqlalchemy import text

from app.database.session import SessionLocal


async def main():
    async with SessionLocal() as db:
        result = await db.execute(
            text("SELECT current_database(), current_schema()")
        )
        print("DATABASE / SCHEMA:", result.fetchall())

        result = await db.execute(
            text("SELECT to_regclass('public.users')")
        )
        print("USERS TABLE:", result.fetchall())


asyncio.run(main())