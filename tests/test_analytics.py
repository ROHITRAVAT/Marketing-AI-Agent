import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date, timedelta, timezone

from app.main import app
from app.api.deps import get_db_session, get_current_user
from app.models.user import User
from app.models.social_analytics import SocialAnalytics

@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    async def _get_test_db():
        yield db_session
        
    async def _get_test_user():
        return User(id=1, email="test@example.com", username="test")

    app.dependency_overrides[get_db_session] = _get_test_db
    app.dependency_overrides[get_current_user] = _get_test_user
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client
        
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_analytics_summary_endpoint_empty(
    async_client: AsyncClient,
    db_session: AsyncSession,
):
    start = (date.today() - timedelta(days=30)).isoformat()
    end = date.today().isoformat()
    
    response = await async_client.get(
        f"/api/v1/analytics/summary?start_date={start}&end_date={end}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["overall_impressions"] == 0
    assert data["platforms"] == []

@pytest.mark.asyncio
async def test_analytics_summary_endpoint_with_data(
    async_client: AsyncClient,
    db_session: AsyncSession,
):
    user = User(id=1, email="test@example.com", username="test", hashed_password="pw")
    db_session.add(user)
    await db_session.commit()
    
    today = date.today()
    record1 = SocialAnalytics(
        user_id=1,
        external_post_id="ext-1",
        platform="twitter",
        metric_date=today,
        impressions=1000,
        engagement=50,
        clicks=10,
        likes=30,
        comments=10,
        shares=10,
    )
    record2 = SocialAnalytics(
        user_id=1,
        external_post_id="ext-2",
        platform="linkedin",
        metric_date=today,
        impressions=2000,
        engagement=100,
        clicks=20,
        likes=60,
        comments=20,
        shares=20,
    )
    db_session.add_all([record1, record2])
    await db_session.commit()

    start = (today - timedelta(days=5)).isoformat()
    end = today.isoformat()
    
    response = await async_client.get(
        f"/api/v1/analytics/summary?start_date={start}&end_date={end}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["overall_impressions"] == 3000
    assert data["overall_engagement"] == 150
    assert len(data["platforms"]) == 2
    
    # Check platform filtering
    response_tw = await async_client.get(
        f"/api/v1/analytics/summary?start_date={start}&end_date={end}&platforms=twitter"
    )
    assert response_tw.status_code == 200
    assert len(response_tw.json()["platforms"]) == 1
    assert response_tw.json()["platforms"][0]["platform"] == "twitter"
    assert response_tw.json()["overall_impressions"] == 1000
