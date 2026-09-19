import os
import re

def fix_test_analytics():
    with open("tests/integration/test_analytics_integration.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Change test signature to include integration_client
    content = content.replace(
        "async def test_analytics_collection_and_idempotency(seeded_db_session: AsyncSession, mock_social_platforms):",
        "async def test_analytics_collection_and_idempotency(seeded_db_session: AsyncSession, mock_social_platforms, integration_client):"
    )

    # Replace the manual client instantiation with integration_client
    manual_client_setup = """    # Verify date range filtering API
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    from app.api.deps import get_db_session, get_current_user
    from app.models.user import User

    async def _get_test_db():
        from conftest import async_session
        async with async_session() as session:
            yield session

    async def _get_test_user():
        return await seeded_db_session.get(User, 1)

    app.dependency_overrides[get_db_session] = _get_test_db
    app.dependency_overrides[get_current_user] = _get_test_user

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        start_date = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
        end_date = datetime.date.today().isoformat()

        response = await client.get(
            f"/api/v1/analytics/summary?start_date={start_date}&end_date={end_date}"
        )"""

    new_client_usage = """    # Verify date range filtering API
    start_date = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    end_date = datetime.date.today().isoformat()

    response = await integration_client.get(
        f"/api/v1/analytics/summary?start_date={start_date}&end_date={end_date}"
    )"""

    # We need to use regex since the actual content might be slightly different due to the previous replace
    content = re.sub(
        r'# Verify date range filtering API.*?response = await client\.get\(\s*f"/api/v1/analytics/summary\?start_date=\{start_date\}&end_date=\{end_date\}"\s*\)',
        new_client_usage,
        content,
        flags=re.DOTALL
    )

    with open("tests/integration/test_analytics_integration.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_test_analytics()
