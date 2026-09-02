import pytest
from unittest.mock import AsyncMock, patch
from app.agents.state import MarketingAgentState
from app.agents.nodes.strategy import generate_strategy
from app.agents.nodes.content import generate_content
from app.langchain.schemas import CampaignStrategyOutput, ContentOutput

@pytest.mark.asyncio
async def test_generate_strategy_node():
    """Test that the strategy node generates a structured strategy."""
    state = MarketingAgentState(
        product="Awesome Shoes",
        target_audience="Runners",
        platform="Instagram",
        campaign_goal="Increase sales",
        analysis="Analysis done."
    )
    
    mock_strategy = CampaignStrategyOutput(
        target_audience="Runners",
        key_messages=["Run faster", "Feel better"],
        channels=["Instagram", "Facebook"],
        success_metrics=["Sales", "Click-through rate"],
        budget_allocation="50% Ads, 50% Influencers"
    )

    with patch("app.agents.nodes.strategy.build_structured_chain") as mock_build_chain:
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = mock_strategy
        mock_build_chain.return_value = mock_chain
        
        result_state = await generate_strategy(state)
        
        assert result_state["status"] == "success"
        assert "target_audience" in result_state["strategy"]
        assert "Runners" in result_state["strategy"]
        mock_chain.ainvoke.assert_called_once()

@pytest.mark.asyncio
async def test_generate_content_node():
    """Test that the content node generates structured content."""
    state = MarketingAgentState(
        product="Awesome Shoes",
        target_audience="Runners",
        platform="Instagram",
        campaign_goal="Increase sales",
        strategy="Some strategy"
    )

    mock_content = ContentOutput(
        headline="Run Faster Today!",
        body_copy="Buy our awesome shoes and feel the difference.",
        call_to_action="Shop Now",
        hashtags=["#running", "#shoes"]
    )

    with patch("app.agents.nodes.content.build_structured_chain") as mock_build_chain:
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = mock_content
        mock_build_chain.return_value = mock_chain
        
        result_state = await generate_content(state)
        
        assert result_state["status"] == "completed"
        assert "Run Faster Today!" in result_state["generated_content"]
        mock_chain.ainvoke.assert_called_once()
