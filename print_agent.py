import os

def print_agent_error():
    with open("app/services/agent_service.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_except = """    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Exception in process_request: {e}")"""
        
    content = content.replace("    except Exception as e:", new_except)

    with open("app/services/agent_service.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    print_agent_error()
