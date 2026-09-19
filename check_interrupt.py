import os

def check_interrupt_type():
    with open("app/agents/nodes/approval.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_except = """    except Exception as error:
        print(f"Exception type: {type(error)}")
        print(f"Exception class name: {error.__class__.__name__}")
        return handle_node_error(
            state,
            error,
            "request_human_approval",
        )"""
        
    old_except = """    except Exception as error:
        return handle_node_error(
            state,
            error,
            "request_human_approval",
        )"""

    if old_except in content:
        content = content.replace(old_except, new_except)

    with open("app/agents/nodes/approval.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    check_interrupt_type()
