import asyncio

from sqlalchemy import text

from app.database.session import SessionLocal


async def main():
    async with SessionLocal() as db:
        result = await db.execute(
            text("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """)
        )

        tables = [row[0] for row in result.fetchall()]

        print("PostgreSQL tables:")
        for table in tables:
            print("-", table)


if __name__ == "__main__":
    asyncio.run(main())