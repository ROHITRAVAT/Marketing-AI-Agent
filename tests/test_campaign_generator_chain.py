import pytest
from unittest.mock import AsyncMock, patch

from app.langchain.chains import build_campaign_generator_chain
from app.langchain.schemas import CampaignStrategyOutput


@pytest.mark.asyncio
async def test_build_campaign_generator_chain_returns_structured_output():
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = CampaignStrategyOutput(
        target_audience="Runners",
        key_messages=["Run faster", "Feel better"],
        channels=["Instagram", "Email"],
        success_metrics=["Sign-ups", "CTR"],
    )

    with patch("app.langchain.chains.build_structured_chain", return_value=mock_chain):
        chain = build_campaign_generator_chain()
        result = await chain.ainvoke({
            "campaign_goal": "Increase sign-ups",
            "product": "Awesome Shoes",
            "target_audience": "Runners",
            "platform": "Instagram",
        })

        assert "Runners" in result.target_audience
        mock_chain.ainvoke.assert_called_once()