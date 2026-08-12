import asyncio

from sqlalchemy import text

from app.database.connection import engine


async def test_connection():
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            print("PostgreSQL connection successful:", result.scalar_one())
    except Exception as exc:
        print("PostgreSQL connection failed:", exc)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_connection())