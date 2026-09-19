import httpx
from typing import Optional

from app.core.oauth.provider import OAuthProvider, TokenExchangeResult
from app.core.config import META_APP_ID, META_APP_SECRET, META_REDIRECT_URI

GRAPH_API_VERSION = "v21.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

class FacebookProvider(OAuthProvider):
    @property
    def name(self) -> str:
        return "facebook"

    def get_authorization_url(self, state: str, code_challenge: Optional[str] = None) -> str:
        scopes = "pages_manage_posts,pages_show_list,pages_read_engagement"
        return (
            f"https://www.facebook.com/{GRAPH_API_VERSION}/dialog/oauth?client_id={META_APP_ID}"
            f"&redirect_uri={META_REDIRECT_URI}"
            f"&state={state}"
            f"&scope={scopes}"
            f"&response_type=code"
        )

    async def exchange_code(self, code: str, redirect_uri: str, code_verifier: Optional[str] = None) -> TokenExchangeResult:
        async with httpx.AsyncClient() as client:
            # 1. Exchange code for short-lived User Access Token
            token_resp = await client.get(
                f"{GRAPH_API_BASE}/oauth/access_token",
                params={
                    "client_id": META_APP_ID,
                    "redirect_uri": redirect_uri,
                    "client_secret": META_APP_SECRET,
                    "code": code,
                },
            )
            token_resp.raise_for_status()
            short_lived_token = token_resp.json().get("access_token")

            # 2. Exchange short-lived token for long-lived token (~60 days)
            ll_resp = await client.get(
                f"{GRAPH_API_BASE}/oauth/access_token",
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": META_APP_ID,
                    "client_secret": META_APP_SECRET,
                    "fb_exchange_token": short_lived_token,
                },
            )

            if ll_resp.status_code == 200:
                ll_data = ll_resp.json()
                access_token = ll_data.get("access_token", short_lived_token)
                expires_in = ll_data.get("expires_in", 5184000)  # default ~60 days
            else:
                access_token = short_lived_token
                expires_in = 3600  # short-lived ~1 hour

            # 3. Get basic user info (id, name)
            user_resp = await client.get(
                f"{GRAPH_API_BASE}/me",
                params={
                    "fields": "id,name",
                    "access_token": access_token
                }
            )
            
            provider_user_id = None
            account_name = None
            
            if user_resp.status_code == 200:
                user_data = user_resp.json()
                provider_user_id = user_data.get("id")
                account_name = user_data.get("name")

            return TokenExchangeResult(
                access_token=access_token,
                expires_in=expires_in,
                refresh_token=None, # FB long-lived tokens don't use standard refresh tokens this way
                provider_user_id=provider_user_id,
                account_name=account_name,
                scopes="pages_manage_posts,pages_show_list,pages_read_engagement"
            )

    async def refresh_token(self, refresh_token: str) -> TokenExchangeResult:
        # Facebook doesn't use refresh tokens in the standard way. 
        # Long-lived tokens usually need to be refreshed via user re-authentication or specific graph API calls.
        # This implementation will return a failure for standard refresh.
        raise Exception("Facebook long-lived tokens cannot be refreshed generically without client interaction.")
