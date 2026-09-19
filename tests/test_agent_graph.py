import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from contextlib import asynccontextmanager

from app.agents.state import MarketingAgentState
from app.agents.enums import AgentStatus, ApprovalStatus
from app.agents.graph import build_marketing_graph

@pytest.mark.asyncio
async def test_agent_graph_success_flow():
    graph = build_marketing_graph()

    initial_state = MarketingAgentState(
        user_input="We need a campaign for a new coffee blend.",
        product="Coffee Blend",
        target_audience="Coffee enthusiasts",
        platform="Twitter",
        campaign_goal="Increase sales by 10%",
        user_id=1
    )

    # Mock AsyncSessionLocal in approval node to avoid real DB calls
    @asynccontextmanager
    async def mock_session():
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        async def mock_execute(*args, **kwargs):
            return mock_result
        mock_db.execute = mock_execute
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        yield mock_db

    # Mock the LLM chains and other external dependencies
    with patch("app.database.connection.AsyncSessionLocal", mock_session), \
         patch("app.database.connection.AsyncSessionLocal", mock_session), \
         patch("app.agents.nodes.approval.interrupt", return_value={"action": "approve"}), \
         patch("app.agents.nodes.retrieval.retrieve_documents") as mock_retrieve, \
         patch("app.agents.nodes.strategy.build_text_chain") as mock_strategy_chain, \
         patch("app.agents.nodes.content.build_text_chain") as mock_content_chain, \
         patch("app.agents.nodes.planning.build_json_chain") as mock_planning_chain, \
         patch("app.agents.nodes.review.build_json_chain") as mock_review_chain:
        
        # Mock retrieval
        async def mock_retrieve_func(state):
            return {"retrieved_documents": []}
        mock_retrieve.side_effect = mock_retrieve_func

        # Mock strategy generation
        mock_text_chain_instance = MagicMock()
        mock_text_chain_instance.ainvoke = AsyncMock(return_value="Mocked Strategy")
        mock_strategy_chain.return_value = mock_text_chain_instance
        
        # Mock content generation
        mock_content_chain.return_value = mock_text_chain_instance

        # Mock planning
        mock_planning_chain_instance = MagicMock()
        mock_planning_chain_instance.ainvoke = AsyncMock(return_value=[{"step_id": "1", "description": "Mocked Step"}])
        mock_planning_chain.return_value = mock_planning_chain_instance

        # Mock review
        mock_review_chain_instance = MagicMock()
        mock_review_chain_instance.ainvoke = AsyncMock(return_value={"approved": True, "score": 9.5, "feedback": "Good", "issues": []})
        mock_review_chain.return_value = mock_review_chain_instance
        
        result_state = await graph.ainvoke(
            initial_state,
            config={
                "configurable": {
                    "thread_id": "test-success-flow"
                }
            }
        )

        assert result_state["status"] == AgentStatus.COMPLETED
        assert result_state["strategy"] == "Mocked Strategy"
        assert len(result_state["plan"]) == 1
        assert result_state["plan"][0].description == "Mocked Step"
        assert result_state["generated_content"] is not None
        assert result_state["generated_content"].body == "Mocked Strategy"
        assert result_state["approval_status"] == ApprovalStatus.APPROVED
        assert len(result_state["tool_results"]) == 1
        assert "Workflow failed" not in result_state["final_response"]


@pytest.mark.asyncio
async def test_agent_graph_clarification_flow():
    graph = build_marketing_graph()

    # Missing product, audience, platform, etc.
    initial_state = MarketingAgentState(
        user_input="We need a campaign."
    )
    
    result_state = await graph.ainvoke(initial_state)

    assert result_state["status"] == AgentStatus.NEEDS_CLARIFICATION
    assert "additional information" in result_state["clarification_message"]
    assert "additional information" in result_state["final_response"]
