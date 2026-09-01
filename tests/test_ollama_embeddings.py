import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock

from app.ollama.service import OllamaService
from app.ollama.config import OllamaSettings


@pytest.fixture
def mock_httpx_client():
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def ollama_service(mock_httpx_client):
    return OllamaService(client=mock_httpx_client, timeout=5.0)


@pytest.mark.asyncio
async def test_embed_success(ollama_service, mock_httpx_client):
    # Setup
    mock_response = MagicMock()
    mock_response.json.return_value = {"embedding": [0.1, 0.2, 0.3]}
    mock_httpx_client.post.return_value = mock_response

    # Execute
    result = await ollama_service.embed("Hello world", model="test-model")

    # Verify
    assert result == [0.1, 0.2, 0.3]
    mock_httpx_client.post.assert_called_once_with(
        "/api/embeddings",
        json={"model": "test-model", "prompt": "Hello world"}
    )


@pytest.mark.asyncio
async def test_embed_missing_model(mock_httpx_client):
    # Setup service with empty embedding model
    with pytest.MonkeyPatch.context() as mp:
        import app.ollama.service
        mp.setattr(app.ollama.service, "OLLAMA_SETTINGS", OllamaSettings(embedding_model=""))
        
        service = app.ollama.service.OllamaService(client=mock_httpx_client)

        # Execute & Verify
        with pytest.raises(ValueError, match="No Ollama embedding model configured"):
            await service.embed("Hello world")


@pytest.mark.asyncio
async def test_embed_http_failure(ollama_service, mock_httpx_client):
    # Setup
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Error", request=MagicMock(), response=mock_response)
    mock_httpx_client.post.return_value = mock_response

    # Execute & Verify
    with pytest.raises(httpx.HTTPStatusError):
        await ollama_service.embed("Hello world", model="test-model")
