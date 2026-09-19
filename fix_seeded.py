import os
import re

def fix_seeded_session():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    old_add_all = "db_session.add_all([active_user, inactive_user])"
    new_add_all = """
    await db_session.merge(active_user)
    await db_session.merge(inactive_user)
"""

    content = content.replace(old_add_all, new_add_all.strip())

    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_seeded_session()
