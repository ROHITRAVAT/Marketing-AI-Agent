import pytest
import asyncio
from unittest.mock import patch, MagicMock
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from app.main import app
from app.models.agent_job import AgentJob
from app.models.user import User
from app.services.agent_service import AgentService, _background_tasks, _llm_semaphore, _is_shutting_down
from app.schemas.agent import AgentChatResponse

@pytest.fixture(autouse=True)
def reset_agent_service_state():
    """Ensure clean background tasks and shutdown state before and after each test."""
    import app.services.agent_service as svc
    svc._background_tasks.clear()
    svc._is_shutting_down = False
    yield
    svc._background_tasks.clear()
    svc._is_shutting_down = False

@pytest.fixture
def mock_db_in_bg():
    yield

@pytest.mark.asyncio
async def test_immediate_http_response(integration_client, mock_db_in_bg):
    """
    Verify POST /api/v1/agent/chat returns immediately (HTTP 202)
    without leaving background tasks running when the test finishes.
    """
    payload = {
        "thread_id": "test-immediate",
        "message": "hello",
        "mode": "copilot"
    }

    started_event = asyncio.Event()
    finish_event = asyncio.Event()

    async def controlled_execute(*args, **kwargs):
        started_event.set()
        await finish_event.wait()
        return AgentChatResponse(status="completed", thread_id="test-immediate", final_response="Done")

    with patch("app.services.agent_service.AgentService._execute_chat", side_effect=controlled_execute):
        import time
        start_time = time.time()
        response = await integration_client.post(
            "/api/v1/agent/chat",
            json=payload,
        )
        end_time = time.time()

        # Should return immediately (well under 0.2s)
        assert end_time - start_time < 0.2
        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"

        # Explicit test synchronization: await the execution start, then release it
        await asyncio.wait_for(started_event.wait(), timeout=2.0)
        finish_event.set()

        # Cleanly await background tasks so no unawaited coroutines outlive the test
        if _background_tasks:
            await asyncio.wait(list(_background_tasks), timeout=2.0)

@pytest.mark.asyncio
async def test_job_lifecycle(integration_client, mock_db_in_bg):
    """Verify job transitions from queued -> running -> completed."""
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
        assert response.status_code == 202
        job_id = response.json()["job_id"]

        # Wait for the background task to complete cleanly
        if _background_tasks:
            await asyncio.wait(list(_background_tasks), timeout=2.0)

        # Check status
        status_response = await integration_client.get(
            f"/api/v1/agent/jobs/{job_id}"
        )
        assert status_response.status_code == 200
        data = status_response.json()
        assert data["status"] == "completed"
        assert data["result"]["final_response"] == "Done"

@pytest.mark.asyncio
async def test_job_ownership(integration_client, seeded_db_session, mock_db_in_bg):
    """
    Verify job ownership enforcement:
    1. User A requests own job -> 200 OK
    2. User A requests User B's job -> 404 Not Found
    3. User requests nonexistent job -> 404 Not Found
    4. Unauthenticated request -> 401/403 status
    """
    # 1. User 1 creates a job
    payload = {
        "thread_id": "test-ownership-u1",
        "message": "hello from user 1",
        "mode": "copilot"
    }

    with patch("app.services.agent_service.AgentService._execute_chat", return_value=AgentChatResponse(status="completed", thread_id="test-ownership-u1", final_response="Done")):
        response = await integration_client.post("/api/v1/agent/chat", json=payload)
        assert response.status_code == 202
        u1_job_id = response.json()["job_id"]

        if _background_tasks:
            await asyncio.wait(list(_background_tasks), timeout=2.0)

        # User 1 requests own job -> 200 OK
        resp_own = await integration_client.get(f"/api/v1/agent/jobs/{u1_job_id}")
        assert resp_own.status_code == 200
        assert resp_own.json()["job_id"] == u1_job_id

    # 2. Seed a second user and create a job owned by User 2
    u2 = User(id=2, email="user2@test.com", username="user2", hashed_password="pw")
    seeded_db_session.add(u2)
    u2_job = AgentJob(
        id="user2-secret-job-id",
        user_id=2,
        thread_id="test-thread-u2",
        status="completed",
        result={"status": "completed", "thread_id": "test-thread-u2", "final_response": "Secret User 2 result"}
    )
    seeded_db_session.add(u2_job)
    await seeded_db_session.commit()

    # User 1 attempts to access User 2's job -> 404 Not Found (no data leakage)
    resp_other = await integration_client.get(f"/api/v1/agent/jobs/{u2_job.id}")
    assert resp_other.status_code == 404
    assert resp_other.json()["detail"] == "Job not found"

    # 3. User requests a nonexistent job -> 404 Not Found
    resp_nonexistent = await integration_client.get("/api/v1/agent/jobs/nonexistent-job-uuid")
    assert resp_nonexistent.status_code == 404
    assert resp_nonexistent.json()["detail"] == "Job not found"

    # 4. Unauthenticated request -> existing authentication rejection
    from app.dependencies.auth import get_current_user as auth_get_current_user
    from app.api.deps import get_current_user as deps_get_current_user
    
    saved_auth = app.dependency_overrides.get(auth_get_current_user)
    saved_deps = app.dependency_overrides.get(deps_get_current_user)
    try:
        app.dependency_overrides.pop(auth_get_current_user, None)
        app.dependency_overrides.pop(deps_get_current_user, None)
        
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as unauth_client:
            resp_unauth = await unauth_client.get(f"/api/v1/agent/jobs/{u1_job_id}")
            assert resp_unauth.status_code in [401, 403]
    finally:
        if saved_auth:
            app.dependency_overrides[auth_get_current_user] = saved_auth
        if saved_deps:
            app.dependency_overrides[deps_get_current_user] = saved_deps

