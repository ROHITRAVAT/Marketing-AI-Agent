from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AnalyticsProvider(ABC):
    """Abstract base class for social media analytics providers."""

    @abstractmethod
    async def get_post_metrics(
        self,
        post_id: str,
        access_token: str,
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch metrics for a specific post.
        
        Args:
            post_id: The platform-specific ID of the post.
            access_token: A valid OAuth access token for the platform.
            account_id: The platform-specific account/page ID (required for some platforms like Facebook/Instagram).
            
        Returns:
            A dictionary containing normalized metrics (impressions, engagement, etc.)
            and a 'provider_metrics' key containing the raw payload.
        """
        pass

    @abstractmethod
    async def get_account_metrics(
        self,
        account_id: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Fetch metrics for an account/page (e.g. followers).
        
        Args:
            account_id: The platform-specific account/page ID.
            access_token: A valid OAuth access token for the platform.
            
        Returns:
            A dictionary containing normalized metrics (followers, etc.)
            and a 'provider_metrics' key containing the raw payload.
        """
        pass
