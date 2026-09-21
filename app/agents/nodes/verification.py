from app.agents.state import MarketingAgentState
from app.agents.schemas import VerificationStatus

def verify_llm_output(state: MarketingAgentState) -> dict:
    """
    Verify whether the generated content is from an actual LLM execution.
    """
    verification = VerificationStatus()

    llm_exec = state.llm_execution
    content = state.generated_content

    if not llm_exec or not content:
        verification.verification_status = "UNVERIFIED"
        verification.issues.append("No LLM execution evidence or generated content was provided.")
        return {"verification": verification}

    verification.llm_invoked = llm_exec.llm_called
    verification.provider = llm_exec.provider
    verification.model = llm_exec.model
    verification.node = llm_exec.node_name
    verification.response_received = llm_exec.response_received
    verification.response_used_as_final = llm_exec.response_used_as_final

    if llm_exec.llm_called:
        verification.evidence.append("LLM invocation was explicitly recorded.")
    if llm_exec.response_received:
        verification.evidence.append("LLM response was received.")
    if llm_exec.response_used_as_final:
        verification.evidence.append("Final generated content matches the LLM response.")

    # Check for hardcoded mock content
    mock_keywords = ["mock", "dummy", "sample", "test", "placeholder", "fake", "MagicMock"]
    has_mock = False
    if content.body:
        lower_body = content.body.lower()
        has_mock = any(k.lower() in lower_body for k in mock_keywords)

    verification.mock_content_detected = has_mock
    
    # In a real app we might have fallback content detected explicitly
    verification.fallback_content_detected = llm_exec.llm_called and not llm_exec.response_received and bool(content.body)
    
    # Hardcoded detection could be based on whether it was used as final and not from LLM
    verification.hardcoded_content_detected = False
    if not llm_exec.response_used_as_final and bool(content.body):
        verification.hardcoded_content_detected = True

    if has_mock:
        verification.verification_status = "MOCK_CONTENT"
        verification.confidence = 0.95
    elif verification.fallback_content_detected:
        verification.verification_status = "FALLBACK_CONTENT"
        verification.confidence = 0.95
    elif verification.hardcoded_content_detected and not llm_exec.response_received:
        verification.verification_status = "HARD_CODED"
        verification.confidence = 0.95
    elif verification.hardcoded_content_detected and llm_exec.response_received:
        verification.verification_status = "PARTIALLY_LLM_GENERATED"
        verification.confidence = 0.8
    elif llm_exec.llm_called and llm_exec.response_received and llm_exec.response_used_as_final:
        verification.verification_status = "VERIFIED_LLM"
        verification.confidence = 0.95
    else:
        verification.verification_status = "UNVERIFIED"
        verification.confidence = 0.0

    return {"verification": verification}