@pytest.mark.asyncio
async def test_background_task_retention(integration_client, mock_db_in_bg):
    """Verify strong references are retained while running and discarded on completion."""
    payload = {
        "thread_id": "test-retention",
        "message": "hello",
        "mode": "copilot"
    }
    
    assert len(_background_tasks) == 0

    finish_event = asyncio.Event()

    async def controlled_execute(*args, **kwargs):
        await finish_event.wait()
        return MagicMock(status="completed", model_dump=lambda: {})

    with patch("app.services.agent_service.AgentService._execute_chat", side_effect=controlled_execute):
        response = await integration_client.post(
            "/api/v1/agent/chat",
            json=payload
        )
        assert response.status_code == 202
        
        # Task should be present in registry while running
        assert len(_background_tasks) == 1
        
        # Release the task
        finish_event.set()
        await asyncio.wait(list(_background_tasks), timeout=2.0)
        
        # Task should be cleanly removed from registry
        assert len(_background_tasks) == 0

@pytest.mark.asyncio
async def test_worker_exception_handling(integration_client, mock_db_in_bg):
    """Verify worker exceptions are observed, logged, and mark the job failed."""
    payload = {
        "thread_id": "test-failure",
        "message": "hello",
        "mode": "copilot"
    }

    async def failing_execute(*args, **kwargs):
        raise RuntimeError("Ollama inference engine crashed with token=secret123")

    with patch("app.services.agent_service.AgentService._execute_chat", side_effect=failing_execute):
        response = await integration_client.post("/api/v1/agent/chat", json=payload)
        assert response.status_code == 202
        job_id = response.json()["job_id"]

        if _background_tasks:
            await asyncio.wait(list(_background_tasks), timeout=2.0)

        status_response = await integration_client.get(f"/api/v1/agent/jobs/{job_id}")
        assert status_response.status_code == 200
        data = status_response.json()
        assert data["status"] == "failed"
        # Verify secret was sanitized
        assert "secret123" not in data["error"]
        assert "[REDACTED]" in data["error"]

@pytest.mark.asyncio
async def test_concurrency_limit(integration_client, mock_db_in_bg):
    """Verify asyncio.Semaphore limits CPU LLM execution to configured concurrency."""
    payload1 = {"thread_id": "test-c1", "message": "hello", "mode": "copilot"}
    payload2 = {"thread_id": "test-c2", "message": "hello", "mode": "copilot"}

    active_executions = 0
    max_executions = 0

    async def tracking_execute(*args, **kwargs):
        nonlocal active_executions, max_executions
        active_executions += 1
        if active_executions > max_executions:
            max_executions = active_executions
        await asyncio.sleep(0.15)
        active_executions -= 1
        return MagicMock(status="completed", model_dump=lambda: {})

    with patch("app.services.agent_service.AgentService._execute_chat", side_effect=tracking_execute):
        # Launch two concurrently
        await integration_client.post("/api/v1/agent/chat", json=payload1)
        await integration_client.post("/api/v1/agent/chat", json=payload2)
        
        # Wait for both to finish cleanly
        if _background_tasks:
            await asyncio.wait(list(_background_tasks), timeout=2.0)
        
        # Concurrency must not exceed 1
        assert max_executions == 1

@pytest.mark.asyncio
async def test_graceful_shutdown(integration_client, mock_db_in_bg):
    """Verify shutdown cancels running tasks, marks jobs failed, and stops accepting new work."""
    payload = {"thread_id": "test-shutdown", "message": "hello", "mode": "copilot"}
    block_event = asyncio.Event()

    async def long_execute(*args, **kwargs):
        await block_event.wait()
        return MagicMock(status="completed", model_dump=lambda: {})

    with patch("app.services.agent_service.AgentService._execute_chat", side_effect=long_execute):
        response = await integration_client.post("/api/v1/agent/chat", json=payload)
        assert response.status_code == 202
        job_id = response.json()["job_id"]

        # Run shutdown with a short timeout
        await AgentService.shutdown_background_tasks(timeout=0.1)

        # After shutdown, new job submission is rejected
        rejected_resp = await integration_client.post("/api/v1/agent/chat", json=payload)
        assert rejected_resp.status_code == 503

        # Interrupted job should be marked failed
        status_resp = await integration_client.get(f"/api/v1/agent/jobs/{job_id}")
        assert status_resp.status_code == 200
        assert status_resp.json()["status"] == "failed"
        assert "interrupted" in status_resp.json()["error"].lower()

@pytest.mark.asyncio
async def test_startup_recovery(seeded_db_session):
    """Verify startup recovery marks queued/running jobs as failed and leaves completed intact."""
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
