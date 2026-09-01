import importlib

import httpx
import pytest
from fastapi.testclient import TestClient

import app.core.config as core_config
import app.ollama.config as ollama_config
import app.ollama.service as ollama_service
from app.main import app
from app.ollama.service import OllamaService
from app.ollama.service import get_ollama_service


def test_default_ollama_model_is_qwen3(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "qwen3")

    importlib.reload(core_config)
    importlib.reload(ollama_config)
    importlib.reload(ollama_service)

    assert ollama_service.OLLAMA_SETTINGS.model == "qwen3"


@pytest.mark.asyncio
async def test_ollama_service_generate_returns_model_response(monkeypatch):
    async def fake_post(self, path, json=None):
        assert path == "/api/generate"
        assert json["model"] == "llama3.2"
        assert json["prompt"] == "Say hello"
        assert json["stream"] is False
        request = httpx.Request("POST", "http://ollama:11434/api/generate")
        response = httpx.Response(200, request=request, json={"model": "llama3.2", "response": "Hello from Ollama"})
        return response

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    service = OllamaService(httpx.AsyncClient(base_url="http://ollama:11434"), timeout=5)

    result = await service.generate("Say hello", model="llama3.2")

    assert result == "Hello from Ollama"
    await service.client.aclose()


def test_ollama_generate_endpoint_returns_inference_result():
    class FakeOllamaService:
        async def generate(self, prompt: str, *, model: str | None = None, **options):
            assert prompt == "Write a greeting"
            assert model == "llama3.2"
            return "Hello from Ollama"

    app.dependency_overrides[get_ollama_service] = lambda: FakeOllamaService()
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/ollama/generate",
                json={"prompt": "Write a greeting", "model": "llama3.2"},
            )

        assert response.status_code == 200
        assert response.json()["response"] == "Hello from Ollama"
        assert response.json()["model"] == "llama3.2"
    finally:
        app.dependency_overrides.clear()
