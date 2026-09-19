import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_db_session
from app.database.base import Base
from app.main import app
from app.models import User


# In-memory SQLite for fast, isolated API testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine):
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        # Create a default user for tests
        user = User(id=1, email="testuser@example.com", username="testuser", hashed_password="pw")
        session.add(user)
        await session.commit()
        yield session


from app.api.deps import get_db_session, get_current_user

@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    async def _get_test_db():
        yield db_session

    async def _get_test_user():
        return User(id=1, email="testuser@example.com", username="testuser", hashed_password="pw")

    app.dependency_overrides[get_db_session] = _get_test_db
    app.dependency_overrides[get_current_user] = _get_test_user
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_campaign_success(async_client: AsyncClient):
    payload = {
        "user_id": 1,
        "name": "Summer Launch 2026",
        "description": "Promotional launch for new AI marketing products",
        "status": "draft",
        "target_audience": "Tech startups and marketers",
        "budget": 5000.0,
        "start_date": "2026-06-01T00:00:00Z",
        "end_date": "2026-06-30T23:59:59Z",
    }
    response = await async_client.post("/api/v1/campaigns/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["status"] == "draft"
    assert data["budget"] == 5000.0
    assert data["user_id"] == 1
    assert "id" in data


@pytest.mark.asyncio
async def test_create_campaign_invalid_budget(async_client: AsyncClient):
    payload = {
        "user_id": 1,
        "name": "Invalid Budget Campaign",
        "budget": -100.0,
    }
    response = await async_client.post("/api/v1/campaigns/", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_campaign_invalid_dates(async_client: AsyncClient):
    payload = {
        "user_id": 1,
        "name": "Invalid Dates Campaign",
        "start_date": "2026-07-01T00:00:00Z",
        "end_date": "2026-06-01T00:00:00Z",  # End before start
    }
    response = await async_client.post("/api/v1/campaigns/", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_campaign_by_id(async_client: AsyncClient):
    # Create campaign first
    create_resp = await async_client.post(
        "/api/v1/campaigns/",
        json={"user_id": 1, "name": "Get Test Campaign", "status": "active"},
    )
    campaign_id = create_resp.json()["id"]

    # Fetch campaign
    get_resp = await async_client.get(f"/api/v1/campaigns/{campaign_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == campaign_id
    assert get_resp.json()["name"] == "Get Test Campaign"


@pytest.mark.asyncio
async def test_get_campaign_not_found(async_client: AsyncClient):
    response = await async_client.get("/api/v1/campaigns/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_campaigns_and_filtering(async_client: AsyncClient):
    # Seed campaigns
    await async_client.post(
        "/api/v1/campaigns/", json={"user_id": 1, "name": "Alpha Campaign", "status": "active"}
    )
    await async_client.post(
        "/api/v1/campaigns/", json={"user_id": 1, "name": "Beta Campaign", "status": "draft"}
    )
    await async_client.post(
        "/api/v1/campaigns/", json={"user_id": 1, "name": "Gamma Promo", "status": "active"}
    )

    # List all
    resp_all = await async_client.get("/api/v1/campaigns/?page=1&size=10")
    assert resp_all.status_code == 200
    all_data = resp_all.json()
    assert all_data["total"] >= 3

    # Filter by status
    resp_active = await async_client.get("/api/v1/campaigns/?status=active")
    assert resp_active.status_code == 200
    active_items = resp_active.json()["items"]
    assert all(item["status"] == "active" for item in active_items)

    # Search filter
    resp_search = await async_client.get("/api/v1/campaigns/?search=Alpha")
    assert resp_search.status_code == 200
    search_items = resp_search.json()["items"]
    assert len(search_items) == 1
    assert search_items[0]["name"] == "Alpha Campaign"


@pytest.mark.asyncio
async def test_update_campaign(async_client: AsyncClient):
    create_resp = await async_client.post(
        "/api/v1/campaigns/", json={"user_id": 1, "name": "Original Name", "status": "draft"}
    )
    cid = create_resp.json()["id"]

    # PUT full update
    put_resp = await async_client.put(
        f"/api/v1/campaigns/{cid}",
        json={"name": "Updated Name", "status": "active", "budget": 1200.0},
    )
    assert put_resp.status_code == 200
    assert put_resp.json()["name"] == "Updated Name"
    assert put_resp.json()["status"] == "active"
    assert put_resp.json()["budget"] == 1200.0

    # PATCH partial update
    patch_resp = await async_client.patch(
        f"/api/v1/campaigns/{cid}",
        json={"description": "Added description via patch"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["name"] == "Updated Name"
    assert patch_resp.json()["description"] == "Added description via patch"


@pytest.mark.asyncio
async def test_update_campaign_status(async_client: AsyncClient):
    create_resp = await async_client.post(
        "/api/v1/campaigns/", json={"user_id": 1, "name": "Status Test", "status": "draft"}
    )
    cid = create_resp.json()["id"]

    status_resp = await async_client.patch(
        f"/api/v1/campaigns/{cid}/status",
        json={"status": "completed"},
    )
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_delete_campaign(async_client: AsyncClient):
    create_resp = await async_client.post(
        "/api/v1/campaigns/", json={"user_id": 1, "name": "Delete Me", "status": "draft"}
    )
    cid = create_resp.json()["id"]

    # Delete
    del_resp = await async_client.delete(f"/api/v1/campaigns/{cid}")
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # Verify deleted
    get_resp = await async_client.get(f"/api/v1/campaigns/{cid}")
    assert get_resp.status_code == 404
