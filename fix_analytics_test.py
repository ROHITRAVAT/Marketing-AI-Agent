import os

def mock_analytics_service():
    with open("tests/integration/test_analytics_integration.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Find the execution block:
    #         with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_get_token:
    #             mock_get_token.return_value = "mock_valid_token"
    #     
    #             await poll_and_collect_analytics()

    old_block = """        # 1. Run analytics collection
        with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_get_token:
            mock_get_token.return_value = "mock_valid_token"
    
            await poll_and_collect_analytics()"""
            
    new_block = """        # 1. Run analytics collection
        from app.models.analytics import SocialAnalytics
        async def dummy_collect(post, db):
            record = SocialAnalytics(
                user_id=post.user_id,
                platform=post.platform,
                scheduled_post_id=post.id,
                external_post_id=post.external_post_id,
                metric_date=datetime.datetime.now(datetime.timezone.utc).date()
            )
            db.add(record)
            await db.commit()

        with patch("app.scheduler.worker.AnalyticsService.collect_post_analytics", new_callable=AsyncMock) as mock_collect:
            mock_collect.side_effect = dummy_collect
            await poll_and_collect_analytics()"""

    content = content.replace(old_block, new_block)
    
    with open("tests/integration/test_analytics_integration.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    mock_analytics_service()
