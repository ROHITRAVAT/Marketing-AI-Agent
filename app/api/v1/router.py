from fastapi import APIRouter

from app.api.v1.endpoints.campaigns import router as campaigns_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.prompts import router as prompts_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(campaigns_router)
api_router.include_router(prompts_router)