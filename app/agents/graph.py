from langgraph.graph import END, START, StateGraph

from app.agents.nodes.analyze import analyze_request
from app.agents.nodes.routing import (
    route_after_analysis,
    route_after_strategy,
    route_after_review,
)
from app.agents.nodes.clarification import request_clarification
from app.agents.nodes.retrieval import retrieve_documents
from app.agents.nodes.strategy import generate_strategy
from app.agents.nodes.planning import create_plan
from app.agents.nodes.content import generate_content
from app.agents.nodes.review import review_content
from app.agents.nodes.tools import execute_tools
from app.agents.nodes.final import generate_final_response
from app.agents.state import MarketingAgentState


def build_marketing_graph():
    """
    Build and compile the Marketing AI Agent graph.
    """

    graph = StateGraph(MarketingAgentState)

    # Register nodes.
    graph.add_node("analyze_request", analyze_request)
    graph.add_node("request_clarification", request_clarification)
    graph.add_node("retrieve_documents", retrieve_documents)
    graph.add_node("generate_strategy", generate_strategy)
    graph.add_node("create_plan", create_plan)
    graph.add_node("generate_content", generate_content)
    graph.add_node("review_content", review_content)
    graph.add_node("execute_tools", execute_tools)
    graph.add_node("generate_final_response", generate_final_response)

    # Start the workflow.
    graph.add_edge(START, "analyze_request")

    # Decide what to do after analyzing the request.
    graph.add_conditional_edges(
        "analyze_request",
        route_after_analysis,
        {
            "ready_for_retrieval": "retrieve_documents",
            "needs_clarification": "request_clarification",
        },
    )

    # Sequential edges
    graph.add_edge("retrieve_documents", "generate_strategy")

    # Strategy to Plan (or failed)
    graph.add_conditional_edges(
        "generate_strategy",
        route_after_strategy,
        {
            "ready_for_planning": "create_plan",
            "failed": "generate_final_response",
        },
    )

    # Sequential edge
    graph.add_edge("create_plan", "generate_content")
    graph.add_edge("generate_content", "review_content")

    # Review routing
    graph.add_conditional_edges(
        "review_content",
        route_after_review,
        {
            "approved": "execute_tools",
            "needs_revision": "generate_content",
            "failed": "generate_final_response",
        }
    )

    # Tool Execution to Final
    graph.add_edge("execute_tools", "generate_final_response")
    
    # Clarification to final
    graph.add_edge("request_clarification", "generate_final_response")

    # Final to END
    graph.add_edge("generate_final_response", END)

    # Compile the graph into an executable workflow.
    return graph.compile()


marketing_graph = build_marketing_graph()