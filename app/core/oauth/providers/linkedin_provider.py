import httpx
from typing import Optional

from app.core.oauth.provider import OAuthProvider, TokenExchangeResult
from app.core.config import LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, LINKEDIN_REDIRECT_URI

class LinkedInProvider(OAuthProvider):
    @property
    def name(self) -> str:
        return "linkedin"

    def get_authorization_url(self, state: str, code_challenge: Optional[str] = None) -> str:
        scopes = "openid profile email w_member_social"
        return (
            f"https://www.linkedin.com/oauth/v2/authorization?response_type=code"
            f"&client_id={LINKEDIN_CLIENT_ID}"
            f"&redirect_uri={LINKEDIN_REDIRECT_URI}"
            f"&state={state}"
            f"&scope={scopes}"
        )

    async def exchange_code(self, code: str, redirect_uri: str, code_verifier: Optional[str] = None) -> TokenExchangeResult:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": LINKEDIN_CLIENT_ID,
                    "client_secret": LINKEDIN_CLIENT_SECRET,
                }
            )
            response.raise_for_status()
            token_data = response.json()
            
            access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 0)
            refresh_token = token_data.get("refresh_token")
            
            # Get user info for OpenID (sub and name)
            user_info_resp = await client.get(
                "https://api.linkedin.com/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            provider_user_id = None
            account_name = None
            
            if user_info_resp.status_code == 200:
                user_info = user_info_resp.json()
                provider_user_id = user_info.get("sub")
                account_name = user_info.get("name")
                
            return TokenExchangeResult(
                access_token=access_token,
                expires_in=expires_in,
                refresh_token=refresh_token,
                provider_user_id=provider_user_id,
                account_name=account_name,
                scopes="openid profile email w_member_social"
            )

    async def refresh_token(self, refresh_token: str) -> TokenExchangeResult:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": LINKEDIN_CLIENT_ID,
                    "client_secret": LINKEDIN_CLIENT_SECRET,
                }
            )
            response.raise_for_status()
            token_data = response.json()
            
            return TokenExchangeResult(
                access_token=token_data.get("access_token"),
                expires_in=token_data.get("expires_in", 0),
                refresh_token=token_data.get("refresh_token") # some providers return a new refresh token
            )
