import asyncio

from app.agents.nodes.retrieval import retrieve_documents
from app.agents.state import MarketingAgentState


async def main():
    state = MarketingAgentState(
        user_input=(
            "Create a LinkedIn campaign for my AI marketing product."
        ),
        product="AI Marketing Agent",
        target_audience="Small businesses",
        platform="LinkedIn",
        campaign_goal="Generate leads",
    )

    result = await retrieve_documents(state)

    print("\nRetrieval Node Result:")
    print("=" * 50)

    documents = result.get("retrieved_documents", [])

    print(f"Documents retrieved: {len(documents)}")

    for document in documents:
        print("\nDocument ID:", document.document_id)
        print("Score:", document.score)
        print("Content:", document.content[:300])
        print("Metadata:", document.metadata)


if __name__ == "__main__":
    asyncio.run(main())