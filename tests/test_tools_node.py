import pytest
from unittest.mock import AsyncMock, patch

from app.agents.nodes.tools import execute_tools
from app.agents.schemas import PlanStep, GeneratedContent
from app.agents.state import MarketingAgentState
from app.agents.enums import ToolExecutionStatus


@pytest.mark.asyncio
async def test_execute_tools_dispatches_seo_step():
    state = MarketingAgentState(
        user_input="Create a campaign",
        product="Awesome Shoes",
        target_audience="Runners",
        plan=[PlanStep(step_id="1", description="Generate SEO recommendations for the content")],
        generated_content=GeneratedContent(content_type="marketing_copy", body="Run faster."),
    )

    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = "SEO Title: Best Shoes\nKeywords: running, shoes"

    with patch("app.agents.nodes.tools.build_seo_chain", return_value=mock_chain):
        result = await execute_tools(state)

    assert len(result["tool_results"]) == 1
    assert result["tool_results"][0].tool_name == "seo_optimization"
    assert result["tool_results"][0].status == ToolExecutionStatus.SUCCESS


@pytest.mark.asyncio
async def test_execute_tools_dispatches_social_media_step():
    state = MarketingAgentState(
        user_id=1,
        user_input="Create a campaign",
        platform="Instagram",
        target_audience="Runners",
        campaign_goal="Increase sales",
        plan=[PlanStep(step_id="1", description="Generate social media posts")],
    )

    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = "Post 1: Run faster today!"

    mock_db = AsyncMock()
    mock_db.__aenter__.return_value = mock_db

    with patch("app.agents.nodes.tools.build_social_media_chain", return_value=mock_chain), \
         patch("app.agents.nodes.tools.db_conn.AsyncSessionLocal", return_value=mock_db), \
         patch("app.core.oauth.manager.TokenManager.get_connection_status", new_callable=AsyncMock, return_value=None), \
         patch("app.services.instagram_service.InstagramService.publish_post", new_callable=AsyncMock, return_value="mock_post_id"):
        result = await execute_tools(state)

    assert len(result["tool_results"]) == 1
    assert result["tool_results"][0].tool_name == "instagram_publish"
    assert result["tool_results"][0].status == ToolExecutionStatus.SUCCESS


@pytest.mark.asyncio
async def test_execute_tools_records_unmatched_step_honestly():
    state = MarketingAgentState(
        user_input="Create a campaign",
        plan=[PlanStep(step_id="1", description="Post to LinkedIn via browser automation")],
    )

    result = await execute_tools(state)

    assert len(result["tool_results"]) == 1
    assert result["tool_results"][0].status == ToolExecutionStatus.FAILED
    assert "No tool implemented" in result["tool_results"][0].error


@pytest.mark.asyncio
async def test_execute_tools_handles_tool_exception_gracefully():
    state = MarketingAgentState(
        user_input="Create a campaign",
        plan=[PlanStep(step_id="1", description="Generate SEO recommendations")],
    )

    with patch("app.agents.nodes.tools.build_seo_chain", side_effect=RuntimeError("Ollama down")):
        result = await execute_tools(state)

    assert result["tool_results"][0].status == ToolExecutionStatus.FAILED
    assert "Ollama down" in result["tool_results"][0].error


@pytest.mark.asyncio
async def test_execute_tools_empty_plan_returns_empty_results():
    state = MarketingAgentState(user_input="Create a campaign")
    result = await execute_tools(state)
    assert result["tool_results"] == []
