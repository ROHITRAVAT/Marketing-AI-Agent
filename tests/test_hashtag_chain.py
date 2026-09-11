import pytest
from unittest.mock import AsyncMock, patch

from app.langchain.chains import build_hashtag_chain
from app.langchain.schemas import HashtagOutput


@pytest.mark.asyncio
async def test_build_hashtag_chain_returns_structured_output():
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = HashtagOutput(
        hashtags=["#running", "#marathon", "#fitness"],
        trending_note="#marathon is trending this season.",
    )

    with patch("app.langchain.chains.build_structured_chain", return_value=mock_chain):
        chain = build_hashtag_chain()
        result = await chain.ainvoke({
            "platform": "Instagram",
            "industry": "Running shoes",
            "product": "Awesome Shoes",
            "count": "5",
        })

        assert "#running" in result.hashtags
        mock_chain.ainvoke.assert_called_once()