"""
Realistic mock responses for social media provider APIs.
Matches real provider response structures for LinkedIn, Facebook, Instagram, and X/Twitter.
Supports configurable error modes (timeout, rate limit, 4xx, 5xx).
"""
from unittest.mock import MagicMock, AsyncMock
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import httpx


@dataclass
class MockProviderConfig:
    """Controls the behavior of a mocked provider API."""
    status_code: int = 200
    response_data: Optional[Dict[str, Any]] = None
    error_text: str = ""
    raise_timeout: bool = False
    delay_seconds: float = 0


# ─── Realistic Response Factories ───────────────────────────────────────────

def linkedin_publish_response(post_id: str = "urn:li:share:mock123") -> Dict:
    return {"id": post_id}


def linkedin_analytics_response(
    impressions: int = 2000, likes: int = 10, comments: int = 5,
    shares: int = 2, clicks: int = 15
) -> Dict:
    return {
        "elements": [{
            "totalShareStatistics": {
                "impressionCount": impressions,
                "engagement": likes + comments + shares + clicks,
                "clickCount": clicks,
                "likeCount": likes,
                "commentCount": comments,
                "shareCount": shares
            }
        }]
    }


def facebook_publish_response(post_id: str = "page123_post456") -> Dict:
    return {"id": post_id}


def facebook_analytics_response(
    impressions: int = 2000, likes: int = 10, comments: int = 5,
    shares: int = 2, reach: int = 1500
) -> Dict:
    return {
        "data": [{
            "insights": {
                "data": [
                    {"name": "impressions", "values": [{"value": impressions}]},
                    {"name": "reach", "values": [{"value": reach}]},
                ]
            },
            "likes": {"summary": {"total_count": likes}},
            "comments": {"summary": {"total_count": comments}},
            "shares": {"count": shares}
        }]
    }


def instagram_container_response(creation_id: str = "ig_container_123") -> Dict:
    return {"id": creation_id}


def instagram_publish_response(media_id: str = "ig_media_456") -> Dict:
    return {"id": media_id}


def instagram_analytics_response(
    impressions: int = 2000, reach: int = 1500, likes: int = 10,
    comments: int = 5, shares: int = 2, saves: int = 3
) -> Dict:
    return {
        "data": [{
            "name": "impressions", "values": [{"value": impressions}]
        }, {
            "name": "reach", "values": [{"value": reach}]
        }],
        "engagement": likes + comments + shares + saves
    }


def twitter_publish_response(tweet_id: str = "tweet_789") -> Dict:
    return {"data": {"id": tweet_id}}


def twitter_analytics_response(
    impressions: int = 2000, likes: int = 10, replies: int = 5,
    retweets: int = 2, quotes: int = 1, bookmarks: int = 3
) -> Dict:
    return {
        "data": {
            "public_metrics": {
                "impression_count": impressions,
                "like_count": likes,
                "reply_count": replies,
                "retweet_count": retweets,
                "quote_count": quotes,
                "bookmark_count": bookmarks
            }
        }
    }


# ─── Error Responses ────────────────────────────────────────────────────────

def rate_limit_response() -> Dict:
    return {"error": "Rate limit exceeded", "retry_after": 60}


def auth_error_response(platform: str = "unknown") -> Dict:
    return {"error": f"{platform} authorization failed", "error_code": 401}


def server_error_response() -> Dict:
    return {"error": "Internal server error"}


def permission_error_response(platform: str = "unknown") -> Dict:
    return {"error": f"Insufficient permissions for {platform}", "error_code": 403}


# ─── Mock HTTP Client Builder ───────────────────────────────────────────────

class MockHTTPResponse:
    """Mimics httpx.Response for testing."""
    def __init__(self, status_code: int, json_data: Dict = None, text: str = ""):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text or str(json_data)

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=MagicMock(),
                response=self
            )


def build_platform_mock(
    platform: str,
    publish_config: Optional[MockProviderConfig] = None,
    analytics_config: Optional[MockProviderConfig] = None,
):
    """
    Build a comprehensive mock for a specific platform's HTTP interactions.
    Returns a dict with 'post' and 'get' mock callables.
    """
    pub = publish_config or MockProviderConfig()
    ana = analytics_config or MockProviderConfig()

    # Default responses based on platform
    default_publish = {
        "linkedin": linkedin_publish_response,
        "facebook": facebook_publish_response,
        "instagram": instagram_publish_response,
        "twitter": twitter_publish_response,
    }
    default_analytics = {
        "linkedin": linkedin_analytics_response,
        "facebook": facebook_analytics_response,
        "instagram": instagram_analytics_response,
        "twitter": twitter_analytics_response,
    }

    async def mock_post(*args, **kwargs):
        if pub.raise_timeout:
            raise httpx.TimeoutException("Connection timed out")
        data = pub.response_data or default_publish.get(platform, lambda: {"id": "mock_id"})()
        return MockHTTPResponse(pub.status_code, data, pub.error_text)

    async def mock_get(*args, **kwargs):
        if ana.raise_timeout:
            raise httpx.TimeoutException("Connection timed out")
        data = ana.response_data or default_analytics.get(platform, lambda: {})()
        return MockHTTPResponse(ana.status_code, data, ana.error_text)

    return {"post": mock_post, "get": mock_get}
