import pytest
from unittest.mock import AsyncMock, patch

from app.langchain.chains import build_seo_chain


@pytest.mark.asyncio
async def test_build_seo_chain_returns_text_output():
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = (
        "SEO Title: Best Running Shoes for Speed\n"
        "Meta Description: Discover our top running shoes built for speed and comfort.\n"
        "Keywords: running shoes, speed training, athletic footwear, marathon gear, comfort fit\n"
        "Heading Suggestions: H1: Best Running Shoes | H2: Why Choose Us | H2: Customer Reviews"
    )

    with patch("app.langchain.chains.build_text_chain", return_value=mock_chain):
        chain = build_seo_chain()
        result = await chain.ainvoke(
            {
                "product": "Awesome Shoes",
                "target_audience": "Runners",
                "generated_content": "Run faster with Awesome Shoes.",
            }
        )

        assert "SEO Title" in result
        assert "Keywords" in result
        mock_chain.ainvoke.assert_called_once()