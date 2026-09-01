"""Standalone verification for the OpenClaw/LangGraph integration."""

import json
import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from app.agents.openclaw import verify_openclaw_langgraph_connection  # noqa: E402


def main() -> int:
    result = verify_openclaw_langgraph_connection()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ready") else 1


if __name__ == "__main__":
    sys.exit(main())