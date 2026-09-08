import pytest
from unittest.mock import patch, AsyncMock
from app.agents.graph import build_marketing_graph
from app.agents.state import MarketingAgentState
from app.agents.enums import AgentStatus

pytestmark = pytest.mark.asyncio

@pytest.fixture
def graph():
    return build_marketing_graph()

async def test_e2e_llm_failure_recovery(graph):
    """Test that if the LLM completely fails, the graph handles it gracefully and transitions to error state."""
    state = MarketingAgentState(
        user_input="Create a campaign for testing LLM failure.",
        product="Test Product",
        target_audience="Developers",
        campaign_goal="Testing",
        platform="LinkedIn"
    )
    
    # Mock LLM to always raise an exception
    config = {"configurable": {"thread_id": "test-thread"}}
    with patch("langchain_core.language_models.chat_models.BaseChatModel.ainvoke", side_effect=Exception("Ollama unavailable")):
        result = await graph.ainvoke(state, config)
        
        # It might retry up to the limit and then fail, but ultimately it must end in FAILED or a handled final response
        # In this graph, handle_error sets status to FAILED and returns a safe final_response.
        assert result["status"] == AgentStatus.FAILED
        assert "Ollama unavailable" in result["error"].message or "Error" in result["final_response"]

async def test_e2e_tool_failure_recovery(graph, mock_social_media):
    """Test that a tool failure is caught and doesn't crash the workflow."""
    
    state = MarketingAgentState(
        user_input="Write an email campaign about our new AI agent product for developers.",
        platform="Email",
        product="AI",
        target_audience="Developers",
        campaign_goal="Sales"
    )
    
    from app.agents.schemas import ErrorInfo
    from app.agents.enums import AgentStatus
    from langchain_core.messages import AIMessage
    
    # Simulate an unexpected exception in tools by modifying the existing mock
    # We return a dict that simulates the node's internal exception handler returning FAILED
    mock_social_media.return_value = {
        "status": AgentStatus.FAILED,
        "error_message": "Social media API timeout",
        "error": ErrorInfo(
            error_code="TOOL_ERROR",
            category="TOOL_EXECUTION",
            message="Social media API timeout",
            retryable=False,
            user_message="Social media API timeout"
        )
    }
    
    from app.agents.graph import build_marketing_graph
    
    # We need to speedrun past human approval by patching it where it is used in the graph builder
    with patch("app.agents.graph.request_human_approval") as mock_approve:
        mock_approve.return_value = {"approval_status": "approved"}
        
        # Rebuild graph inside patch context so it binds the mocked node!
        local_graph = build_marketing_graph()
        
        config = {"configurable": {"thread_id": "test-thread"}}
        result = await local_graph.ainvoke(state, config)
        
        # Since tools failed, it should route to handle_error and mark as FAILED
        assert result["status"] == AgentStatus.FAILED
        assert "Social media API timeout" in result["error"].message or "error" in result["final_response"].lower()
