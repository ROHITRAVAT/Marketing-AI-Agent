from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user, require_roles
from app.models.user import User, UserRole


router = APIRouter(
    prefix="/auth-test",
    tags=["Authentication Test"],
)


@router.get("/protected")
async def protected_test(
    current_user: User = Depends(get_current_user),
):
    """Temporary protected endpoint for authentication testing."""

    return {
        "message": "Authentication successful",
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
    }

@router.get("/admin-only")
async def admin_only_test(
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
):
    """Temporary endpoint accessible only to administrators."""

    return {
        "message": "Admin authorization successful",
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
    }


@router.get("/management")
async def management_test(
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER,
        )
    ),
):
    """Temporary endpoint accessible to admins and managers."""

    return {
        "message": "Management authorization successful",
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
    }