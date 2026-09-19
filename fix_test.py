import os

def fix_test():
    with open("tests/integration/test_full_agent_flow.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_code = """
        mock_planning_chain = MagicMock()
        mock_planning_chain.ainvoke = AsyncMock(return_value={
            "steps": [
                {"step_id": 1, "description": "social media post on linkedin", "dependency": []}
            ]
        })
        
        mock_review_chain = MagicMock()
        mock_review_chain.ainvoke = AsyncMock(return_value={
            "approval_status": "APPROVED",
            "feedback": "Looks good",
            "revised_content": "Revised content"
        })
        
        with patch("app.agents.nodes.strategy.build_text_chain", return_value=mock_text_chain), \\
             patch("app.agents.nodes.content.build_text_chain", return_value=mock_text_chain), \\
             patch("app.agents.nodes.planning.build_json_chain", return_value=mock_planning_chain), \\
             patch("app.agents.nodes.review.build_json_chain", return_value=mock_review_chain), \\
"""
    
    old_code = """
        mock_json_chain = MagicMock()
        # Mock a plan that will dispatch the LinkedIn tool
        mock_json_chain.ainvoke = AsyncMock(return_value={
            "steps": [
                {"step_id": 1, "description": "social media post on linkedin", "dependency": []}
            ]
        })
    
        with patch("app.agents.nodes.strategy.build_text_chain", return_value=mock_text_chain), \\
             patch("app.agents.nodes.content.build_text_chain", return_value=mock_text_chain), \\
             patch("app.agents.nodes.planning.build_json_chain", return_value=mock_json_chain), \\
             patch("app.agents.nodes.review.build_json_chain", return_value=mock_json_chain), \\
"""
    
    content = content.replace(old_code.strip(), new_code.strip())
    
    with open("tests/integration/test_full_agent_flow.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_test()
