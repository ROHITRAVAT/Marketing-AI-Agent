import os
import glob
import re

def fix_tests():
    for fpath in glob.glob("tests/integration/*.py"):
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        # Fix content="something" to content={"body": "something", "content_type": "text"}
        # But we must be careful. Let's just do simple string replacements for the known ones.
        content = re.sub(
            r'content="Past post"',
            r'content={"body": "Past post", "content_type": "text"}',
            content
        )
        content = re.sub(
            r'content="Cancelled post"',
            r'content={"body": "Cancelled post", "content_type": "text"}',
            content
        )
        content = re.sub(
            r'content="Token fail post"',
            r'content={"body": "Token fail post", "content_type": "text"}',
            content
        )
        content = re.sub(
            r'content="Future post"',
            r'content={"body": "Future post", "content_type": "text"}',
            content
        )
        content = re.sub(
            r'content=f"\{plat\} test content"',
            r'content={"body": f"{plat} test content", "content_type": "text"}',
            content
        )

        # Fix published_at
        content = re.sub(
            r'status="published",\n\s*external_post_id=',
            r'status="published",\n                published_at=past_time,\n                external_post_id=',
            content
        )

        # Fix post.error to post.error_message
        content = content.replace("post.error\n", "post.error_message\n")
        content = content.replace("in post.error", "in post.error_message")

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    fix_tests()
