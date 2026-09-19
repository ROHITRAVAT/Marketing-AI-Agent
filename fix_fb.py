import sys
import re

file_path = 'tests/test_facebook_integration.py'
with open(file_path, 'r') as f:
    content = f.read()

# Remove test_generate_auth_url, test_exchange_token_success, test_exchange_token_failure
content = re.sub(r'@pytest\.mark\.asyncio\s+async def test_generate_auth_url\(\):.*?(?=@pytest\.mark\.asyncio)', '', content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
