import pytest
from app.agents.graph import build_marketing_graph
from app.agents.state import MarketingAgentState
from app.agents.enums import AgentStatus
from app.qdrant.service import get_qdrant_service
from app.qdrant.collections import COLLECTION_MARKETING_DOCUMENTS
from qdrant_client.models import PointStruct
from app.ollama.service import get_ollama_service
from qdrant_client import AsyncQdrantClient
from app.qdrant.service import QdrantService
from unittest.mock import patch
import uuid

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def seeded_qdrant():
    """Seeds Qdrant with specific marketing documents for testing retrieval."""
    
    memory_client = AsyncQdrantClient(":memory:")
    # We must ensure the collection is created in memory
    from qdrant_client.models import VectorParams, Distance
    from app.core.config import QDRANT_VECTOR_SIZE
    
    await memory_client.create_collection(
        collection_name=COLLECTION_MARKETING_DOCUMENTS,
        vectors_config=VectorParams(size=QDRANT_VECTOR_SIZE, distance=Distance.COSINE),
    )
    
    qdrant = QdrantService(memory_client)
    
    with patch("app.agents.nodes.retrieval.get_qdrant_service", return_value=qdrant):
        ollama = get_ollama_service()
    
        # Generate test documents
        docs = [
            "Company Description: AI-Marketing Co builds advanced autonomous agents for social media.",
            "Tone Guidelines: Professional, energetic, and concise.",
            "Target Audience: Marketing agencies, social media managers."
        ]
        
        points = []
        for i, doc in enumerate(docs):
            # We must generate real embeddings to be retrieved semantically
            vector = await ollama.embed(doc)
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={"content": doc, "source": "e2e_test"}
                )
            )
        
        await qdrant.insert_points(COLLECTION_MARKETING_DOCUMENTS, points)
        
        yield qdrant
        
        # Cleanup (optional but good for E2E)
        point_ids = [p.id for p in points]
        await qdrant.delete_points(COLLECTION_MARKETING_DOCUMENTS, point_ids)

async def test_qdrant_retrieval_flow(seeded_qdrant):
    graph = build_marketing_graph()
    
    # The prompt should be similar to the seeded documents to ensure high retrieval score
    state = MarketingAgentState(
        user_input="Create a LinkedIn post describing our product using our brand guidelines.",
        product="autonomous agents",
        platform="LinkedIn",
        target_audience="Marketing agencies",
        campaign_goal="Launch",
    )
    
    config = {"configurable": {"thread_id": "test-thread"}}
    result = await graph.ainvoke(state, config)
    
    assert result["status"] in [AgentStatus.WAITING_FOR_APPROVAL, AgentStatus.COMPLETED]
    
    # Verify retrieval
    assert len(result["retrieved_documents"]) > 0
    retrieved_content = " ".join([d.content for d in result["retrieved_documents"]])
    assert "AI-Marketing Co" in retrieved_content or "Tone Guidelines" in retrieved_content
    
    # The LLM should incorporate the retrieved context (like 'professional', 'energetic', 'AI-Marketing')
    generated = result["generated_content"].body.lower()
    assert len(generated) > 0
