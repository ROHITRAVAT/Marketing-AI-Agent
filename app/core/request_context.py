import contextvars
from typing import Optional

# Context variable to store the request ID for the current request
request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)

def get_request_id() -> Optional[str]:
    """Retrieve the current request ID."""
    return request_id_var.get()

def set_request_id(request_id: str) -> contextvars.Token:
    """Set the request ID for the current context."""
    return request_id_var.set(request_id)
