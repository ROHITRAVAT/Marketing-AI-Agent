import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.agents.nodes.tools import execute_tools
from app.agents.schemas import PlanStep
from app.agents.state import MarketingAgentState
from app.agents.enums import ToolExecutionStatus
from app.core.errors import ToolExecutionError


@pytest.mark.asyncio
async def test_execute_tools_creates_real_campaign():
    state = MarketingAgentState(
        user_input="Create a campaign",
        user_id=1,
        product="Awesome Shoes",
        target_audience="Runners",
        campaign_goal="Increase sales",
        plan=[PlanStep(step_id="1", description="Create the marketing campaign record")],
    )

    mock_campaign = MagicMock(id=42, name="Awesome Shoes")

    with patch("app.services.campaign_service.CampaignService.create_campaign", AsyncMock(return_value=mock_campaign)):
        result = await execute_tools(state)

    assert len(result["tool_results"]) == 1
    assert result["tool_results"][0].tool_name == "create_campaign"
    assert result["tool_results"][0].status == ToolExecutionStatus.SUCCESS
    assert result["tool_results"][0].data["output"]["campaign_id"] == 42


@pytest.mark.asyncio
async def test_execute_tools_campaign_without_user_id_fails_honestly():
    state = MarketingAgentState(
        user_input="Create a campaign",
        product="Awesome Shoes",
        plan=[PlanStep(step_id="1", description="Create the marketing campaign record")],
    )

    result = await execute_tools(state)

    assert result["tool_results"][0].status == ToolExecutionStatus.FAILED
    assert "user_id" in result["tool_results"][0].error