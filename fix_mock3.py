import os

def fix_mock_again():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    # The current json mock is MagicMock(return_value={"likes": 10, "comments": 5, "shares": 2, "impressions": 100, "clicks": 15})
    # We should make it return empty data so that the providers use defaults.
    old_json = """        mock_get.return_value.json = MagicMock(return_value={
            "likes": 10,
            "comments": 5,
            "shares": 2,
            "impressions": 100,
            "clicks": 15
        })"""
    new_json = """        mock_get.return_value.json = MagicMock(return_value={
            "data": [],
            "likes": 10,
            "comments": {"summary": {"total_count": 5}},
            "shares": 2,
            "impressions": 100,
            "clicks": 15
        })"""
    
    content = content.replace(old_json, new_json)

    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_mock_again()
