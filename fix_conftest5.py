import os

def fix_conftest5():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_code = """
    from app.models.integration import IntegrationConnection
    linkedin_conn = IntegrationConnection(
        user_id=1,
        provider="linkedin",
        access_token="mock_valid_token",
        provider_user_id="mock_urn"
    )
"""
    
    old_code = """
    from app.models.integration import IntegrationConnection
    linkedin_conn = IntegrationConnection(
        user_id=1,
        provider="linkedin",
        access_token="mock_valid_token",
        provider_user_id="mock_urn",
        status="connected"
    )
"""
    
    if old_code.strip() in content:
        content = content.replace(old_code.strip(), new_code.strip())
    
    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_conftest5()
