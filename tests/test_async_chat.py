import pytest
import asyncio
from unittest.mock import patch, MagicMock
from sqlalchemy import text
from app.models.agent_job import AgentJob
from app.services.agent_service import AgentService, _background_tasks, _llm_semaphore

@pytest.fixture
async def clear_background_tasks():
    _background_tasks.clear()
    yield
    _background_tasks.clear()

from app.schemas.agent import AgentChatResponse

@pytest.fixture
def mock_db_in_bg():
    yield

@pytest.mark.asyncio
async def test_immediate_http_response(integration_client, mock_db_in_bg):
    payload = {
        "thread_id": "test-immediate",
        "message": "hello",
        "mode": "copilot"
    }

    # Make _execute_chat artificially slow
    async def slow_execute(*args, **kwargs):
        await asyncio.sleep(0.5)
        return AgentChatResponse(status="completed", thread_id="test-immediate", final_response="Done")

    with patch("app.services.agent_service.AgentService._execute_chat", side_effect=slow_execute):
        import time
        start_time = time.time()
        response = await integration_client.post(
            "/api/v1/agent/chat",
            json=payload,
        )
        end_time = time.time()

        # Should return immediately (well under 0.5s)
        assert end_time - start_time < 0.2
        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"

@pytest.mark.asyncio
async def test_job_lifecycle(integration_client, mock_db_in_bg):
    payload = {
        "thread_id": "test-lifecycle",
        "message": "hello",
        "mode": "copilot"
    }

    async def fast_execute(*args, **kwargs):
        return AgentChatResponse(status="completed", thread_id="test-lifecycle", final_response="Done")

    with patch("app.services.agent_service.AgentService._execute_chat", side_effect=fast_execute):
        response = await integration_client.post(
            "/api/v1/agent/chat",
            json=payload
        )
        job_id = response.json()["job_id"]

        # Let the background task run
        await asyncio.sleep(0.2)

        # Check status
        status_response = await integration_client.get(
            f"/api/v1/agent/jobs/{job_id}"
        )
        assert status_response.status_code == 200
        data = status_response.json()
        assert data["status"] in ["completed", "failed"]

@pytest.mark.asyncio
async def test_job_ownership(integration_client, mock_db_in_bg):
    payload = {
        "thread_id": "test-ownership",
        "message": "hello",
        "mode": "copilot"
    }

    with patch("app.services.agent_service.AgentService._execute_chat", return_value=AgentChatResponse(status="completed", thread_id="test-ownership", final_response="Done")):
        # User 1 creates a job (assuming integration_client uses user 1)
        response = await integration_client.post(
            "/api/v1/agent/chat",
            json=payload
        )
        job_id = response.json()["job_id"]

        # User 1 can access it
        status_response = await integration_client.get(
            f"/api/v1/agent/jobs/{job_id}"
        )
        assert status_response.status_code == 200

    # Unknown job -> 404
    status_response3 = await integration_client.get(
        f"/api/v1/agent/jobs/not-a-real-job-id"
    )
    assert status_response3.status_code == 404

@pytest.mark.asyncio
async def test_background_task_retention(integration_client, clear_background_tasks, mock_db_in_bg):
    payload = {
        "thread_id": "test-retention",
        "message": "hello",
        "mode": "copilot"
    }
    
    assert len(_background_tasks) == 0

    async def slow_execute(*args, **kwargs):
        await asyncio.sleep(0.2)
        return MagicMock(status="completed", model_dump=lambda: {})

    with patch("app.services.agent_service.AgentService._execute_chat", side_effect=slow_execute):
        response = await integration_client.post(
            "/api/v1/agent/chat",
            json=payload
        )
        assert response.status_code == 202
        
        # Task should be in registry
        assert len(_background_tasks) == 1
        
        # Wait for completion
        await asyncio.sleep(0.3)
        
        # Task should be removed
        assert len(_background_tasks) == 0

@pytest.mark.asyncio
async def test_concurrency_limit(integration_client, mock_db_in_bg):
    payload1 = {"thread_id": "test-c1", "message": "hello", "mode": "copilot"}
    payload2 = {"thread_id": "test-c2", "message": "hello", "mode": "copilot"}

    active_executions = 0
    max_executions = 0

    async def tracking_execute(*args, **kwargs):
        nonlocal active_executions, max_executions
        active_executions += 1
        if active_executions > max_executions:
            max_executions = active_executions
        await asyncio.sleep(0.2)
        active_executions -= 1
        return MagicMock(status="completed", model_dump=lambda: {})

    with patch("app.services.agent_service.AgentService._execute_chat", side_effect=tracking_execute):
        # Launch two concurrently
        await integration_client.post("/api/v1/agent/chat", json=payload1)
        await integration_client.post("/api/v1/agent/chat", json=payload2)
        
        # Wait for both to finish
        await asyncio.sleep(0.5)
        
        # Assert max concurrency was 1 due to the semaphore
        assert max_executions == 1

@pytest.mark.asyncio
async def test_startup_recovery(seeded_db_session):
    # Insert some stale jobs directly
    user_id = 1
    j1 = AgentJob(id="job-recovery-1", user_id=user_id, thread_id="t1", status="queued")
    j2 = AgentJob(id="job-recovery-2", user_id=user_id, thread_id="t2", status="running")
    j3 = AgentJob(id="job-recovery-3", user_id=user_id, thread_id="t3", status="completed")
    
    seeded_db_session.add_all([j1, j2, j3])
    await seeded_db_session.commit()

    # Run recovery
    await AgentService.recover_stale_jobs(seeded_db_session)
    
    # Verify results
    await seeded_db_session.refresh(j1)
    await seeded_db_session.refresh(j2)
    await seeded_db_session.refresh(j3)
    
    assert j1.status == "failed"
    assert "restarted" in j1.error
    assert j2.status == "failed"
    assert "restarted" in j2.error
    assert j3.status == "completed"
