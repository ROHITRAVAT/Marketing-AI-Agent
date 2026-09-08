from langgraph.graph import END, START, StateGraph

from app.agents.nodes.analyze import analyze_request
from app.agents.nodes.routing import (
    route_after_analysis,
    route_after_strategy,
    route_after_review,
    route_after_human_approval,
)
from app.agents.nodes.clarification import request_clarification
from app.agents.nodes.retrieval import retrieve_documents
from app.agents.nodes.strategy import generate_strategy
from app.agents.nodes.planning import create_plan
from app.agents.nodes.content import generate_content
from app.agents.nodes.review import review_content
from app.agents.nodes.approval import request_human_approval
from app.agents.nodes.tools import execute_tools
from app.agents.nodes.final import generate_final_response
from app.agents.nodes.error import handle_error
from app.agents.state import MarketingAgentState
from app.agents.enums import AgentStatus

def route_after_error(state: MarketingAgentState) -> str:
    """Route based on whether the error is retryable or permanent."""
    if state.status == AgentStatus.RETRYING and state.last_failed_node:
        return state.last_failed_node
    return "generate_final_response"

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
    graph.add_node("request_human_approval", request_human_approval)
    graph.add_node("execute_tools", execute_tools)
    graph.add_node("generate_final_response", generate_final_response)
    graph.add_node("handle_error", handle_error)

    # Start the workflow.
    graph.add_edge(START, "analyze_request")

    # Decide what to do after analyzing the request.
    graph.add_conditional_edges(
        "analyze_request",
        route_after_analysis,
        {
            "ready_for_retrieval": "retrieve_documents",
            "needs_clarification": "request_clarification",
            "failed": "handle_error",
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
            "failed": "handle_error",
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
            "approved": "request_human_approval",
            "needs_revision": "generate_content",
            "failed": "handle_error",
        }
    )

    # Human approval routing
    graph.add_conditional_edges(
        "request_human_approval",
        route_after_human_approval,
        {
            "approved": "execute_tools",
            "failed": "handle_error",
        }
    )

    # Tool Execution to Final or Error
    # Assuming tools will return "failed" state on error
    def route_after_tools(state: MarketingAgentState) -> str:
        if state.status == AgentStatus.FAILED:
            return "handle_error"
        return "generate_final_response"
        
    graph.add_conditional_edges("execute_tools", route_after_tools)
    
    # Error routing
    graph.add_conditional_edges(
        "handle_error",
        route_after_error,
    )

    # Clarification to final
    graph.add_edge("request_clarification", "generate_final_response")

    # Final to END
    graph.add_edge("generate_final_response", END)

    # Compile the graph into an executable workflow.
    # Note: the checkpointer will be injected during execution or initialized elsewhere
    # but we will just pass nothing here, or configure checkpointer if available.
    return graph.compile()


marketing_graph = build_marketing_graph()