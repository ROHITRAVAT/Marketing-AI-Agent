import pytest
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from unittest.mock import patch, AsyncMock

from app.models.scheduled_post import ScheduledPost
from app.models.social_analytics import SocialAnalytics
from app.scheduler.worker import poll_and_collect_analytics

pytestmark = pytest.mark.asyncio

async def test_analytics_collection_and_idempotency(seeded_db_session: AsyncSession, mock_social_platforms, integration_client):
    # Create 4 published posts across the 4 platforms
    past_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2)
    platforms = ["linkedin", "facebook", "instagram", "twitter"]
    
    posts = []
    for i, plat in enumerate(platforms):
        p = ScheduledPost(
            user_id=1,
            platform=plat,
            content=f"{plat} test content",
            scheduled_time=past_time,
            status="published",
            published_at=past_time,
            external_post_id=f"ext_id_{plat}_{i}",
            account_id=f"urn:li:person:mock123" if plat == "linkedin" else None
        )
        posts.append(p)
        
    seeded_db_session.add_all(posts)
    await seeded_db_session.commit()
    
    # 1. Run analytics collection
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_get_token:
        mock_get_token.return_value = "mock_valid_token"
        
        await poll_and_collect_analytics()
        
    # Verify records were created for all platforms
    await seeded_db_session.commit()
    stmt = select(SocialAnalytics)
    records = (await seeded_db_session.execute(stmt)).scalars().all()
    
    assert len(records) == 4
    for record in records:
        if record.platform == "facebook":
            assert record.reach == 2000
            assert record.engagement == 150
        elif record.platform == "linkedin":
            assert record.impressions == 2000
            assert record.engagement == 32
        elif record.platform == "twitter":
            assert record.impressions == 2000
            assert record.engagement == 17
        else:
            assert record.impressions == 2000
            assert record.engagement == 150
        
    # 2. Idempotency test - run again
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_get_token:
        mock_get_token.return_value = "mock_valid_token"
        
        await poll_and_collect_analytics()
        
    # Verify no duplicate records were created
    await seeded_db_session.commit()
    count_stmt = select(func.count(SocialAnalytics.id))
    total_records = (await seeded_db_session.execute(count_stmt)).scalar()
    
    assert total_records == 4
    
    # Verify date range filtering API
    start_date = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    end_date = datetime.date.today().isoformat()

    response = await integration_client.get(
        f"/api/v1/analytics/summary?start_date={start_date}&end_date={end_date}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["overall_impressions"] == 6000  # 3 platforms * 2000 (facebook returns reach instead)
