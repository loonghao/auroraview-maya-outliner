"""The GUI probe owns only its panel, bindings and disposable scene fixture."""

import threading
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from auroraview_maya_outliner import maya_outliner
from scripts.maya_gui_probe import GuiProbe


def probe(tmp_path):
    result = object.__new__(GuiProbe)
    result.server = SimpleNamespace(is_running=True, mcp_url="http://127.0.0.1:12345/mcp", stop=Mock())
    result.cmds = SimpleNamespace(workspaceControl=Mock(return_value=False), objExists=Mock(return_value=True), delete=Mock(), select=Mock())
    result.report = tmp_path / "gui.json"
    result.source_commit = "candidate"
    result.main_thread = threading.get_ident()
    result.threads = [result.main_thread]
    result.previous_selection = ["|original"]
    result.root = "fixture"
    result.workspace = "fixtureWorkspaceControl"
    result.tools = SimpleNamespace(closed=False, close=Mock(), call=Mock(return_value={"hierarchy": [], "selection": []}))
    result.agent = SimpleNamespace(close=Mock(), method_names={"scene.rename": "maya-outliner__scene_rename"})
    result.artifact = {}
    result.panel = SimpleNamespace(
        close=Mock(), _callbacks=SimpleNamespace(ids=[]),
        _ui_binding=SimpleNamespace(closed=True), webview=None, dialog=None,
    )
    return result


def test_probe_cleanup_preserves_borrowed_server_and_restores_original_selection(tmp_path):
    gate = probe(tmp_path)
    agent, tools = gate.agent, gate.tools
    assert gate.close()["status"] == "cleanup-passed"
    gate.server.stop.assert_not_called()
    agent.close.assert_called_once_with()
    tools.close.assert_called_once_with()
    gate.cmds.delete.assert_called_once_with("fixture")
    gate.cmds.select.assert_called_once_with(["|original"], replace=True)


def test_probe_cleanup_failure_retains_panel_owner_and_fixture_for_retry(tmp_path):
    gate = probe(tmp_path)
    panel, agent, tools = gate.panel, gate.agent, gate.tools
    gate.panel._callbacks.ids = [2]
    with pytest.raises(RuntimeError, match="cleanup failed"):
        gate.close()
    gate.server.stop.assert_not_called()
    assert gate.panel is panel
    assert gate.agent is agent and gate.tools is tools
    agent.close.assert_not_called()
    tools.close.assert_not_called()
    gate.cmds.delete.assert_not_called()
    assert '"status": "cleanup-failed"' in gate.report.read_text(encoding="utf-8")
    panel._callbacks.ids.clear()
    assert gate.close()["status"] == "cleanup-passed"
    assert gate.panel is None and gate.agent is None and gate.tools is None
    assert panel.close.call_count == 2
    agent.close.assert_called_once_with()
    tools.close.assert_called_once_with()
    gate.cmds.delete.assert_called_once_with("fixture")


def test_probe_records_core_mcp_url_property_without_starting_transport(tmp_path, monkeypatch):
    gate = probe(tmp_path)
    monkeypatch.setattr(maya_outliner, "_maya_main_window", lambda: SimpleNamespace(winId=lambda: 1234))
    gate.panel.webview = SimpleNamespace(get_hwnd=lambda: 5678)
    gate.panel.dialog = SimpleNamespace(devicePixelRatioF=lambda: 1.5)
    gate.panel._frontend_ready = True
    state = gate.state()
    assert state["mcp_url"] == "http://127.0.0.1:12345/mcp"
    assert state["main_hwnd"] == 1234 and state["webview_hwnd"] == 5678
    assert state["frontend_ready"]
    assert state["status"] == "awaiting-interactive-acceptance"


def test_probe_rejects_worker_cleanup_before_host_calls(tmp_path):
    gate = probe(tmp_path)
    with ThreadPoolExecutor(max_workers=1) as executor:
        with pytest.raises(AssertionError):
            executor.submit(gate.close).result()
    gate.panel.close.assert_not_called()
    gate.cmds.delete.assert_not_called()


def test_probe_agent_unload_failure_retains_tool_owner_and_fixture_for_retry(tmp_path):
    gate = probe(tmp_path)
    agent, tools = gate.agent, gate.tools
    agent.close.side_effect = [RuntimeError("unload busy"), None]
    with pytest.raises(RuntimeError, match="unload busy"):
        gate.close()
    assert gate.panel is None and gate.agent is agent and gate.tools is tools
    tools.close.assert_not_called()
    gate.cmds.delete.assert_not_called()
    assert gate.close()["status"] == "cleanup-passed"
    assert agent.close.call_count == 2
    tools.close.assert_called_once_with()
    gate.cmds.delete.assert_called_once_with("fixture")


def test_probe_does_not_report_cleanup_passed_when_borrowed_service_stops(tmp_path):
    gate = probe(tmp_path)
    gate.agent.close.side_effect = lambda: setattr(gate.server, "is_running", False)
    with pytest.raises(RuntimeError, match="borrowed Core service stopped"):
        gate.close()
    gate.server.stop.assert_not_called()
    gate.cmds.delete.assert_not_called()
    gate.server.is_running = True
    assert gate.close()["status"] == "cleanup-passed"
    gate.cmds.delete.assert_called_once_with("fixture")
