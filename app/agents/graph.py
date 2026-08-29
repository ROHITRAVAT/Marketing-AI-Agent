from langgraph.graph import END, START, StateGraph

from app.agents.nodes.analyze import analyze_request
from app.agents.nodes.routing import (
    route_after_analysis,
    route_after_strategy,
)
from app.agents.nodes.clarification import request_clarification
from app.agents.nodes.strategy import generate_strategy
from app.agents.nodes.content import generate_content
from app.agents.state import MarketingAgentState


def build_marketing_graph():
    """
    Build and compile the Marketing AI Agent graph.
    """

    graph = StateGraph(MarketingAgentState)

    # Register nodes.
    graph.add_node("analyze_request", analyze_request)
    graph.add_node("generate_strategy", generate_strategy)
    graph.add_node("generate_content", generate_content)
    graph.add_node("request_clarification", request_clarification)

    # Start the workflow.
    graph.add_edge(START, "analyze_request")

    # Decide what to do after analyzing the request.
    graph.add_conditional_edges(
        "analyze_request",
        route_after_analysis,
        {
            "ready_for_strategy": "generate_strategy",
            "needs_clarification": "request_clarification",
        },
    )

    # Normal marketing workflow.
    graph.add_conditional_edges(
        "generate_strategy",
        route_after_strategy,
        {
            "ready_for_content": "generate_content",
            "failed": END,
        },
    )

    # Successful content generation.
    graph.add_edge("generate_content", END)

    # Clarification workflow.
    graph.add_edge("request_clarification", END)

    # Compile the graph into an executable workflow.
    return graph.compile()


marketing_graph = build_marketing_graph()