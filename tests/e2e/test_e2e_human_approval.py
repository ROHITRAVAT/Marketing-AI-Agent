import pytest
import uuid
from httpx import AsyncClient
from langgraph.checkpoint.memory import MemorySaver
from app.agents.graph import build_marketing_graph
from app.agents.state import MarketingAgentState
from app.agents.enums import AgentStatus, ApprovalStatus
from app.models.approval import ApprovalRequest
from unittest.mock import patch
from app.models.user import User

pytestmark = pytest.mark.asyncio

@pytest.fixture
def memory_saver():
    return MemorySaver()

@pytest.fixture
def graph_with_checkpointer(memory_saver):
    graph = build_marketing_graph()
    graph.checkpointer = memory_saver
    return graph

async def test_human_approval_workflow_e2e(e2e_client: AsyncClient, e2e_seeded_user: User, memory_saver, graph_with_checkpointer, e2e_db_session):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # 1. Start Workflow
    state = MarketingAgentState(
        user_input="Create a LinkedIn post.",
        platform="LinkedIn",
        product="AI",
        target_audience="Developers",
        campaign_goal="Testing",
        user_id=e2e_seeded_user.id
    )
    
    from contextlib import asynccontextmanager
    
    @asynccontextmanager
    async def mock_db_session():
        yield e2e_db_session

    with patch("app.agents.nodes.approval.AsyncSessionLocal", mock_db_session):
        try:
            result = await graph_with_checkpointer.ainvoke(state, config)
        except Exception:
            pass # GraphInterrupt may be raised depending on langgraph version/runner

        # 2. Verify Approval Request is retrievable via API
        response = await e2e_client.get("/api/v1/approvals/pending")
        assert response.status_code == 200
        pending_approvals = response.json()["items"]
        assert len(pending_approvals) > 0
        
        # Get the latest approval request
        approval_id = pending_approvals[0]["id"]
        
        # 3. Approve via API
        @asynccontextmanager
        async def mock_get_checkpointer():
            yield memory_saver
            
        with patch("app.services.approval_service.get_checkpointer", mock_get_checkpointer):
            with patch("app.agents.graph.execute_tools") as mock_tools:
                mock_tools.return_value = {"status": AgentStatus.COMPLETED, "tool_results": [{"tool": "linkedin", "status": "success"}]}
                
                approve_response = await e2e_client.post(
                    f"/api/v1/approvals/{approval_id}/approve",
                    json={"reason": "Looks perfect!"}
                )
                assert approve_response.status_code == 200
                
                # 4. Verify graph resumed and finished
                final_state = memory_saver.get_tuple(config).checkpoint["channel_values"]
                assert final_state["status"] == AgentStatus.COMPLETED
                assert final_state["approval_status"].value == "approved"

async def test_human_approval_rejection_e2e(e2e_client: AsyncClient, e2e_seeded_user: User, memory_saver, graph_with_checkpointer, e2e_db_session):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    state = MarketingAgentState(
        user_input="Create a Facebook post.",
        platform="Facebook",
        product="AI",
        target_audience="Developers",
        campaign_goal="Testing",
        user_id=e2e_seeded_user.id
    )
    
    from contextlib import asynccontextmanager
    
    @asynccontextmanager
    async def mock_db_session():
        yield e2e_db_session

    with patch("app.agents.nodes.approval.AsyncSessionLocal", mock_db_session):
        try:
            result = await graph_with_checkpointer.ainvoke(state, config)
        except Exception:
            pass # GraphInterrupt may be raised depending on langgraph version/runner
            
        # Get the latest approval request
        response = await e2e_client.get("/api/v1/approvals/pending")
        pending_approvals = response.json()["items"]
        approval_id = pending_approvals[0]["id"]
        
        @asynccontextmanager
        async def mock_get_checkpointer():
            yield memory_saver
            
        with patch("app.services.approval_service.get_checkpointer", mock_get_checkpointer):
            with patch("app.agents.graph.execute_tools") as mock_tools:
                # 3. Reject via API
                reject_response = await e2e_client.post(
                    f"/api/v1/approvals/{approval_id}/reject",
                    json={"reason": "Not the right tone."}
                )
                assert reject_response.status_code == 200
                
                # Tools should NOT be executed
                mock_tools.assert_not_called()
                
                final_state = memory_saver.get_tuple(config).checkpoint["channel_values"]
                # After rejection, graph might be routing to handle_error or final response
                assert final_state["approval_status"].value == "rejected"
                assert final_state["status"] in [AgentStatus.FAILED, AgentStatus.COMPLETED]
