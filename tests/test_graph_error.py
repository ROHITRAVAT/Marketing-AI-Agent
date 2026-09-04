import pytest

from app.agents.graph import build_marketing_graph
from app.agents.state import MarketingAgentState


@pytest.mark.asyncio
async def test_strategy_failure_stops_graph(monkeypatch):
    """
    Verify that a failed strategy node:
    1. Produces status='failed'
    2. Stores a safe error message
    3. Does not execute content generation
    """

    async def mock_retrieval(state: MarketingAgentState) -> dict:
        return {"retrieved_documents": []}

    def failing_strategy(state: MarketingAgentState) -> dict:
        return {
            "status": "failed",
            "error_message": (
                "Unable to complete the 'generate_strategy' step "
                "of the marketing workflow."
            ),
        }

    def content_should_not_run(state: MarketingAgentState) -> dict:
        raise AssertionError(
            "generate_content should not run after strategy failure"
        )

    monkeypatch.setattr("app.agents.graph.retrieve_documents", mock_retrieval)
    monkeypatch.setattr("app.agents.graph.generate_strategy", failing_strategy)
    monkeypatch.setattr("app.agents.graph.generate_content", content_should_not_run)

    marketing_graph = build_marketing_graph()

    state: MarketingAgentState = {
        "user_id": 1,
        "user_input": "Create a LinkedIn campaign",
        "product": "AI Marketing Platform",
        "target_audience": "Small Businesses",
        "platform": "LinkedIn",
        "campaign_goal": "Lead Generation",
        "analysis": "",
        "strategy": "",
        "generated_content": None,
        "clarification_message": "",
        "status": "idle",
        "error_message": "",
    }

    result = await marketing_graph.ainvoke(state)

    assert result["status"] == "failed"
    assert "generate_strategy" in result["error_message"]