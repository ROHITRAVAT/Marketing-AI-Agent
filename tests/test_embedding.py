import pytest
from unittest.mock import AsyncMock

from app.rag.embedding import build_point, ingest_document
from app.rag.loaders import LoadedDocument


def test_build_point_includes_filterable_payload():
    from app.rag.chunking import Chunk

    chunk = Chunk(
        content="Our summer sale starts in June.",
        document_id="doc-1",
        source_type="txt",
        chunk_index=0,
        metadata={"filename": "sale.txt"},
    )
    vector = [0.1, 0.2, 0.3]

    point = build_point(chunk, vector, knowledge_type="campaign", user_id="user-42")

    assert point.vector == vector
    assert point.payload["content"] == "Our summer sale starts in June."
    assert point.payload["document_id"] == "doc-1"
    assert point.payload["source_type"] == "txt"
    assert point.payload["knowledge_type"] == "campaign"
    assert point.payload["user_id"] == "user-42"
    assert point.payload["filename"] == "sale.txt"


@pytest.mark.asyncio
async def test_ingest_document_embeds_and_stores_all_chunks():
    document = LoadedDocument(
        content="word " * 300,  # long enough to produce multiple chunks
        source_type="txt",
        document_id="doc-99",
        metadata={"filename": "brand.txt"},
    )

    mock_ollama = AsyncMock()
    mock_ollama.embed.return_value = [0.1] * 384  # matches all-minilm dimension

    mock_qdrant = AsyncMock()

    result = await ingest_document(
        document,
        knowledge_type="brand_knowledge",
        user_id="user-1",
        ollama_service=mock_ollama,
        qdrant_service=mock_qdrant,
    )

    assert result.document_id == "doc-99"
    assert result.chunks_created > 1
    assert result.chunks_stored == result.chunks_created
    assert mock_ollama.embed.call_count == result.chunks_created
    mock_qdrant.insert_points.assert_called_once()


@pytest.mark.asyncio
async def test_ingest_document_empty_content_stores_nothing():
    document = LoadedDocument(content="   ", source_type="txt", document_id="doc-empty")

    mock_ollama = AsyncMock()
    mock_qdrant = AsyncMock()

    result = await ingest_document(
        document,
        knowledge_type="brand_knowledge",
        ollama_service=mock_ollama,
        qdrant_service=mock_qdrant,
    )

    assert result.chunks_created == 0
    assert result.chunks_stored == 0
    mock_ollama.embed.assert_not_called()
    mock_qdrant.insert_points.assert_not_called()
