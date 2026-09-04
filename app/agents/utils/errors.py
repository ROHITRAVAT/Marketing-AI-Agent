import logging

from app.agents.state import MarketingAgentState
from app.agents.enums import AgentStatus

logger = logging.getLogger(__name__)


def handle_node_error(
    state: MarketingAgentState,
    error: Exception,
    node_name: str,
) -> dict:
    """
    Handle an unexpected error that occurs inside an agent node.

    The detailed exception is logged for developers.
    A safe error message is returned as a state update.
    """

    logger.exception(
        "Marketing agent node failed: %s",
        node_name,
        exc_info=error,
    )

    error_message = (
        f"Unable to complete the '{node_name}' step "
        "of the marketing workflow."
    )

    return {
        "status": AgentStatus.FAILED,
        "error_message": error_message,
    }