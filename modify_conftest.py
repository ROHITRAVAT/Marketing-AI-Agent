import sys

def modify_conftest():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Modify engine
    content = content.replace("from sqlalchemy.orm import sessionmaker", "from sqlalchemy.orm import sessionmaker\nfrom sqlalchemy.pool import StaticPool")
    
    old_engine = """    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )"""
    new_engine = """    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )"""
    content = content.replace(old_engine, new_engine)
    
    # Append fixtures
    fixtures = """

@pytest.fixture(autouse=True)
def mock_worker_session(test_engine):
    from unittest.mock import patch
    
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    with patch("app.scheduler.worker.AsyncSessionLocal", new=async_session):
        yield

@pytest_asyncio.fixture
async def integration_client(seeded_db_session: AsyncSession):
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    from app.api.deps import get_db_session, get_current_user

    async def _get_test_db():
        yield seeded_db_session

    async def _get_test_user():
        return await seeded_db_session.get(User, 1)

    app.dependency_overrides[get_db_session] = _get_test_db
    app.dependency_overrides[get_current_user] = _get_test_user

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_social_platforms():
    from unittest.mock import patch, AsyncMock
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \\
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
         
        # Make default returns for analytics get requests
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "likes": 10,
            "comments": 5,
            "shares": 2,
            "impressions": 100,
            "clicks": 15
        }
        
        # Default for post requests (publishing)
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"id": "mock_external_id_123"}
        
        yield {"post": mock_post, "get": mock_get}
"""
    content += fixtures

    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    modify_conftest()
