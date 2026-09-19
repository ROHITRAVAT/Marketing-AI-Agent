import os

def fix_agent_error():
    with open("app/services/agent_service.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_except = """    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Exception in process_request: {e}")"""
        
    old_except = """    except Exception as e:
import traceback
traceback.print_exc()
print(f"Exception in process_request: {e}")"""

    if old_except in content:
        content = content.replace(old_except, new_except)

    with open("app/services/agent_service.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_agent_error()
