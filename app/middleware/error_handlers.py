import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.encoders import jsonable_encoder

from app.schemas.common import ErrorResponse
from app.core.request_context import get_request_id
from app.core.errors import MarketingAgentError

logger = logging.getLogger(__name__)

async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    """Handle FastAPI HTTP exceptions (404, 401, etc.) with clean JSON."""
    request_id = get_request_id()

    logger.warning(
        "request_id=%s | HTTP error %s %s - status=%s detail=%s",
        request_id,
        request.method,
        request.url.path,
        exc.status_code,
        exc.detail,
    )

    error_response = ErrorResponse(
        success=False,
        message=str(exc.detail),
        detail=str(exc.detail),
        error_code=f"HTTP_{exc.status_code}",
        request_id=request_id,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
    )

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """Handle request validation errors with a clean 422 JSON response."""
    request_id = get_request_id()

    logger.warning(
        "request_id=%s | Validation error %s %s - errors=%s",
        request_id,
        request.method,
        request.url.path,
        exc.errors(),
    )

    error_response = ErrorResponse(
        success=False,
        message="Request validation failed",
        error_code="VALIDATION_ERROR",
        details=jsonable_encoder(exc.errors()),
        request_id=request_id,
    )

    return JSONResponse(
        status_code=422,
        content=error_response.model_dump(),
    )

async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unexpected errors.

    Logs the full error for debugging but returns a generic message to the
    client so internal details are never leaked.
    """
    request_id = get_request_id()
    
    logger.exception(
        "request_id=%s | Unhandled error on %s %s", 
        request_id, 
        request.method, 
        request.url.path
    )

    error_response = ErrorResponse(
        success=False,
        message="Internal server error",
        error_code="INTERNAL_SERVER_ERROR",
        request_id=request_id,
    )

    return JSONResponse(
        status_code=500,
        content=error_response.model_dump(),
    )

async def marketing_agent_error_handler(
    request: Request, 
    exc: MarketingAgentError
) -> JSONResponse:
    """
    Global exception handler for MarketingAgentError.
    Ensures safe, structured errors are returned to the frontend.
    """
    logger.error(
        f"MarketingAgentError caught in middleware: {exc.error_code} - {exc.message}",
        exc_info=exc
    )
    
    status_code = 400
    if exc.category.value == "AUTHENTICATION_ERROR":
        status_code = 401
    elif exc.category.value == "AUTHORIZATION_ERROR":
        status_code = 403
    elif exc.category.value in ["NETWORK_ERROR", "TIMEOUT_ERROR", "API_ERROR", "VECTOR_DB_ERROR"]:
        status_code = 502
    elif exc.category.value == "RATE_LIMIT_ERROR":
        status_code = 429
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.user_message or "An unexpected error occurred.",
                "retryable": exc.retryable
            }
        }
    )
