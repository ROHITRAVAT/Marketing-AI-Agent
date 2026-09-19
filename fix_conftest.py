import os

def fix_conftest():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_code = """
    from app.api.deps import get_db_session, get_current_user as deps_get_current_user
    from app.dependencies.auth import get_current_user as auth_get_current_user
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
    app.dependency_overrides[deps_get_current_user] = _get_test_user
    app.dependency_overrides[auth_get_current_user] = _get_test_user
"""
    
    old_code = """
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
"""
    
    content = content.replace(old_code.strip(), new_code.strip())
    
    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_conftest()
