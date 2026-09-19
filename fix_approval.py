import os

def fix_approval_node():
    with open("app/agents/nodes/approval.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Import NodeInterrupt
    if "NodeInterrupt" not in content:
        content = content.replace("from langgraph.errors import GraphInterrupt", "from langgraph.errors import GraphInterrupt, NodeInterrupt")
        
    # Catch both
    old_catch = "    except GraphInterrupt as gi:"
    new_catch = "    except (GraphInterrupt, NodeInterrupt) as gi:"
    
    content = content.replace(old_catch, new_catch)
    
    with open("app/agents/nodes/approval.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_approval_node()
