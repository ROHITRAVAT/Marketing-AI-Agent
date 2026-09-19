import logging
import uuid
from app.agents.state import MarketingAgentState
from app.agents.enums import AgentStatus
from app.agents.schemas import ErrorInfo
from app.core.errors import MarketingAgentError, ErrorCategory
import app.database.connection as db_conn
from app.models.error_log import AgentErrorLog

logger = logging.getLogger(__name__)

async def handle_error(state: MarketingAgentState) -> dict:
    """
    Central error handling node for LangGraph workflow.
    
    This node is responsible for:
    1. Processing the error placed in state by a failing node.
    2. Persisting it to the database for auditing.
    3. Determining if the error is retryable and if retry limit is reached.
    4. Updating the state status to either RETRYING or FAILED/REQUIRES_MANUAL_ACTION.
    """
    logger.info("Entering handle_error node")
    
    if not state.error:
        # If we reached here without a structured error, create a generic one based on error_message
        msg = state.error_message or "Unknown error occurred"
        state.error = ErrorInfo(
            error_code="UNKNOWN_ERROR",
            category=ErrorCategory.UNKNOWN_ERROR.value,
            message=msg,
            retryable=False,
            user_message=msg if state.error_message else "An unexpected error occurred."
        )

    # Increment retry count if it's retryable
    retry_limit = 3
    is_retryable = state.error.retryable and state.retry_count < retry_limit
    
    new_retry_count = state.retry_count
    if is_retryable:
        new_retry_count += 1
        new_status = AgentStatus.RETRYING
        resolution_status = "retrying"
    else:
        new_status = AgentStatus.FAILED
        resolution_status = "failed"

    # Persist to Database
    try:
        async with db_conn.AsyncSessionLocal() as db:
            error_log = AgentErrorLog(
                workflow_id=f"thread_{state.user_id}" if state.user_id else str(uuid.uuid4()), # Need proper thread ID if available
                user_id=state.user_id,
                node=state.last_failed_node,
                tool=state.last_failed_tool,
                platform=state.platform,
                error_category=state.error.category,
                error_code=state.error.error_code,
                message=state.error.message,
                retryable=state.error.retryable,
                retry_count=new_retry_count,
                resolution_status=resolution_status,
            )
            db.add(error_log)
            await db.commit()
    except Exception as e:
        logger.error(f"Failed to persist error log: {e}")

    return {
        "status": new_status,
        "retry_count": new_retry_count,
        "error_message": state.error.user_message or state.error.message
    }
