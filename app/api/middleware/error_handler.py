from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.errors import MarketingAgentError
import logging

logger = logging.getLogger(__name__)

async def marketing_agent_error_handler(request: Request, exc: MarketingAgentError):
    """
    Global exception handler for MarketingAgentError.
    Ensures safe, structured errors are returned to the frontend without leaking secrets.
    """
    logger.error(
        f"MarketingAgentError caught in middleware: {exc.error_code} - {exc.message}",
        exc_info=exc
    )
    
    # Map certain error categories to HTTP status codes
    status_code = 400
    if exc.category.value == "AUTHENTICATION_ERROR":
        status_code = 401
    elif exc.category.value == "AUTHORIZATION_ERROR":
        status_code = 403
    elif exc.category.value in ["NETWORK_ERROR", "TIMEOUT_ERROR", "API_ERROR", "VECTOR_DB_ERROR"]:
        status_code = 502 # Bad Gateway / Upstream Error
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
