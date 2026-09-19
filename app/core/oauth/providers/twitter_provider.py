import httpx
import base64
from typing import Optional

from app.core.oauth.provider import OAuthProvider, TokenExchangeResult
from app.core.config import TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET, TWITTER_REDIRECT_URI

class TwitterProvider(OAuthProvider):
    @property
    def name(self) -> str:
        return "twitter"
        
    @property
    def requires_pkce(self) -> bool:
        return True

    def get_authorization_url(self, state: str, code_challenge: Optional[str] = None) -> str:
        scopes = "tweet.read tweet.write users.read offline.access"
        return (
            f"https://twitter.com/i/oauth2/authorize?response_type=code"
            f"&client_id={TWITTER_CLIENT_ID}"
            f"&redirect_uri={TWITTER_REDIRECT_URI}"
            f"&scope={scopes.replace(' ', '%20')}"
            f"&state={state}"
            f"&code_challenge={code_challenge}"
            f"&code_challenge_method=S256"
        )

    async def exchange_code(self, code: str, redirect_uri: str, code_verifier: Optional[str] = None) -> TokenExchangeResult:
        if not code_verifier:
            raise ValueError("Twitter requires a PKCE code_verifier for token exchange.")
            
        async with httpx.AsyncClient() as client:
            auth_args = {}
            if TWITTER_CLIENT_SECRET:
                auth_args["auth"] = (TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET)
            else:
                auth_args["data"] = {"client_id": TWITTER_CLIENT_ID}

            response = await client.post(
                "https://api.twitter.com/2/oauth2/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "code_verifier": code_verifier,
                    **auth_args.get("data", {})
                },
                auth=auth_args.get("auth"),
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            token_data = response.json()
            
            access_token = token_data.get("access_token")
            
            # Fetch user identity
            user_response = await client.get(
                "https://api.twitter.com/2/users/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            provider_user_id = None
            account_name = None
            if user_response.status_code == 200:
                user_data = user_response.json().get("data", {})
                provider_user_id = user_data.get("id")
                username = user_data.get("username")
                name = user_data.get("name")
                account_name = f"@{username}" if username else name
                
            return TokenExchangeResult(
                access_token=access_token,
                expires_in=token_data.get("expires_in", 7200),
                refresh_token=token_data.get("refresh_token"),
                provider_user_id=provider_user_id,
                account_name=account_name,
                scopes="tweet.read tweet.write users.read offline.access"
            )

    async def refresh_token(self, refresh_token: str) -> TokenExchangeResult:
        async with httpx.AsyncClient() as client:
            auth_args = {}
            if TWITTER_CLIENT_SECRET:
                auth_args["auth"] = (TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET)
            else:
                auth_args["data"] = {"client_id": TWITTER_CLIENT_ID}

            response = await client.post(
                "https://api.twitter.com/2/oauth2/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    **auth_args.get("data", {})
                },
                auth=auth_args.get("auth"),
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            token_data = response.json()
            
            return TokenExchangeResult(
                access_token=token_data.get("access_token"),
                expires_in=token_data.get("expires_in", 7200),
                refresh_token=token_data.get("refresh_token")
            )
