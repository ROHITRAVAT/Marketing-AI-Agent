import os
import re

def debug_test():
    with open("tests/integration/test_full_agent_flow.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Add a print statement before the assert
    content = content.replace(
        'assert chat_response.status_code == 200\n        chat_data = chat_response.json()\n        assert chat_data["status"] == "waiting_for_approval"',
        'assert chat_response.status_code == 200\n        chat_data = chat_response.json()\n        print(f"\\n\\nCHAT DATA: {chat_data}\\n\\n")\n        assert chat_data["status"] == "waiting_for_approval"'
    )

    with open("tests/integration/test_full_agent_flow.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    debug_test()
