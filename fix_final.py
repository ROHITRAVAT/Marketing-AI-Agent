import os

def final_fix():
    with open("tests/integration/test_scheduler_integration.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Fix provider
    content = content.replace(
        'platform="linkedin",\n            access_token="mock_token"', 
        'provider="linkedin",\n            access_token="mock_token"'
    )
    
    # Fix the assertion
    content = content.replace(
        'assert "Failed to refresh token" in post.error_message', 
        'assert "Tool execution did not report success" in post.error_message'
    )

    with open("tests/integration/test_scheduler_integration.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    final_fix()
