"""Embedding pipeline: turns chunked documents into vectors stored in Qdrant.

Ties together app.rag.chunking (chunks) with app.ollama.service (embed) and
app.qdrant.service (store), so a document goes from raw file -> chunks ->
vectors -> searchable Qdrant points in one call.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass

from qdrant_client.models import PointStruct

from app.ollama.service import OllamaService, get_ollama_service
from app.qdrant.collections import COLLECTION_MARKETING_DOCUMENTS
from app.qdrant.service import QdrantService, get_qdrant_service
from app.rag.chunking import Chunk, chunk_document
from app.rag.loaders import LoadedDocument

logger = logging.getLogger(__name__)


@dataclass
class IngestResult:
    """Summary of an ingestion run, for logging/API responses."""

    document_id: str
    chunks_created: int
    chunks_stored: int


async def embed_chunk(chunk: Chunk, ollama_service: OllamaService) -> list[float]:
    """Generate an embedding vector for a single chunk's text content."""
    return await ollama_service.embed(chunk.content)


def build_point(
    chunk: Chunk,
    vector: list[float],
    *,
    knowledge_type: str,
    user_id: str | None = None,
) -> PointStruct:
    """Build a Qdrant point from a chunk + its vector, with filterable payload.

    Payload fields match the indices created in QdrantService.ensure_collections
    (document_id, source_type, knowledge_type, user_id) so retrieval can filter
    without scanning the whole collection.
    """
    return PointStruct(
        id=str(uuid.uuid4()),
        vector=vector,
        payload={
            "content": chunk.content,
            "document_id": chunk.document_id,
            "source_type": chunk.source_type,
            "knowledge_type": knowledge_type,
            "user_id": user_id,
            "chunk_index": chunk.chunk_index,
            **chunk.metadata,
        },
    )


async def ingest_document(
    document: LoadedDocument,
    *,
    knowledge_type: str,
    user_id: str | None = None,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    ollama_service: OllamaService | None = None,
    qdrant_service: QdrantService | None = None,
    collection_name: str = COLLECTION_MARKETING_DOCUMENTS,
) -> IngestResult:
    """Full ingestion pipeline: chunk -> embed -> store.

    ``knowledge_type`` is the caller's classification (e.g. "brand_knowledge",
    "campaign", "content") used later for filtered retrieval. Required, since
    there's no sensible default that wouldn't misclassify data.
    """
    ollama_service = ollama_service or get_ollama_service()
    qdrant_service = qdrant_service or get_qdrant_service()

    chunks = chunk_document(document, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    if not chunks:
        logger.warning("No chunks produced for document %s", document.document_id)
        return IngestResult(document.document_id, chunks_created=0, chunks_stored=0)

    points: list[PointStruct] = []
    for chunk in chunks:
        vector = await embed_chunk(chunk, ollama_service)
        points.append(build_point(chunk, vector, knowledge_type=knowledge_type, user_id=user_id))

    await qdrant_service.insert_points(collection_name, points)

    logger.info(
        "Ingested document %s: %d chunks embedded and stored",
        document.document_id,
        len(points),
    )
    return IngestResult(document.document_id, chunks_created=len(chunks), chunks_stored=len(points))