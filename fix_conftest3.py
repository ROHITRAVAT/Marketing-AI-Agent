import os

def fix_conftest3():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_code = """
    inactive_user = User(
        id=9,
        email="inactive-test@example.com",
        username="inactive_test",
        hashed_password=hash_password("StrongPass123"),
        full_name="Inactive Test User",
        role="user",
        is_active=False,
        is_superuser=False,
    )

    from app.models.integration import IntegrationConnection
    linkedin_conn = IntegrationConnection(
        user_id=1,
        platform="linkedin",
        access_token_encrypted=b"mock",
        provider_user_id="mock_urn",
        status="connected"
    )

    await db_session.merge(active_user)
    await db_session.merge(inactive_user)
    await db_session.merge(linkedin_conn)
    await db_session.commit()
"""
    
    old_code = """
    inactive_user = User(
        id=9,
        email="inactive-test@example.com",
        username="inactive_test",
        hashed_password=hash_password("StrongPass123"),
        full_name="Inactive Test User",
        role="user",
        is_active=False,
        is_superuser=False,
    )

    await db_session.merge(active_user)
    await db_session.merge(inactive_user)
    await db_session.commit()
"""
    
    if old_code.strip() in content:
        content = content.replace(old_code.strip(), new_code.strip())
    
    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_conftest3()
