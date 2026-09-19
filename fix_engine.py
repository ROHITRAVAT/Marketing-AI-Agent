import os
import re

def fix_sqlite_concurrency():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Replace the test_engine fixture
    new_engine = """@pytest.fixture(scope="session")
def test_engine():
    import os
    db_path = "./test_db.sqlite"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except:
            pass
            
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        echo=False,
    )
    yield engine
    
    # Cleanup after all tests
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except:
            pass
"""
    
    content = re.sub(
        r'@pytest\.fixture\(scope="session"\)\ndef test_engine\(\):.*?yield engine',
        new_engine.strip(),
        content,
        flags=re.DOTALL
    )

    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_sqlite_concurrency()
