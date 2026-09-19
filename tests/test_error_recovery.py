import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.agents.state import MarketingAgentState
from app.agents.schemas import PlanStep, GeneratedContent, ToolResult
from app.agents.enums import AgentStatus, ToolExecutionStatus
from app.agents.nodes.error import handle_error
from app.core.errors import ToolExecutionError, MarketingAgentError, ErrorCategory
from app.utils.retry import retry_operation

@pytest.mark.asyncio
async def test_retry_operation_success_after_failure():
    """Test that retry_operation succeeds after initial failures."""
    
    mock_func = AsyncMock()
    mock_func.side_effect = [
        ValueError("Transient error 1"),
        ValueError("Transient error 2"),
        "Success!"
    ]
    
    result = await retry_operation(
        operation=mock_func,
        max_attempts=3,
        base_delay=0.01,
        max_delay=0.05,
        retryable_exceptions=(ValueError,)
    )
    
    assert result == "Success!"
    assert mock_func.call_count == 3

@pytest.mark.asyncio
async def test_retry_operation_permanent_failure():
    """Test that retry_operation raises exception after max attempts."""
    
    mock_func = AsyncMock(side_effect=ValueError("Always fails"))
    
    with pytest.raises(ValueError):
        await retry_operation(
            operation=mock_func,
            max_attempts=2,
            base_delay=0.01,
            max_delay=0.05,
            retryable_exceptions=(ValueError,)
        )
    
    assert mock_func.call_count == 2

@pytest.mark.asyncio
@patch("app.database.connection.AsyncSessionLocal")
async def test_handle_error_node_retryable(mock_db_session):
    """Test handle_error node with a retryable error."""
    
    from app.agents.schemas import ErrorInfo
    
    state = MarketingAgentState(
        user_input="test",
        status=AgentStatus.FAILED,
        retry_count=1,
        last_failed_node="execute_tools",
        error=ErrorInfo(
            error_code="TEST_ERROR",
            category=ErrorCategory.API_ERROR.value,
            message="Test retryable error",
            retryable=True,
            user_message="Wait"
        )
    )
    
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_db_session.return_value.__aenter__.return_value = mock_session
    
    result = await handle_error(state)
    
    assert result["status"] == AgentStatus.RETRYING
    assert result["retry_count"] == 2
    
    # Assert DB was called to log the error
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

@pytest.mark.asyncio
@patch("app.database.connection.AsyncSessionLocal")
async def test_handle_error_node_permanent(mock_db_session):
    """Test handle_error node with a non-retryable error."""
    from app.agents.schemas import ErrorInfo
    
    state = MarketingAgentState(
        user_input="test",
        status=AgentStatus.FAILED,
        retry_count=0,
        last_failed_node="execute_tools",
        error=ErrorInfo(
            error_code="TEST_PERM_ERROR",
            category=ErrorCategory.VALIDATION_ERROR.value,
            message="Test permanent error",
            retryable=False,
            user_message="Fatal"
        )
    )
    
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_db_session.return_value.__aenter__.return_value = mock_session
    
    result = await handle_error(state)
    
    assert result["status"] == AgentStatus.FAILED
    assert result["retry_count"] == 0

@pytest.mark.asyncio
@patch("app.agents.nodes.tools.build_seo_chain")
async def test_execute_tools_idempotency(mock_build_seo_chain):
    """Test that execute_tools skips already successful steps based on idempotency_key."""
    from app.agents.nodes.tools import execute_tools
    
    state = MarketingAgentState(
        user_input="test",
        plan=[PlanStep(step_id="1", description="SEO optimization")],
        approval_request_id=123,
        tool_results=[
            ToolResult(
                tool_name="seo_optimization",
                status=ToolExecutionStatus.SUCCESS,
                idempotency_key="approval_123_step_1",
                data={"output": "old_result"}
            )
        ]
    )
    
    mock_chain = AsyncMock()
    mock_build_seo_chain.return_value = mock_chain
    
    result = await execute_tools(state)
    
    # Should skip executing the chain since it was already successful
    mock_chain.ainvoke.assert_not_called()
    assert len(result["tool_results"]) == 1
    assert result["tool_results"][0].data["output"] == "old_result"
