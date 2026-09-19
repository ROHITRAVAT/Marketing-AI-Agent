import os

def fix_patch():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace(
        'patch("app.db.session.AsyncSessionLocal", new=async_session), \\',
        'patch("app.database.connection.AsyncSessionLocal", new=async_session), \\'
    )

    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_patch()
