"""OpenClaw and LangGraph integration helpers.

OpenClaw is used here as the installer/wrapper for the ``cmdop`` browser
automation runtime. The LangGraph graph keeps the integration observable and
testable without requiring a live browser session in unit tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from openclaw import default_install_dir, find_installed


class OpenClawState(TypedDict, total=False):
    installed: bool
    installed_path: str | None
    default_install_dir: str
    ready: bool
    message: str


@dataclass(frozen=True)
class OpenClawRuntime:
    """Snapshot of the local OpenClaw/cmdop installation state."""

    installed: bool
    installed_path: Path | None
    default_install_dir: Path


def get_openclaw_runtime() -> OpenClawRuntime:
    """Inspect whether the OpenClaw-managed cmdop binary is available."""

    installed_path = find_installed()
    return OpenClawRuntime(
        installed=installed_path is not None,
        installed_path=installed_path,
        default_install_dir=default_install_dir(),
    )


def _inspect_runtime(_: OpenClawState) -> OpenClawState:
    runtime = get_openclaw_runtime()
    return {
        "installed": runtime.installed,
        "installed_path": str(runtime.installed_path) if runtime.installed_path else None,
        "default_install_dir": str(runtime.default_install_dir),
    }


def _summarize_runtime(state: OpenClawState) -> OpenClawState:
    if state.get("installed") and state.get("installed_path"):
        return {
            "ready": True,
            "message": (
                "OpenClaw/cmdop is available at "
                f"{state['installed_path']} and LangGraph can target it for "
                "browser automation workflows."
            ),
        }

    install_dir = state.get("default_install_dir") or str(default_install_dir())
    return {
        "ready": False,
        "message": (
            "OpenClaw/cmdop is not installed. Run `openclaw` to install the "
            f"browser automation runtime into {install_dir}."
        ),
    }


def build_openclaw_graph() -> Any:
    """Build a tiny LangGraph workflow that verifies OpenClaw availability."""

    graph = StateGraph(OpenClawState)
    graph.add_node("inspect_runtime", _inspect_runtime)
    graph.add_node("summarize_runtime", _summarize_runtime)
    graph.set_entry_point("inspect_runtime")
    graph.add_edge("inspect_runtime", "summarize_runtime")
    graph.add_edge("summarize_runtime", END)
    return graph.compile()


def verify_openclaw_langgraph_connection() -> OpenClawState:
    """Run the LangGraph workflow and return the resulting status payload."""

    return build_openclaw_graph().invoke({})