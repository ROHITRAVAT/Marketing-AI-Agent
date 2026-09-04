import asyncio
import logging
import uuid
import sys
from qdrant_client.models import PointStruct

from app.core.config import OLLAMA_EMBEDDING_MODEL, QDRANT_VECTOR_SIZE
from app.ollama.service import get_ollama_service
from app.qdrant.service import get_qdrant_service
from app.qdrant.collections import COLLECTION_MARKETING_DOCUMENTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    qdrant = get_qdrant_service()
    ollama = get_ollama_service()

    # 1. Check connections
    try:
        await qdrant.check_connection()
        logger.info("Qdrant is reachable")
    except Exception as e:
        logger.error(f"Qdrant connection failed: {e}")
        sys.exit(1)

    try:
        await ollama.check_connection()
        logger.info("Ollama is reachable")
    except Exception as e:
        logger.error(f"Ollama connection failed: {e}")
        sys.exit(1)

    # 2. Check model availability
    models = await ollama.list_models()
    model_names = [m.get("name") for m in models]
    
    # Simple prefix matching for model variants (e.g. all-minilm:latest)
    if not any(OLLAMA_EMBEDDING_MODEL in m for m in model_names):
        logger.error(f"Embedding model {OLLAMA_EMBEDDING_MODEL} not found in Ollama.")
        sys.exit(1)
    logger.info(f"Embedding model {OLLAMA_EMBEDDING_MODEL} is available")

    # 3 & 4. Generate embedding and check dimension
    text_to_embed = "This is a test marketing document about our new AI features."
    try:
        embedding = await ollama.embed(text_to_embed)
        logger.info("Successfully generated embedding")
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        sys.exit(1)

    if len(embedding) != QDRANT_VECTOR_SIZE:
        logger.error(f"Dimension mismatch! Model output: {len(embedding)}, Configured: {QDRANT_VECTOR_SIZE}")
        sys.exit(1)
    logger.info(f"Vector dimension is correct ({len(embedding)})")

    # 5. Make sure collection exists
    await qdrant.ensure_collections()
    if not await qdrant.collection_exists(COLLECTION_MARKETING_DOCUMENTS):
        logger.error(f"Collection {COLLECTION_MARKETING_DOCUMENTS} does not exist even after ensure_collections.")
        sys.exit(1)
    logger.info(f"Collection {COLLECTION_MARKETING_DOCUMENTS} exists")

    # 6. Insert test vector with payload
    point_id = str(uuid.uuid4())
    payload = {
        "document_id": "test_doc_001",
        "document_name": "test_marketing.pdf",
        "chunk_id": f"test_doc_001_chunk_{point_id}",
        "chunk_index": 0,
        "text": text_to_embed,
        "source_type": "script",
        "knowledge_type": "test",
        "user_id": "test_user"
    }
    
    try:
        await qdrant.insert_points(
            name=COLLECTION_MARKETING_DOCUMENTS,
            points=[PointStruct(id=point_id, vector=embedding, payload=payload)]
        )
        logger.info(f"Successfully inserted test vector (ID: {point_id})")
    except Exception as e:
        logger.error(f"Failed to insert vector: {e}")
        sys.exit(1)

    # 7. Perform similarity search
    try:
        results = await qdrant.search(name=COLLECTION_MARKETING_DOCUMENTS, query_vector=embedding, limit=1)
        if not results:
            logger.error("Similarity search returned no results.")
            sys.exit(1)
        logger.info(f"Similarity search works. Top match score: {results[0].score}")
    except Exception as e:
        logger.error(f"Similarity search failed: {e}")
        sys.exit(1)

    # Cleanup test vector
    try:
        await qdrant.delete_points(name=COLLECTION_MARKETING_DOCUMENTS, point_ids=[point_id])
        logger.info(f"Cleaned up test vector (ID: {point_id})")
    except Exception as e:
        logger.warning(f"Failed to clean up test vector: {e}")

    logger.info("All RAG infrastructure checks passed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
