import os
import re

def unfix_test():
    with open("tests/integration/test_analytics_integration.py", "r", encoding="utf-8") as f:
        content = f.read()

    replacement = """    # 1. Run analytics collection
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_get_token:
        mock_get_token.return_value = "mock_valid_token"
        
        await poll_and_collect_analytics()"""

    content = re.sub(
        r'# 1\. Run analytics collection.*?await poll_and_collect_analytics\(\)',
        replacement,
        content,
        flags=re.DOTALL
    )
    
    replacement2 = """# 2. Idempotency test - run again
    with patch("app.core.oauth.manager.TokenManager.get_valid_access_token", new_callable=AsyncMock) as mock_get_token:
        mock_get_token.return_value = "mock_valid_token"
        
        await poll_and_collect_analytics()"""
        
    content = re.sub(
        r'# 2\. Idempotency test - run again.*?await poll_and_collect_analytics\(\)',
        replacement2,
        content,
        flags=re.DOTALL
    )

    with open("tests/integration/test_analytics_integration.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    unfix_test()
