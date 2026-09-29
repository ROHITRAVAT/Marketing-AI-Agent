import asyncio
from sqlalchemy import select
from app.database.connection import AsyncSessionLocal
from app.models.integration import IntegrationConnection

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(IntegrationConnection))
        integrations = res.scalars().all()
        for i in integrations:
            print(f"Provider: {i.provider}, User: {i.user_id}, Token (len): {len(i.access_token) if i.access_token else 0}, URN: {i.provider_user_id}")

if __name__ == "__main__":
    asyncio.run(main())
