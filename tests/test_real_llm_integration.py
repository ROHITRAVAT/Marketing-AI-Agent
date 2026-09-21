import pytest
import asyncio
import httpx
from app.langchain.config import LANGCHAIN_SETTINGS
from app.agents.state import MarketingAgentState
from app.agents.nodes.content import generate_content
from app.agents.nodes.verification import verify_llm_output
from app.agents.schemas import GeneratedContent, LLMExecution
from unittest.mock import patch
import subprocess

pytestmark = pytest.mark.real_llm

def get_installed_ollama_models():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return []
        lines = result.stdout.strip().split('\n')[1:]
        models = [line.split()[0] for line in lines if line.strip()]
        return models
    except Exception:
        return []

def get_generative_model():
    models = get_installed_ollama_models()
    for m in models:
        if "minilm" not in m.lower() and "embed" not in m.lower():
            return m
    return None

async def is_ollama_reachable(url: str) -> bool:
    """Check if the Ollama server is reachable."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(url)
            return response.status_code == 200
    except Exception:
        return False

@pytest.fixture
async def check_ollama():
    """Fixture to check Ollama availability and models."""
    url = LANGCHAIN_SETTINGS.base_url
    if not await is_ollama_reachable(url):
        pytest.skip(f"Ollama server is not available at the configured endpoint: {url}")
        
    gen_model = get_generative_model()
    if not gen_model:
        pytest.skip("REAL LLM TEST NOT AVAILABLE\nReason:\nNo generative Ollama model is installed.")
        
    return gen_model

@pytest.mark.asyncio
async def test_real_llm_verification_flow(check_ollama):
    """
    Execute the real Marketing Agent workflow connecting to the actual Ollama server.
    """
    model_name = check_ollama
    provider = "ollama"
    
    # We need to ensure the system uses the generative model we found
    with patch("app.langchain.config.LANGCHAIN_SETTINGS.model", model_name), \
         patch("app.core.config.OLLAMA_MODEL", model_name):

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
        assert llm_exec.model == model_name
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
