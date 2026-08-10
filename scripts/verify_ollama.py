"""Standalone infrastructure verification for Ollama (FastAPI -> Ollama).

Run inside the backend container so the connection uses the Docker network
(http://ollama:11434), never localhost:

    docker compose exec backend python scripts/verify_ollama.py

The script checks:
    1. Ollama is reachable over the Docker network
    2. /api/tags responds and returns a model list

The model list is expected to be empty — no model is downloaded in this
infrastructure task (Qwen 3 is installed in a separate task).
"""

import asyncio
import os
import sys

# Allow running as `python scripts/verify_ollama.py` from any working directory.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from app.core.config import OLLAMA_TIMEOUT, OLLAMA_URL  # noqa: E402
from app.ollama.client import build_async_client  # noqa: E402
from app.ollama.service import OllamaService  # noqa: E402


def _ok() -> None:
    print("      OK")


async def main() -> int:
    client = build_async_client()
    service = OllamaService(client, timeout=OLLAMA_TIMEOUT)
    try:
        print(f"[1/2] Ollama reachable at {OLLAMA_URL} ...")
        assert await service.check_connection() is True
        _ok()

        print("[2/2] Querying /api/tags ...")
        models = await service.list_models()
        model_names = [m.get("name", m.get("model", "?")) for m in models]
        print(f"      Installed models: {model_names if model_names else '(none — expected)'}")
        _ok()

        print(
            "\nSUCCESS — Ollama verified over the FastAPI/Docker network "
            f"({OLLAMA_URL}). No model was downloaded.\n"
        )
        return 0
    except Exception as exc:  # noqa: BLE001 - report any failure clearly
        print(f"\nFAILED: {exc}", file=sys.stderr)
        return 1
    finally:
        await client.aclose()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))