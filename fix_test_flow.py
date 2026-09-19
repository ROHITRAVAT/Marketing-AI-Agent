import os

def fix_test_flow():
    with open("tests/integration/test_full_agent_flow.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_code = """
        # 4. Verify the post was published and saved as a ScheduledPost for analytics
        scheduled_posts_response = await integration_client.get("/api/v1/scheduled-posts/")
        assert scheduled_posts_response.status_code == 200
        scheduled_posts = scheduled_posts_response.json()
        assert len(scheduled_posts) > 0
        assert scheduled_posts[0]["status"] == "published"
    
        post_id = scheduled_posts[0]["id"]
    
        # Check the database to see if the post is published
        await seeded_db_session.commit() # Ensure we read fresh data
        from sqlalchemy import select
        from app.models.scheduled_post import ScheduledPost
        stmt = select(ScheduledPost).where(ScheduledPost.id == post_id)
        post_db = (await seeded_db_session.execute(stmt)).scalar_one()
        assert post_db.status == "published"
        assert post_db.external_post_id == "mock_external_id_123"
        
        # 5. Run Analytics Collection
"""
    
    import re
    pattern = re.compile(r'        # 4\. Verify the post was scheduled.*?        # 6\. Run Analytics Collection', re.DOTALL)
    
    content = pattern.sub(new_code.strip() + "\n", content)
    
    with open("tests/integration/test_full_agent_flow.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_test_flow()
