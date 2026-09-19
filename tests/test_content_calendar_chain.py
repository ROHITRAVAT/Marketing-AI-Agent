import pytest
from unittest.mock import AsyncMock, patch

from app.langchain.chains import build_content_calendar_chain
from app.langchain.schemas import ContentCalendarOutput, ContentCalendarEntry


@pytest.mark.asyncio
async def test_build_content_calendar_chain_returns_structured_output():
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = ContentCalendarOutput(
        schedule=[
            ContentCalendarEntry(date="Monday", platform="Instagram", content_type="post", topic="Product launch"),
            ContentCalendarEntry(date="Thursday", platform="LinkedIn", content_type="article", topic="Customer story"),
        ],
        frequency="weekly",
    )

    with patch("app.langchain.chains.build_structured_chain", return_value=mock_chain):
        chain = build_content_calendar_chain()
        result = await chain.ainvoke({
            "product": "Awesome Shoes",
            "target_audience": "Runners",
            "platform": "Instagram",
            "campaign_goal": "Increase sales",
            "timeframe": "weekly",
        })

        assert len(result.schedule) == 2
        assert result.schedule[0].platform == "Instagram"
        mock_chain.ainvoke.assert_called_once()