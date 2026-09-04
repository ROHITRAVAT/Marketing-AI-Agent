from app.agents.schemas import RetrievedDocument
from app.agents.state import MarketingAgentState
from app.agents.utils.errors import handle_node_error
from app.qdrant.collections import COLLECTION_MARKETING_DOCUMENTS
from app.qdrant.service import get_qdrant_service
from app.ollama.service import get_ollama_service


async def retrieve_documents(
    state: MarketingAgentState,
) -> dict:
    """
    Retrieve relevant marketing documents from Qdrant.

    The node:
        1. Builds a retrieval query from the marketing request.
        2. Generates an embedding using Ollama.
        3. Searches the marketing_knowledge Qdrant collection.
        4. Converts Qdrant results into RetrievedDocument objects.
        5. Returns the documents as a state update.
    """ 

    print("Retrieving relevant marketing documents...")

    try:
        retrieval_query = _build_retrieval_query(state)

        ollama_service = get_ollama_service()
        qdrant_service = get_qdrant_service()

        query_vector = await ollama_service.embed(retrieval_query)

        if not query_vector:
            raise ValueError(
                "Embedding service returned an empty vector."
            )

        results = await qdrant_service.search(
            COLLECTION_MARKETING_DOCUMENTS,
            query_vector,
            limit=5,
        )

        retrieved_documents: list[RetrievedDocument] = []

        for point in results:
            payload = point.payload or {}

            document_id = str(
                payload.get("document_id", point.id)
            )

            content = payload.get("content")

            if not content:
                continue

            retrieved_documents.append(
                RetrievedDocument(
                    document_id=document_id,
                    content=str(content),
                    score=float(point.score),
                    metadata=payload,
                )
            )

        return {
            "retrieved_documents": retrieved_documents,
        }

    except Exception as error:
        return handle_node_error(
            state,
            error,
            "retrieve_documents",
        )


def _build_retrieval_query(
    state: MarketingAgentState,
) -> str:
    """
    Build a meaningful semantic-search query from the agent state.
    """

    query_parts = [
        state.user_input,
    ]

    if state.product:
        query_parts.append(
            f"Product or service: {state.product}"
        )

    if state.target_audience:
        query_parts.append(
            f"Target audience: {state.target_audience}"
        )

    if state.platform:
        query_parts.append(
            f"Marketing platform: {state.platform}"
        )

    if state.campaign_goal:
        query_parts.append(
            f"Campaign goal: {state.campaign_goal}"
        )

    return "\n".join(query_parts)