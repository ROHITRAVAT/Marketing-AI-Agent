from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.auth_test import router as auth_test_router
from app.api.v1.endpoints.campaigns import router as campaigns_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.ollama import router as ollama_router
from app.api.v1.endpoints.prompts import router as prompts_router
from app.api.v1.endpoints.approvals import router as approvals_router
from app.api.v1.endpoints.agent import router as agent_router
from app.api.v1.endpoints.linkedin import router as linkedin_router
from app.api.v1.endpoints.facebook import router as facebook_router
from app.api.v1.endpoints.instagram import router as instagram_router
from app.api.v1.endpoints.twitter import router as twitter_router
from app.api.v1.endpoints.scheduled_posts import router as scheduled_posts_router
from app.api.v1.endpoints.analytics import router as analytics_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(auth_test_router)
api_router.include_router(campaigns_router)
api_router.include_router(ollama_router)
api_router.include_router(prompts_router)
api_router.include_router(approvals_router)
api_router.include_router(agent_router)
api_router.include_router(linkedin_router, prefix="/integrations/linkedin", tags=["integrations"])
api_router.include_router(facebook_router, prefix="/integrations/facebook", tags=["integrations"])
api_router.include_router(instagram_router, prefix="/integrations/instagram", tags=["integrations"])
api_router.include_router(twitter_router, prefix="/integrations/twitter", tags=["integrations"])
api_router.include_router(scheduled_posts_router)
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
