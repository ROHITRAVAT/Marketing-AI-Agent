"""Ollama connectivity tests.

Requires the Ollama container to be running and reachable.

Run inside the backend container (FastAPI -> Ollama over the Docker network):
    docker compose exec backend pytest tests/test_ollama_connection.py -v

The model list is expected to be empty — no model is downloaded in this
infrastructure task (Qwen 3 is installed in a separate task).
"""

import pytest

from app.core.config import OLLAMA_TIMEOUT, OLLAMA_URL
from app.ollama.client import build_async_client
from app.ollama.service import OllamaService


@pytest.fixture
async def ollama_service():
    """OllamaService bound to a per-test httpx client; skips if unreachable."""
    client = build_async_client()
    service = OllamaService(client, timeout=OLLAMA_TIMEOUT)
    try:
        await service.check_connection()
    except Exception as exc:  # pragma: no cover - env not started
        await client.aclose()
        pytest.skip(f"Ollama unreachable at {OLLAMA_URL}: {exc}")
    yield service
    await client.aclose()


@pytest.mark.asyncio
async def test_ollama_connectivity(ollama_service):
    """Ollama is reachable through the configured URL."""
    assert await ollama_service.check_connection() is True


@pytest.mark.asyncio
async def test_list_models_returns_expected_empty_list(ollama_service):
    """list_models() returns a list that is empty (no model is downloaded yet)."""
    models = await ollama_service.list_models()
    assert isinstance(models, list)
    assert models == [], (
        "Expected no Ollama model to be installed yet — Qwen 3 is installed "
        "in a separate task"
    )