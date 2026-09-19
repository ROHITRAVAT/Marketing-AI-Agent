import os

def fix_tools_py_time():
    with open("app/agents/nodes/tools.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_code = """
                                scheduled_time=datetime.now(timezone.utc),
"""
    
    old_code = """
                                scheduled_time=datetime.now(timezone.utc) + timedelta(minutes=5),
"""
    
    if old_code.strip() in content:
        content = content.replace(old_code.strip(), new_code.strip())
    
    with open("app/agents/nodes/tools.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_tools_py_time()
