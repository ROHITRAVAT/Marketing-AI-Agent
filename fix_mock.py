import os

def fix_mock():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    # We need to replace the json configuration
    content = content.replace("mock_get.return_value.json.return_value = {", 'from unittest.mock import MagicMock\n        mock_get.return_value.json = MagicMock(return_value={')
    content = content.replace('mock_post.return_value.json.return_value = {"id": "mock_external_id_123"}', 'mock_post.return_value.json = MagicMock(return_value={"id": "mock_external_id_123"})')

    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_mock()
