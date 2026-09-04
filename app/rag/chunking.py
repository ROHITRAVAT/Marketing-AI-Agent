"""Text chunking for RAG ingestion.

Splits document content into overlapping chunks sized for the embedding
model (all-minilm handles short-to-medium chunks well). Overlap preserves
context across chunk boundaries so a fact split across two chunks isn't lost.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.rag.loaders import LoadedDocument


@dataclass
class Chunk:
    """A single chunk of a document, ready for embedding."""

    content: str
    document_id: str
    source_type: str
    chunk_index: int
    metadata: dict


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[str]:
    """Split text into overlapping chunks by character count.

    Splits on whitespace boundaries where possible so words aren't cut
    mid-token, which matters for embedding quality.
    """
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # Try to break on a word boundary rather than mid-word, unless
        # we're at the very end of the text.
        if end < text_len:
            last_space = text.rfind(" ", start, end)
            if last_space > start:
                end = last_space

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_len:
            break

        start = end - chunk_overlap

    return chunks


def chunk_document(
    document: LoadedDocument,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[Chunk]:
    """Chunk a LoadedDocument, carrying forward its metadata onto each chunk."""
    text_chunks = chunk_text(document.content, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    return [
        Chunk(
            content=text_chunk,
            document_id=document.document_id,
            source_type=document.source_type,
            chunk_index=i,
            metadata=document.metadata,
        )
        for i, text_chunk in enumerate(text_chunks)
    ]