import os

import pytest
import asyncio
import httpx
from app.langchain.config import LANGCHAIN_SETTINGS, LangChainSettings
from app.agents.state import MarketingAgentState
from app.agents.nodes.content import generate_content
from app.agents.nodes.verification import verify_llm_output
from app.agents.schemas import GeneratedContent, LLMExecution
from unittest.mock import patch

pytestmark = pytest.mark.real_llm


async def get_installed_ollama_models(base_url: str):
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            url = f"{base_url.rstrip('/')}/api/tags"
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                models = [model.get("name") for model in data.get("models", [])]
                return models
            return []
    except Exception:
        return []


@pytest.fixture
async def check_ollama():
    """
    Skip (never mock, never fail) when a real Ollama server or the model is unavailable.
    The model can be overridden with the REAL_LLM_TEST_MODEL environment variable.
    """
    url = LANGCHAIN_SETTINGS.base_url
    model = os.getenv("REAL_LLM_TEST_MODEL", "qwen3:8b")
    models = await get_installed_ollama_models(url)
    if not models:
        pytest.skip(f"Ollama is not reachable at {url} or has no models installed")
    if model not in models:
        pytest.skip(f"{model} is not installed on the Ollama server")
    return model


@pytest.mark.asyncio
async def test_real_llm_verification_flow(check_ollama):
    """
    Execute the real Marketing Agent workflow connecting to the actual Ollama server.
    """
    model_name = check_ollama
    provider = "ollama"

    # We need to ensure the system uses the generative model we found
    new_settings = LangChainSettings(model=model_name)
    with patch("app.langchain.llm.LANGCHAIN_SETTINGS", new_settings), \
         patch("app.langchain.config.LANGCHAIN_SETTINGS", new_settings), \
         patch("app.core.config.OLLAMA_MODEL", model_name):

        from app.langchain.llm import get_chat_model
        get_chat_model.cache_clear()

        unique_token = "REAL-OLLAMA-VERIFY-92831"
        prompt_text = f"""Create a short marketing message for a fictional product called:

"ZX-8472 Quantum Marketing Device"

You MUST include this exact unique verification token:

"{unique_token}"

Return only the marketing message."""

        state = MarketingAgentState(user_input=prompt_text)

        # 1. Execute the real content generation node
        result_content = await generate_content(state)

        # Check that generation didn't fail
        assert result_content.get("status") != "failed", f"Content generation failed: {result_content.get('error_message')}"

        # 2. Update state for verification node
        state.generated_content = result_content["generated_content"]
        state.llm_execution = result_content["llm_execution"]

        # 3. Verify execution evidence
        llm_exec = state.llm_execution
        assert llm_exec is not None
        assert llm_exec.llm_called is True
        assert llm_exec.response_received is True
        assert llm_exec.provider == provider
        assert llm_exec.model == "ollama"
        assert llm_exec.raw_llm_response is not None
        assert len(llm_exec.raw_llm_response) > 0
        assert llm_exec.response_used_as_final is True
        assert llm_exec.execution_id is not None

        # 4. Verify actual response contains token
        assert unique_token in llm_exec.raw_llm_response
        assert unique_token in state.generated_content.body

        # 5. Execute verification node
        result_verify = verify_llm_output(state)
        verification = result_verify["verification"]

        # 6. Verify final verification status
        assert verification.verification_status == "VERIFIED_LLM"
        assert verification.llm_invoked is True
        assert verification.response_received is True
        assert verification.response_used_as_final is True


def test_verification_hardcoded_content_with_mock():
    """
    Negative verification: LLM is invoked BUT response is replaced by hardcoded content.
    This test uses mocking because it specifically tests the verification logic.
    """
    state = MarketingAgentState(user_input="test")
    state.llm_execution = LLMExecution(
        llm_called=True,
        response_received=True,
        response_used_as_final=False,
        raw_llm_response="This is the real LLM response",
        provider="ollama",
        model="qwen3"
    )

    # The content was replaced with hardcoded content
    state.generated_content = GeneratedContent(body="Hardcoded static marketing content")

    result = verify_llm_output(state)
    verification = result["verification"]

    # Since llm_exec.response_used_as_final is False and content.body is present,
    # hardcoded_content_detected should be True.
    # Since llm_exec.response_received is True, status should be PARTIALLY_LLM_GENERATED
    assert verification.verification_status == "PARTIALLY_LLM_GENERATED"