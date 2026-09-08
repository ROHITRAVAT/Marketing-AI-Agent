import logging

from app.agents.state import MarketingAgentState
from app.agents.enums import AgentStatus
from app.agents.schemas import ErrorInfo
from app.core.errors import MarketingAgentError, ErrorCategory

logger = logging.getLogger(__name__)


def handle_node_error(
    state: MarketingAgentState,
    error: Exception,
    node_name: str,
) -> dict:
    """
    Handle an unexpected error that occurs inside an agent node.

    The detailed exception is logged for developers.
    A safe error message is returned as a state update, setting the error info
    for the handle_error node to process.
    """

    logger.exception(
        "Marketing agent node failed: %s",
        node_name,
        exc_info=error,
    )

    if isinstance(error, MarketingAgentError):
        error_info = ErrorInfo(
            error_code=error.error_code,
            category=error.category.value,
            message=error.message,
            retryable=error.retryable,
            user_message=error.user_message
        )
    else:
        error_info = ErrorInfo(
            error_code="UNKNOWN_ERROR",
            category=ErrorCategory.UNKNOWN_ERROR.value,
            message=str(error),
            retryable=False,
            user_message=f"Unable to complete the '{node_name}' step of the marketing workflow."
        )

    return {
        "status": AgentStatus.FAILED,
        "error": error_info,
        "error_message": error_info.user_message or error_info.message,
        "last_failed_node": node_name
    }