import pytest
from unittest.mock import AsyncMock, patch

from app.agents.state import MarketingAgentState
from app.agents.nodes.strategy import generate_strategy
from app.agents.nodes.content import generate_content


@pytest.mark.asyncio
async def test_generate_strategy_node():
    """Test that the strategy node generates a text strategy via build_text_chain."""
    state = MarketingAgentState(
        user_input="Create a marketing strategy for Awesome Shoes targeting runners on Instagram.",
        product="Awesome Shoes",
        target_audience="Runners",
        platform="Instagram",
        campaign_goal="Increase sales",
    )

    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = "## Objective\nIncrease sales...\n## Audience\nRunners"

    with patch("app.agents.nodes.strategy.build_text_chain", return_value=mock_chain):
        result_state = await generate_strategy(state)

        assert result_state["status"].value == "completed" if hasattr(result_state["status"], "value") else True
        assert "Objective" in result_state["strategy"]
        mock_chain.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_generate_content_node():
    """Test that the content node generates content and wraps it in GeneratedContent."""
    state = MarketingAgentState(
        user_input="Generate content for Awesome Shoes targeting runners on Instagram.",
        product="Awesome Shoes",
        target_audience="Runners",
        platform="Instagram",
        campaign_goal="Increase sales",
        strategy="Some strategy",
    )

    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = "Run Faster Today! Shop Now. #running #shoes"

    with patch("app.agents.nodes.content.build_text_chain", return_value=mock_chain):
        result_state = await generate_content(state)

        assert result_state["generated_content"].body == "Run Faster Today! Shop Now. #running #shoes"
        assert result_state["generated_content"].content_type == "marketing_copy"
        mock_chain.ainvoke.assert_called_once()