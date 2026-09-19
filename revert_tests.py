import os
import glob
import re

def revert_tests():
    for fpath in glob.glob("tests/integration/*.py"):
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        content = content.replace('content={"body": "Past post", "content_type": "text"}', 'content="Past post"')
        content = content.replace('content={"body": "Cancelled post", "content_type": "text"}', 'content="Cancelled post"')
        content = content.replace('content={"body": "Token fail post", "content_type": "text"}', 'content="Token fail post"')
        content = content.replace('content={"body": "Future post", "content_type": "text"}', 'content="Future post"')
        
        # fix dynamic string substitution back
        content = re.sub(
            r'content=\{"body": f"\{plat\} test content", "content_type": "text"\}',
            r'content=f"{plat} test content"',
            content
        )

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    revert_tests()
