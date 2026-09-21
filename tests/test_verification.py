import pytest
from app.agents.state import MarketingAgentState
from app.agents.schemas import GeneratedContent, LLMExecution
from app.agents.nodes.verification import verify_llm_output
from app.agents.nodes.content import generate_content
from unittest.mock import patch
from langchain_core.messages import AIMessage

def test_verification_real_llm():
    """Test 1 — Real LLM: VERIFIED_LLM"""
    state = MarketingAgentState(user_input="test")
    state.llm_execution = LLMExecution(
        llm_called=True,
        response_received=True,
        response_used_as_final=True,
        raw_llm_response="Real marketing text",
        provider="ollama",
        model="qwen3"
    )
    state.generated_content = GeneratedContent(body="Real marketing text")
    
    result = verify_llm_output(state)
    assert result["verification"].verification_status == "VERIFIED_LLM"


def test_verification_hardcoded():
    """Test 2 — Hardcoded response: HARD_CODED"""
    state = MarketingAgentState(user_input="test")
    # No LLM response used, but we got content
    state.llm_execution = LLMExecution(
        llm_called=False,
        response_received=False,
        response_used_as_final=False,
    )
    state.generated_content = GeneratedContent(body="Hardcoded static text")
    
    result = verify_llm_output(state)
    assert result["verification"].verification_status == "HARD_CODED"


def test_verification_mock():
    """Test 3 — Mock response: MOCK_CONTENT"""
    state = MarketingAgentState(user_input="test")
    state.llm_execution = LLMExecution(
        llm_called=True,
        response_received=True,
        response_used_as_final=True,
    )
    state.generated_content = GeneratedContent(body="This is a MagicMock response")
    
    result = verify_llm_output(state)
    assert result["verification"].verification_status == "MOCK_CONTENT"


def test_verification_fallback():
    """Test 4 — LLM failure: FALLBACK_CONTENT"""
    state = MarketingAgentState(user_input="test")
    state.llm_execution = LLMExecution(
        llm_called=True,
        response_received=False,
        response_used_as_final=False,
    )
    state.generated_content = GeneratedContent(body="default content because LLM failed")
    
    result = verify_llm_output(state)
    assert result["verification"].verification_status == "FALLBACK_CONTENT"


def test_verification_partially_generated():
    """Test 5 — LLM called but response ignored: PARTIALLY_LLM_GENERATED"""
    state = MarketingAgentState(user_input="test")
    state.llm_execution = LLMExecution(
        llm_called=True,
        response_received=True,
        response_used_as_final=False,
        raw_llm_response="Real LLM response"
    )
    # Content body doesn't match and response wasn't used as final
    state.generated_content = GeneratedContent(body="Hardcoded content replacing LLM")
    
    result = verify_llm_output(state)
    assert result["verification"].verification_status == "PARTIALLY_LLM_GENERATED"


def test_verification_missing_evidence():
    """Test 6 — Missing execution evidence: UNVERIFIED"""
    state = MarketingAgentState(user_input="test")
    # No llm_execution present in state
    state.llm_execution = None
    state.generated_content = GeneratedContent(body="Some content")
    
    result = verify_llm_output(state)
    assert result["verification"].verification_status == "UNVERIFIED"

@pytest.mark.asyncio
@patch("app.langchain.llm.ChatOllama.ainvoke")
async def test_dynamic_verification_phrase(mock_ainvoke):
    """Test dynamic generation with unique verification phrase."""
    # Mock the LLM response
    mock_ainvoke.return_value = AIMessage(content="Here is your marketing post for ZX-8472 Quantum Bottle. LLM-VERIFY-92831")

    # We call generate_content node and then verify_llm_output
    state = MarketingAgentState(
        user_input='Create a marketing post for a fictional product named "ZX-8472 Quantum Bottle". Include the unique verification phrase: "LLM-VERIFY-92831".'
    )
    
    # Run content node
    result_content = await generate_content(state)
    
    # Ensure no error
    assert result_content.get("status") != "failed"
    
    # Update state
    state.generated_content = result_content["generated_content"]
    state.llm_execution = result_content["llm_execution"]
    
    # Run verification node
    result_verify = verify_llm_output(state)
    verif_status = result_verify["verification"]
    
    # Verification checks
    assert verif_status.llm_invoked is True
    assert verif_status.response_received is True
    assert verif_status.verification_status == "VERIFIED_LLM"
    assert "LLM-VERIFY-92831" in state.generated_content.body
    
    # Ensure provider is set properly
    assert verif_status.provider == "ollama"
    assert verif_status.model is not None
