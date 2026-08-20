import asyncio

from sqlalchemy import text
from app.database.session import engine


async def main():
    async with engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """)
        )

        tables = [row[0] for row in result]

        print("Database:", engine.url.database)
        print("Tables:")
        for table in tables:
            print(" -", table)


asyncio.run(main())