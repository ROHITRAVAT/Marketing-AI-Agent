import os

def fix_test_engine():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    old_code = """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except:
            pass
"""

    new_code = """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    return engine
"""

    content = content.replace(old_code.strip(), new_code.strip())
    
    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_test_engine()
