from pathlib import Path

import app.agents.openclaw as openclaw_integration


def test_openclaw_graph_reports_available_cmdop(monkeypatch, tmp_path):
    binary = tmp_path / "cmdop.exe"
    binary.write_text("fake binary")

    monkeypatch.setattr(openclaw_integration, "find_installed", lambda: binary)

    result = openclaw_integration.verify_openclaw_langgraph_connection()

    assert result["installed"] is True
    assert result["installed_path"] == str(binary)
    assert result["ready"] is True
    assert "browser automation" in result["message"]


def test_openclaw_graph_reports_missing_cmdop(monkeypatch, tmp_path):
    monkeypatch.setattr(openclaw_integration, "find_installed", lambda: None)
    monkeypatch.setattr(
        openclaw_integration,
        "default_install_dir",
        lambda: Path(tmp_path / "cmdop" / "bin"),
    )

    result = openclaw_integration.verify_openclaw_langgraph_connection()

    assert result["installed"] is False
    assert result["ready"] is False
    assert "openclaw/cmdop is not installed" in result["message"].lower()
