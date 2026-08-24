import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.request_context import set_request_id, get_request_id

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every incoming HTTP request with method, path, status, duration, and request ID."""

    async def dispatch(self, request: Request, call_next):
        # Extract existing request ID or generate a new one
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())
        else:
            # Sanitize existing request ID to prevent log injection or excessively long headers
            request_id = request_id[:64].strip()

        # Set the request ID in the current context
        token = set_request_id(request_id)

        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
            
            # Add the request ID to the response headers
            response.headers["X-Request-ID"] = request_id
            
            process_time = time.perf_counter() - start_time
            logger.info(
                "request_id=%s | %s %s -> %s (%.2fms)",
                request_id,
                request.method,
                request.url.path,
                response.status_code,
                process_time * 1000,
            )
            return response
        finally:
            # Reset contextvar token (though ContextVar manages per-async task context natively, 
            # this is good practice if context sharing is configured).
            from app.core.request_context import request_id_var
            request_id_var.reset(token)