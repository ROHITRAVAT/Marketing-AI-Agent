import os

def fix_agent_service():
    with open("app/services/agent_service.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_code = """
                # Run the graph
                logger.info(f"Invoking graph for thread {request.thread_id}")
                result_state = await graph.ainvoke(input_data, config)
                
                # Check snapshot to see if interrupted
                post_snapshot = await graph.aget_state(config)
                
                # Check the result state to determine the response
                if post_snapshot.next and "request_human_approval" in post_snapshot.next:
                    return AgentChatResponse(
                        status="waiting_for_approval",
                        thread_id=request.thread_id,
                        final_response=None,
                        approval_required=True,
                        approval_request_id=post_snapshot.values.get("approval_request_id")
                    )
                elif result_state.get("status") == AgentStatus.WAITING_FOR_APPROVAL:
                    return AgentChatResponse(
                        status="waiting_for_approval",
                        thread_id=request.thread_id,
                        final_response=None,
                        approval_required=True,
                        approval_request_id=result_state.get("approval_request_id")
                    )
"""
    
    old_code = """
                # Run the graph
                logger.info(f"Invoking graph for thread {request.thread_id}")
                result_state = await graph.ainvoke(input_data, config)
                
                # Check the result state to determine the response
                if result_state.get("status") == AgentStatus.WAITING_FOR_APPROVAL:
                    return AgentChatResponse(
                        status="approval_pending",
                        thread_id=request.thread_id,
                        final_response=None,
                        approval_required=True,
                        approval_request_id=result_state.get("approval_request_id")
                    )
"""
    
    content = content.replace(old_code.strip(), new_code.strip())
    
    with open("app/services/agent_service.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_agent_service()
