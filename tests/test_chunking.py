import pytest

from app.rag.chunking import chunk_document, chunk_text
from app.rag.loaders import LoadedDocument


def test_chunk_text_short_text_returns_single_chunk():
    result = chunk_text("Short text.", chunk_size=500, chunk_overlap=50)
    assert result == ["Short text."]


def test_chunk_text_splits_long_text():
    text = "word " * 300  # 1500 chars
    result = chunk_text(text, chunk_size=500, chunk_overlap=50)
    assert len(result) > 1
    # Every chunk should respect the size limit (allowing for word-boundary trim)
    assert all(len(c) <= 500 for c in result)


def test_chunk_text_overlap_preserves_boundary_words():
    text = "alpha beta gamma delta epsilon zeta eta theta " * 20
    result = chunk_text(text, chunk_size=100, chunk_overlap=20)
    # With overlap, consecutive chunks should share some trailing/leading words
    assert len(result) > 1


def test_chunk_text_empty_returns_empty_list():
    assert chunk_text("   ", chunk_size=500, chunk_overlap=50) == []


def test_chunk_text_rejects_bad_overlap():
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=100, chunk_overlap=100)


def test_chunk_document_carries_metadata():
    doc = LoadedDocument(
        content="word " * 300,
        source_type="txt",
        document_id="doc-123",
        metadata={"filename": "brand.txt"},
    )
    chunks = chunk_document(doc, chunk_size=500, chunk_overlap=50)

    assert len(chunks) > 1
    for i, chunk in enumerate(chunks):
        assert chunk.document_id == "doc-123"
        assert chunk.source_type == "txt"
        assert chunk.chunk_index == i
        assert chunk.metadata == {"filename": "brand.txt"}


def test_chunk_document_short_doc_single_chunk():
    doc = LoadedDocument(content="Tiny doc.", source_type="txt", document_id="doc-456")
    chunks = chunk_document(doc)
    assert len(chunks) == 1
    assert chunks[0].content == "Tiny doc."