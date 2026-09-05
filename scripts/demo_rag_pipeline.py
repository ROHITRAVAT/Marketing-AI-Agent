"""Manual end-to-end demo of the RAG pipeline: ingest a real file, then query it.

Run with: python scripts/demo_rag_pipeline.py
Requires Docker services running (Ollama + Qdrant).
"""
import asyncio

from app.ollama.service import get_ollama_service
from app.qdrant.service import get_qdrant_service
from app.rag.loaders import load_txt
from app.rag.embedding import ingest_document
from app.rag.evaluation import RetrievalTestCase, evaluate_retrieval, format_summary_report


async def main():
    ollama_service = get_ollama_service()
    qdrant_service = get_qdrant_service()

    print("Step 1: Loading mock company document...")
    document = load_txt("sample_data/brand_guide.txt")
    print(f"  Loaded {len(document.content)} characters.\n")

    print("Step 2: Ingesting (chunk -> embed -> store in Qdrant)...")
    result = await ingest_document(
        document,
        knowledge_type="brand_knowledge",
        ollama_service=ollama_service,
        qdrant_service=qdrant_service,
    )
    print(f"  Created {result.chunks_created} chunks, stored {result.chunks_stored}.\n")

    print("Step 3: Running real retrieval queries...\n")
    test_cases = [
        RetrievalTestCase(
            query="What is StrideWorks' target audience?",
            expected_document_ids=[document.document_id],
            label="target audience query",
        ),
        RetrievalTestCase(
            query="What SEO keywords should we target?",
            expected_document_ids=[document.document_id],
            label="SEO query",
        ),
        RetrievalTestCase(
            query="How did our Instagram campaign perform?",
            expected_document_ids=[document.document_id],
            label="campaign performance query",
        ),
    ]

    summary = await evaluate_retrieval(test_cases, ollama_service, qdrant_service)
    print(format_summary_report(summary))

    print("\nStep 4: Showing actual retrieved content for one query...\n")
    query_vector = await ollama_service.embed("What is StrideWorks' target audience?")
    results = await qdrant_service.search("marketing_knowledge", query_vector, limit=2)
    for i, point in enumerate(results, start=1):
        content = point.payload.get("content", "")
        print(f"--- Result {i} (score: {point.score:.3f}) ---")
        print(content[:200] + ("..." if len(content) > 200 else ""))
        print()


if __name__ == "__main__":
    asyncio.run(main())