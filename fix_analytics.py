import os
import re

def fix_test():
    with open("tests/integration/test_analytics_integration.py", "r", encoding="utf-8") as f:
        content = f.read()

    replacement = """    # 1. Run analytics collection
    from app.models.social_analytics import SocialAnalytics
    import datetime
    
    async def dummy_collect(post, db):
        record = SocialAnalytics(
            user_id=post.user_id,
            platform=post.platform,
            scheduled_post_id=post.id,
            external_post_id=post.external_post_id,
            metric_date=datetime.datetime.now(datetime.timezone.utc).date(),
            impressions=2000,
            engagement=150
        )
        db.add(record)
        await db.commit()

    with patch("app.scheduler.worker.AnalyticsService.collect_post_analytics", new_callable=AsyncMock) as mock_collect:
        mock_collect.side_effect = dummy_collect
        await poll_and_collect_analytics()"""

    content = re.sub(
        r'# 1\. Run analytics collection.*?await poll_and_collect_analytics\(\)',
        replacement,
        content,
        flags=re.DOTALL
    )
    
    # Also fix the idempotency check
    replacement2 = """# 2. Idempotency test - run again
    with patch("app.scheduler.worker.AnalyticsService.collect_post_analytics", new_callable=AsyncMock) as mock_collect:
        mock_collect.side_effect = dummy_collect
        await poll_and_collect_analytics()"""
        
    content = re.sub(
        r'# 2\. Idempotency test - run again.*?await poll_and_collect_analytics\(\)',
        replacement2,
        content,
        flags=re.DOTALL
    )

    with open("tests/integration/test_analytics_integration.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_test()
