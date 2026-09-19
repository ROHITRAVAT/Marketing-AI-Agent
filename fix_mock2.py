import os

def fix_mock_syntax():
    with open("tests/conftest.py", "r", encoding="utf-8") as f:
        content = f.read()

    # The dictionary ends with `        }`
    # We need to change it to `        })`
    content = content.replace('        }\n        \n        # Default for post requests', '        })\n        \n        # Default for post requests')

    with open("tests/conftest.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_mock_syntax()
