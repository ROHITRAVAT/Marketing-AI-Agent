import os

def fix_conftest2():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_code = """
        app.dependency_overrides[get_db_session] = _get_test_db
        app.dependency_overrides[deps_get_current_user] = _get_test_user
        app.dependency_overrides[auth_get_current_user] = _get_test_user
    """
    
    old_code = """
        app.dependency_overrides[get_db_session] = _get_test_db
        app.dependency_overrides[get_current_user] = _get_test_user
    """
    
    if old_code.strip() in content:
        content = content.replace(old_code.strip(), new_code.strip())
    
    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_conftest2()
