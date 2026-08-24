from pydantic import BaseModel


class BaseResponse(BaseModel):
    """Base response schema with success flag and message."""

    success: bool
    message: str = "OK"


class SuccessResponse(BaseResponse):
    """Standard success response with optional data payload."""

    data: dict | None = None


class ErrorResponse(BaseResponse):
    """Standard error response with optional machine-readable error code."""

    error_code: str | None = None
    details: list | None = None
    request_id: str | None = None