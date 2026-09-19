import os

def print_error():
    with open("app/agents/nodes/error.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_code = """
    try:
        import traceback
        traceback.print_exc()
        print(f"Exception passed to error_handler: {exc}")
    except:
        pass
    
    # 1. Determine Error Category
"""
    
    content = content.replace("    # 1. Determine Error Category", new_code)
    
    with open("app/agents/nodes/error.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    print_error()
