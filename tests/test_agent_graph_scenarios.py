import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.agents.enums import AgentStatus
from app.agents.graph import build_marketing_graph
from app.agents.state import MarketingAgentState


@pytest.mark.asyncio
async def test_agent_graph_strategy_failure_reaches_final_response():
    """A strategy failure should route straight to final response, not content generation."""
    graph = build_marketing_graph()

    initial_state = MarketingAgentState(
        user_input="Create a campaign for a new energy drink.",
        product="Energy Drink",
        target_audience="Athletes",
        platform="Instagram",
        campaign_goal="Increase awareness",
    )

    with patch("app.agents.nodes.retrieval.retrieve_documents") as mock_retrieve, \
         patch("app.agents.nodes.strategy.build_text_chain") as mock_strategy_chain:

        async def mock_retrieve_func(state):
            return {"retrieved_documents": []}
        mock_retrieve.side_effect = mock_retrieve_func

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=RuntimeError("LLM unavailable"))
        mock_strategy_chain.return_value = mock_chain

        result_state = await graph.ainvoke(initial_state)

        assert result_state["status"] == AgentStatus.FAILED
        assert "Workflow failed" in result_state["final_response"]


@pytest.mark.asyncio
async def test_agent_graph_revision_loop_regenerates_content_once_rejected():
    """Content rejected on first review should be regenerated, then approved on retry."""
    graph = build_marketing_graph()

    initial_state = MarketingAgentState(
        user_input="Create a campaign for a new energy drink.",
        product="Energy Drink",
        target_audience="Athletes",
        platform="Instagram",
        campaign_goal="Increase awareness",
    )

    with patch("app.agents.nodes.retrieval.retrieve_documents") as mock_retrieve, \
         patch("app.agents.nodes.strategy.build_text_chain") as mock_strategy_chain, \
         patch("app.agents.nodes.content.build_text_chain") as mock_content_chain, \
         patch("app.agents.nodes.planning.build_json_chain") as mock_planning_chain, \
         patch("app.agents.nodes.review.build_json_chain") as mock_review_chain:

        async def mock_retrieve_func(state):
            return {"retrieved_documents": []}
        mock_retrieve.side_effect = mock_retrieve_func

        text_chain = MagicMock()
        text_chain.ainvoke = AsyncMock(return_value="Some content")
        mock_strategy_chain.return_value = text_chain
        mock_content_chain.return_value = text_chain

        planning_chain = MagicMock()
        planning_chain.ainvoke = AsyncMock(return_value=[{"step_id": "1", "description": "Execute strategy"}])
        mock_planning_chain.return_value = planning_chain

        review_chain = MagicMock()
        review_chain.ainvoke = AsyncMock(
            side_effect=[
                {"approved": False, "score": 3.0, "feedback": "Too generic", "issues": ["vague"]},
                {"approved": True, "score": 8.5, "feedback": "Better", "issues": []},
            ]
        )
        mock_review_chain.return_value = review_chain

        result_state = await graph.ainvoke(initial_state)

        assert result_state["revision_count"] == 2
        assert result_state["approval_status"].value == "approved"
        assert result_state["status"] == AgentStatus.COMPLETED