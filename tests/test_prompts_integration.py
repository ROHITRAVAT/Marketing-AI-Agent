import pytest
from app.agents.state import MarketingAgentState
from app.agents.nodes.strategy import generate_strategy
from app.agents.nodes.content import generate_content

class MockOllamaService:
    async def generate(self, prompt: str, **kwargs) -> str:
        return f"Mocked LLM Response for:\n{prompt}"

@pytest.fixture
def mock_ollama(monkeypatch):
    monkeypatch.setattr("app.agents.nodes.strategy.get_ollama_service", lambda: MockOllamaService())
    monkeypatch.setattr("app.agents.nodes.content.get_ollama_service", lambda: MockOllamaService())

@pytest.mark.asyncio
async def test_generate_strategy_uses_prompt_manager(mock_ollama):
    """Verify that the generate_strategy node retrieves the rendered prompt from the library and calls the LLM."""
    state: MarketingAgentState = {
        "user_id": 1,
        "user_request": "Need a campaign",
        "product": "AI App",
        "target_audience": "Marketers",
        "platform": "Twitter",
        "campaign_goal": "Brand Awareness",
        "analysis": "Test analysis string.",
        "strategy": "",
        "generated_content": "",
        "clarification_message": "",
        "status": "pending",
        "error_message": ""
    }
    
    result = await generate_strategy(state)
    
    assert result["status"] == "success"
    assert "Mocked LLM Response for:" in result["strategy"]
    assert "System:" in result["strategy"]
    assert "Senior Marketing Strategist" in result["strategy"]
    assert "Product/Service: AI App" in result["strategy"]
    assert "Preliminary Analysis:\nTest analysis string." in result["strategy"]

@pytest.mark.asyncio
async def test_generate_content_uses_prompt_manager(mock_ollama):
    """Verify that the generate_content node retrieves the rendered prompt from the library and calls the LLM."""
    state: MarketingAgentState = {
        "user_id": 1,
        "user_request": "Need content",
        "product": "AI App",
        "target_audience": "Marketers",
        "platform": "Twitter",
        "campaign_goal": "Brand Awareness",
        "analysis": "Test analysis string.",
        "strategy": "The generated strategy text.",
        "generated_content": "",
        "clarification_message": "",
        "status": "pending",
        "error_message": ""
    }
    
    result = await generate_content(state)
    
    assert result["status"] == "completed"
    assert "Mocked LLM Response for:" in result["generated_content"]
    assert "System:" in result["generated_content"]
    assert "expert Marketing AI Copywriter" in result["generated_content"]
    assert "Strategy:\nThe generated strategy text." in result["generated_content"]
