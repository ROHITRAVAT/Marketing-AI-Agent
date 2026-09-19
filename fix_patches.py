import os
import re

def remove_bad_patch():
    files = [
        "tests/integration/test_full_agent_flow.py",
        "tests/integration/test_multi_platform_integration.py"
    ]
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Remove the patch line
        content = re.sub(
            r',\s*patch\("app\.agents\.nodes\.retrieval\.retrieve_documents", new_callable=AsyncMock\) as mock_retrieve',
            '',
            content
        )
        # Remove mock_retrieve.return_value line
        content = re.sub(
            r'mock_retrieve\.return_value = \{"retrieved_documents": \[\]\}',
            '',
            content
        )
        
        with open(file, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    remove_bad_patch()
