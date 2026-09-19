import os

def fix_import():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("from app.models.scheduler import ScheduledPost", "from app.models.scheduled_post import ScheduledPost")

    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_import()
