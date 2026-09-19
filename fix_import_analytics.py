import os

def fix_import():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("from app.models.analytics import AnalyticsMetric", "from app.models.social_analytics import SocialAnalytics")

    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_import()
