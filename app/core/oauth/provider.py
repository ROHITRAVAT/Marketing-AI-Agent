from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

@dataclass
class TokenExchangeResult:
    access_token: str
    expires_in: int  # Seconds
    refresh_token: Optional[str] = None
    provider_user_id: Optional[str] = None
    account_name: Optional[str] = None
    scopes: Optional[str] = None

class OAuthProvider(ABC):
    """
    Abstract Base Class for all social media OAuth integrations.
    Provides standard interface for generating URLs, exchanging codes,
    refreshing tokens, and fetching basic user identities.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the provider (e.g. 'linkedin', 'facebook')."""
        pass

    @property
    def requires_pkce(self) -> bool:
        """Whether this provider requires PKCE (e.g., Twitter v2)."""
        return False

    @abstractmethod
    def get_authorization_url(self, state: str, code_challenge: Optional[str] = None) -> str:
        """
        Generates the provider's OAuth 2.0 authorization URL.
        
        Args:
            state (str): The CSRF state token.
            code_challenge (Optional[str]): The PKCE challenge, if requires_pkce is True.
            
        Returns:
            str: The authorization URL to redirect the user to.
        """
        pass

    @abstractmethod
    async def exchange_code(self, code: str, redirect_uri: str, code_verifier: Optional[str] = None) -> TokenExchangeResult:
        """
        Exchanges the authorization code for access and refresh tokens, and fetches the user identity.
        
        Args:
            code (str): The auth code returned by the provider.
            redirect_uri (str): The redirect URI used in the initial request.
            code_verifier (Optional[str]): The PKCE verifier, if requires_pkce is True.
            
        Returns:
            TokenExchangeResult: Standardized token result containing tokens and user identity.
        """
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> TokenExchangeResult:
        """
        Refreshes an expired access token using the refresh token.
        
        Args:
            refresh_token (str): The refresh token.
            
        Returns:
            TokenExchangeResult: Standardized token result containing the new tokens.
        """
        pass
