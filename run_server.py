"""
Development server launcher for Windows environments.
Sets WindowsSelectorEventLoopPolicy to prevent ProactorEventLoop incompatibilities
with asyncpg and starts Uvicorn locally on http://127.0.0.1:8000.
"""
import asyncio
import sys
import uvicorn

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.main import app

if __name__ == "__main__":
    config = uvicorn.Config(app=app, host="127.0.0.1", port=8000, loop="none")
    server = uvicorn.Server(config)
    asyncio.run(server.serve())
