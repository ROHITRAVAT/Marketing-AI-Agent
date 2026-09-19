import os

def fix_scheduler_tests():
    with open("tests/integration/test_scheduler_integration.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Fix test_scheduler_past_post_published
    old_test_1 = """    post = ScheduledPost(
        user_id=1,
        platform="linkedin",
        content="Past post",
        scheduled_time=past_time,
        status="scheduled"
    )
    seeded_db_session.add(post)
    await seeded_db_session.commit()"""

    new_test_1 = """    from app.models.integration import IntegrationConnection
    # Add an integration connection so publishing doesn't fail
    conn = IntegrationConnection(
        user_id=1,
        platform="linkedin",
        access_token="mock_token",
        provider_user_id="mock_user_id",
        status="active"
    )
    seeded_db_session.add(conn)
    
    post = ScheduledPost(
        user_id=1,
        platform="linkedin",
        content="Past post",
        scheduled_time=past_time,
        status="scheduled"
    )
    seeded_db_session.add(post)
    await seeded_db_session.commit()"""

    # Fix test_scheduler_token_refresh_fails
    old_test_2 = """    post = ScheduledPost(
        user_id=1,
        platform="twitter",
        content="Token fail post",
        scheduled_time=past_time,
        status="scheduled"
    )
    seeded_db_session.add(post)
    await seeded_db_session.commit()"""

    new_test_2 = """    post = ScheduledPost(
        user_id=1,
        platform="twitter",
        content="Token fail post",
        scheduled_time=past_time,
        status="scheduled",
        attempt_count=2 # so it fails on this try
    )
    seeded_db_session.add(post)
    await seeded_db_session.commit()"""
    
    content = content.replace(old_test_1, new_test_1)
    content = content.replace(old_test_2, new_test_2)
    
    with open("tests/integration/test_scheduler_integration.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_scheduler_tests()
