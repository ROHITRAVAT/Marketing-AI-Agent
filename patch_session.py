import os
import re

def patch_async_session_local():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Replace the single patch with patching app.db.session.AsyncSessionLocal
    content = content.replace(
        'patch("app.scheduler.worker.AsyncSessionLocal", new=async_session), \\',
        'patch("app.db.session.AsyncSessionLocal", new=async_session), \\\n         patch("app.scheduler.worker.AsyncSessionLocal", new=async_session), \\'
    )

    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    patch_async_session_local()
