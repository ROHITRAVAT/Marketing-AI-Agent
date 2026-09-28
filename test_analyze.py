import asyncio
from dotenv import load_dotenv
load_dotenv()
from app.agents.state import MarketingAgentState
from app.agents.nodes.analyze import analyze_request
import logging
logging.basicConfig(level=logging.DEBUG)

async def test():
    print("STARTING TEST")
    try:
        state = MarketingAgentState(user_input="Create a 5-day LinkedIn launch sequence for our AI product")
        result = await analyze_request(state)
        print("RESULT:")
        print(result)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(test())
