import os
import re

def fix_dependency_overrides():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_fixture = """@pytest_asyncio.fixture
async def integration_client(test_engine, seeded_db_session):
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    from app.api.deps import get_db_session, get_current_user
    from app.models.user import User
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def _get_test_db():
        async with async_session() as session:
            yield session

    async def _get_test_user():
        async with async_session() as session:
            return await session.get(User, 1)

    app.dependency_overrides[get_db_session] = _get_test_db
    app.dependency_overrides[get_current_user] = _get_test_user

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client

    app.dependency_overrides.clear()
"""
    
    content = re.sub(
        r'@pytest_asyncio\.fixture\s*\nasync def integration_client\(seeded_db_session: AsyncSession\):.*?(?=\n\n|\Z)',
        new_fixture.strip(),
        content,
        flags=re.DOTALL
    )

    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_dependency_overrides()
