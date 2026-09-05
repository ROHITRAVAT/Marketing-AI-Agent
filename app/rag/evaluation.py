"""Evaluation utilities for the RAG retrieval pipeline.

Measures whether expected documents surface in results (recall@k), latency
(embed + search time), and basic quality signals (top similarity score).
Offline tooling — run manually or in CI to catch regressions as the
embedding model, chunking, or ingestion pipeline change over time.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

from app.ollama.service import OllamaService
from app.qdrant.collections import COLLECTION_MARKETING_DOCUMENTS
from app.qdrant.service import QdrantService


@dataclass
class RetrievalTestCase:
    """A query and the document(s) expected to surface for it."""

    query: str
    expected_document_ids: list[str]
    label: str = ""


@dataclass
class RetrievalEvalResult:
    query: str
    label: str
    latency_ms: float
    top_score: float | None
    result_count: int
    expected_found: bool
    found_at_rank: int | None


@dataclass
class RetrievalEvalSummary:
    results: list[RetrievalEvalResult]
    recall_at_k: float
    avg_latency_ms: float
    p95_latency_ms: float
    avg_top_score: float


async def evaluate_query(
    test_case: RetrievalTestCase,
    ollama_service: OllamaService,
    qdrant_service: QdrantService,
    *,
    limit: int = 5,
    collection_name: str = COLLECTION_MARKETING_DOCUMENTS,
) -> RetrievalEvalResult:
    """Run one retrieval query and score it against the expected document(s)."""
    start = time.perf_counter()

    query_vector = await ollama_service.embed(test_case.query)
    results = await qdrant_service.search(collection_name, query_vector, limit=limit)

    latency_ms = (time.perf_counter() - start) * 1000

    found_at_rank: int | None = None
    for rank, point in enumerate(results, start=1):
        payload = point.payload or {}
        doc_id = str(payload.get("document_id", point.id))
        if doc_id in test_case.expected_document_ids:
            found_at_rank = rank
            break

    top_score = float(results[0].score) if results else None

    return RetrievalEvalResult(
        query=test_case.query,
        label=test_case.label,
        latency_ms=latency_ms,
        top_score=top_score,
        result_count=len(results),
        expected_found=found_at_rank is not None,
        found_at_rank=found_at_rank,
    )


async def evaluate_retrieval(
    test_cases: list[RetrievalTestCase],
    ollama_service: OllamaService,
    qdrant_service: QdrantService,
    *,
    limit: int = 5,
    collection_name: str = COLLECTION_MARKETING_DOCUMENTS,
) -> RetrievalEvalSummary:
    """Run a full evaluation suite, computing aggregate accuracy/latency stats."""
    results = [
        await evaluate_query(tc, ollama_service, qdrant_service, limit=limit, collection_name=collection_name)
        for tc in test_cases
    ]

    if not results:
        return RetrievalEvalSummary(results=[], recall_at_k=0.0, avg_latency_ms=0.0, p95_latency_ms=0.0, avg_top_score=0.0)

    recall_at_k = sum(1 for r in results if r.expected_found) / len(results)

    latencies = sorted(r.latency_ms for r in results)
    avg_latency_ms = sum(latencies) / len(latencies)
    p95_index = min(int(len(latencies) * 0.95), len(latencies) - 1)
    p95_latency_ms = latencies[p95_index]

    scores = [r.top_score for r in results if r.top_score is not None]
    avg_top_score = sum(scores) / len(scores) if scores else 0.0

    return RetrievalEvalSummary(
        results=results,
        recall_at_k=recall_at_k,
        avg_latency_ms=avg_latency_ms,
        p95_latency_ms=p95_latency_ms,
        avg_top_score=avg_top_score,
    )


def format_summary_report(summary: RetrievalEvalSummary) -> str:
    """Human-readable report for console/log output."""
    lines = [
        "RAG Retrieval Evaluation",
        "=" * 40,
        f"Test cases:       {len(summary.results)}",
        f"Recall@k:         {summary.recall_at_k:.1%}",
        f"Avg latency:      {summary.avg_latency_ms:.1f} ms",
        f"P95 latency:      {summary.p95_latency_ms:.1f} ms",
        f"Avg top score:    {summary.avg_top_score:.3f}",
        "",
        "Per-query results:",
    ]
    for r in summary.results:
        status = "PASS" if r.expected_found else "FAIL"
        rank_str = f"rank {r.found_at_rank}" if r.found_at_rank else "not found"
        lines.append(
            f"  [{status}] {r.label or r.query[:40]!r}: {r.latency_ms:.1f}ms, top_score={r.top_score}, {rank_str}"
        )
    return "\n".join(lines)