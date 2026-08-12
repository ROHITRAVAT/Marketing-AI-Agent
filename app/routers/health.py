from fastapi import APIRouter

from app.services.health_service import HealthService


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("/")
async def health_check():
    return HealthService.get_health_status()