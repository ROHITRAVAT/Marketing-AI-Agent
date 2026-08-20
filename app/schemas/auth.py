from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    """Request schema for registering a new user."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    username: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=100,
    )
    full_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

class UserLogin(BaseModel):
    """Request schema for user login."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserResponse(BaseModel):
    """Response schema for user data."""

    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

class TokenResponse(BaseModel):
    """Response schema containing the JWT access token."""

    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """JWT payload schema."""

    sub: str
    role: str
    exp: datetime

class ForgotPasswordRequest(BaseModel):
    """Request to start the password reset flow."""

    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """Response for a password reset request."""

    message: str


class ResetPasswordRequest(BaseModel):
    """Request to reset a password using a reset token."""

    token: str
    new_password: str = Field(min_length=8, max_length=128)


class ResetPasswordResponse(BaseModel):
    """Response after successfully resetting a password."""

    message: str