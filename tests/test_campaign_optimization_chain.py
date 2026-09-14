import pytest
from unittest.mock import AsyncMock, patch

from app.langchain.chains import build_campaign_optimization_chain
from app.langchain.schemas import CampaignOptimizationOutput


@pytest.mark.asyncio
async def test_build_campaign_optimization_chain_returns_structured_output():
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = CampaignOptimizationOutput(
        strengths=["Strong engagement on Instagram"],
        weaknesses=["Low email open rate"],
        recommendations=["A/B test subject lines"],
    )

    with patch("app.langchain.chains.build_structured_chain", return_value=mock_chain):
        chain = build_campaign_optimization_chain()
        result = await chain.ainvoke({
            "campaign_name": "Summer Sale",
            "description": "Promote summer discounts",
            "target_audience": "Bargain shoppers",
            "status": "active",
            "budget": "5000",
        })

        assert "A/B test subject lines" in result.recommendations
        mock_chain.ainvoke.assert_called_once()