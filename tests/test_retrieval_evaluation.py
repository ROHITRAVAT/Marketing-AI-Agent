import pytest
from unittest.mock import AsyncMock

from app.rag.evaluation import RetrievalTestCase, evaluate_query, evaluate_retrieval, format_summary_report


def _mock_point(doc_id: str, score: float):
    point = AsyncMock()
    point.payload = {"document_id": doc_id}
    point.score = score
    point.id = doc_id
    return point


@pytest.mark.asyncio
async def test_evaluate_query_finds_expected_document():
    mock_ollama = AsyncMock()
    mock_ollama.embed.return_value = [0.1] * 384

    mock_qdrant = AsyncMock()
    mock_qdrant.search.return_value = [_mock_point("doc-1", 0.92), _mock_point("doc-2", 0.71)]

    test_case = RetrievalTestCase(query="running shoes", expected_document_ids=["doc-1"], label="shoes query")
    result = await evaluate_query(test_case, mock_ollama, mock_qdrant)

    assert result.expected_found is True
    assert result.found_at_rank == 1
    assert result.top_score == 0.92
    assert result.result_count == 2
    assert result.latency_ms >= 0


@pytest.mark.asyncio
async def test_evaluate_query_expected_document_not_found():
    mock_ollama = AsyncMock()
    mock_ollama.embed.return_value = [0.1] * 384

    mock_qdrant = AsyncMock()
    mock_qdrant.search.return_value = [_mock_point("doc-9", 0.5)]

    test_case = RetrievalTestCase(query="unrelated query", expected_document_ids=["doc-1"])
    result = await evaluate_query(test_case, mock_ollama, mock_qdrant)

    assert result.expected_found is False
    assert result.found_at_rank is None


@pytest.mark.asyncio
async def test_evaluate_query_no_results():
    mock_ollama = AsyncMock()
    mock_ollama.embed.return_value = [0.1] * 384

    mock_qdrant = AsyncMock()
    mock_qdrant.search.return_value = []

    test_case = RetrievalTestCase(query="empty collection query", expected_document_ids=["doc-1"])
    result = await evaluate_query(test_case, mock_ollama, mock_qdrant)

    assert result.expected_found is False
    assert result.top_score is None
    assert result.result_count == 0


@pytest.mark.asyncio
async def test_evaluate_retrieval_computes_recall_and_latency():
    mock_ollama = AsyncMock()
    mock_ollama.embed.return_value = [0.1] * 384

    mock_qdrant = AsyncMock()
    mock_qdrant.search.side_effect = [
        [_mock_point("doc-1", 0.9)],  # found
        [_mock_point("doc-9", 0.4)],  # not found
    ]

    test_cases = [
        RetrievalTestCase(query="q1", expected_document_ids=["doc-1"], label="case 1"),
        RetrievalTestCase(query="q2", expected_document_ids=["doc-2"], label="case 2"),
    ]

    summary = await evaluate_retrieval(test_cases, mock_ollama, mock_qdrant)

    assert summary.recall_at_k == 0.5
    assert len(summary.results) == 2
    assert summary.avg_latency_ms >= 0


@pytest.mark.asyncio
async def test_evaluate_retrieval_empty_test_cases():
    mock_ollama = AsyncMock()
    mock_qdrant = AsyncMock()

    summary = await evaluate_retrieval([], mock_ollama, mock_qdrant)

    assert summary.results == []
    assert summary.recall_at_k == 0.0


def test_format_summary_report_contains_key_metrics():
    from app.rag.evaluation import RetrievalEvalResult, RetrievalEvalSummary

    summary = RetrievalEvalSummary(
        results=[
            RetrievalEvalResult(
                query="test query",
                label="case 1",
                latency_ms=45.2,
                top_score=0.88,
                result_count=3,
                expected_found=True,
                found_at_rank=1,
            )
        ],
        recall_at_k=1.0,
        avg_latency_ms=45.2,
        p95_latency_ms=45.2,
        avg_top_score=0.88,
    )

    report = format_summary_report(summary)
    assert "Recall@k" in report
    assert "100.0%" in report
    assert "case 1" in report
