from app.core.oauth.manager import TokenManager
from app.core.oauth.providers.linkedin_provider import LinkedInProvider
from app.core.oauth.providers.facebook_provider import FacebookProvider
from app.core.oauth.providers.instagram_provider import InstagramProvider
from app.core.oauth.providers.twitter_provider import TwitterProvider

def register_all_providers():
    TokenManager.register_provider(LinkedInProvider())
    TokenManager.register_provider(FacebookProvider())
    TokenManager.register_provider(InstagramProvider())
    TokenManager.register_provider(TwitterProvider())

# Register immediately upon import
register_all_providers()
