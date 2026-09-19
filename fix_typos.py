import os

def fix_scheduler_typos():
    with open("tests/integration/test_scheduler_integration.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Fix provider vs platform
    content = content.replace('platform="linkedin",\n            access_token="mock_token"', 'provider="linkedin",\n            access_token="mock_token"')
    
    # Fix error_message_message
    content = content.replace('post.error_message_message', 'post.error_message')

    with open("tests/integration/test_scheduler_integration.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_scheduler_typos()
