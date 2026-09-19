"""
Instagram publishing integration tests.
Tests the two-step media container → publish flow specific to Instagram.
Covers requirement §17.
"""
import pytest
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.instagram_service import InstagramService
from app.core.errors import SocialMediaAPIError
from app.core.oauth.encryption import OAuthEncryption
from app.models.integration import IntegrationConnection
from tests.mocks.social_providers import MockHTTPResponse

pytestmark = [pytest.mark.asyncio, pytest.mark.integration, pytest.mark.publishing]


async def _seed_instagram_account(db: AsyncSession, user_id: int = 1):
    """Seed a selected Instagram business account."""
    ig = IntegrationConnection(
        user_id=user_id,
        provider="instagram_account",
        access_token=OAuthEncryption.encrypt("mock_ig_page_token"),
        provider_user_id="ig_biz_123",
        account_name="test_ig_account",
        scopes="selected",
    )
    db.add(ig)
    await db.commit()
    return ig


async def test_instagram_publish_success(seeded_db_session: AsyncSession):
    """Instagram two-step flow: create container → publish → returns media ID."""
    await _seed_instagram_account(seeded_db_session)

    container_resp = MockHTTPResponse(200, {"id": "container_456"})
    publish_resp = MockHTTPResponse(200, {"id": "ig_media_789"})

    call_count = 0

    async def mock_post_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return container_resp
        return publish_resp

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="valid_token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, side_effect=mock_post_side_effect):
        post_id = await InstagramService.publish_post(
            user_id=1, image_url="https://example.com/image.jpg",
            caption="Test IG post", db=seeded_db_session
        )

    assert post_id == "ig_media_789"
    assert call_count == 2  # Container + publish


async def test_instagram_no_account_selected(seeded_db_session: AsyncSession):
    """No Instagram account selected → INSTAGRAM_ACCOUNT_NOT_SELECTED."""
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="valid_token"):
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await InstagramService.publish_post(
                user_id=1, image_url="https://example.com/img.jpg",
                caption="Test", db=seeded_db_session
            )
    assert exc_info.value.error_code == "INSTAGRAM_ACCOUNT_NOT_SELECTED"


async def test_instagram_container_creation_auth_error(seeded_db_session: AsyncSession):
    """401 during container creation → auth error."""
    await _seed_instagram_account(seeded_db_session)
    mock_response = MockHTTPResponse(401, {}, "Invalid token")

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="bad_token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await InstagramService.publish_post(
                user_id=1, image_url="https://example.com/img.jpg",
                caption="Test", db=seeded_db_session
            )

    assert exc_info.value.error_code == "INSTAGRAM_AUTH_ERROR"


async def test_instagram_publish_step_fails(seeded_db_session: AsyncSession):
    """Container succeeds but publish step fails → INSTAGRAM_API_ERROR."""
    await _seed_instagram_account(seeded_db_session)

    container_resp = MockHTTPResponse(200, {"id": "container_123"})
    publish_resp = MockHTTPResponse(400, {}, "Bad request")

    call_count = 0

    async def mock_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return container_resp
        return publish_resp

    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token",
               new_callable=AsyncMock, return_value="token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, side_effect=mock_post):
        with pytest.raises(SocialMediaAPIError) as exc_info:
            await InstagramService.publish_post(
                user_id=1, image_url="https://example.com/img.jpg",
                caption="Test", db=seeded_db_session
            )

    assert exc_info.value.error_code == "INSTAGRAM_API_ERROR"
