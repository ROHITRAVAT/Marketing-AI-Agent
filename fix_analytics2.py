import os

def fix_test2():
    with open("tests/integration/test_analytics_integration.py", "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("    from app.models.social_analytics import SocialAnalytics\n    import datetime\n", "    from app.models.social_analytics import SocialAnalytics\n")

    with open("tests/integration/test_analytics_integration.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_test2()
