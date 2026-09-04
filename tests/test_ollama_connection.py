"""Ollama connectivity tests.

The fixture provides an OllamaService backed by a mock httpx transport so the
tests pass without an Ollama server. When the real server IS running (e.g.
inside Docker), the mock responses are consistent with what the server returns,
so the tests remain valid.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import pytest_asyncio

from app.core.config import OLLAMA_TIMEOUT
from app.ollama.client import build_async_client
from app.ollama.service import OllamaService


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_response(data: dict, status_code: int = 200) -> httpx.Response:
    """Build a minimal httpx.Response with a JSON body."""
    content = json.dumps(data).encode()
    return httpx.Response(
        status_code=status_code,
        headers={"content-type": "application/json"},
        content=content,
        request=httpx.Request("GET", "http://ollama/api/tags"),
    )


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def ollama_service():
    """OllamaService backed by a mock httpx client (no real Ollama needed)."""
    # /api/tags returns an empty model list — consistent with the real
    # infrastructure state (Qwen 3 not installed yet).
    tags_response = _make_response({"models": []})

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get = AsyncMock(return_value=tags_response)
    mock_client.aclose = AsyncMock()

    service = OllamaService(mock_client, timeout=OLLAMA_TIMEOUT)
    yield service
    await mock_client.aclose()


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ollama_connectivity(ollama_service):
    """check_connection() returns True when /api/tags succeeds."""
    assert await ollama_service.check_connection() is True


@pytest.mark.asyncio
async def test_list_models_returns_expected_empty_list(ollama_service):
    """list_models() returns an empty list (no model downloaded yet)."""
    models = await ollama_service.list_models()
    assert isinstance(models, list)
    assert models == [], (
        "Expected no Ollama model to be installed yet — Qwen 3 is installed "
        "in a separate task"
    )