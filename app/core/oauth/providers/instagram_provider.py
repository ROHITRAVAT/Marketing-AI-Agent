import httpx
from typing import Optional

from app.core.oauth.provider import OAuthProvider, TokenExchangeResult
from app.core.config import META_APP_ID, META_APP_SECRET, META_REDIRECT_URI

GRAPH_API_VERSION = "v21.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
INSTAGRAM_REDIRECT_URI = META_REDIRECT_URI.replace("facebook", "instagram")

class InstagramProvider(OAuthProvider):
    @property
    def name(self) -> str:
        return "instagram"

    def get_authorization_url(self, state: str, code_challenge: Optional[str] = None) -> str:
        scopes = (
            "instagram_business_basic,"
            "instagram_business_content_publish,"
            "instagram_business_manage_insights,"
            "pages_show_list,"
            "pages_read_engagement"
        )
        return (
            f"https://www.facebook.com/{GRAPH_API_VERSION}/dialog/oauth?client_id={META_APP_ID}"
            f"&redirect_uri={INSTAGRAM_REDIRECT_URI}"
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

            # 2. Exchange short-lived token for long-lived token
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
                expires_in = ll_data.get("expires_in", 5184000)
            else:
                access_token = short_lived_token
                expires_in = 3600

            return TokenExchangeResult(
                access_token=access_token,
                expires_in=expires_in,
                refresh_token=None,
                provider_user_id=None, # IG service will handle account specific saving
                account_name=None,
                scopes="instagram_oauth_base"
            )

    async def refresh_token(self, refresh_token: str) -> TokenExchangeResult:
        raise Exception("Instagram/Meta long-lived tokens cannot be refreshed generically.")
