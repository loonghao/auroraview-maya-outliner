"""Probe orchestration fakes do not certify native UI behavior."""

import inspect
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import auroraview_maya_outliner
from auroraview_maya_outliner import maya_outliner
from scripts.maya_gui_probe import GuiProbe


def panel(generation=1):
    result = SimpleNamespace(
        _callbacks=SimpleNamespace(ids=[], close=Mock()),
        _ui_binding=SimpleNamespace(closed=False), _cleanup_pending=[],
        _frontend_ready=True,
        webview=SimpleNamespace(get_hwnd=lambda: 5678),
        dialog=SimpleNamespace(objectName=lambda: "view" + str(generation), devicePixelRatioF=lambda: 1.5),
    )

    def dispose():
        result._callbacks.close()
        result._ui_binding.closed = True
        result.webview = result.dialog = None

    result.close = Mock(side_effect=dispose)
    return result


class Runtime:
    """Model only the runtime's public ownership and delegation boundary."""

    def __init__(self, server, attached=True):
        self.server, self.closed = server, False
        self.scene = SimpleNamespace(**{
            name: Mock(return_value=[]) for name in (
                "rename_node", "get_scene_hierarchy", "get_selection", "select_multiple_nodes",
            )
        })
        self.tools = self.agent = None
        self.panel = panel() if attached else None
        self.generation = 1 if attached else 0
        self.on_attach = lambda: None
        self.attach = Mock(side_effect=self._attach)
        self.open = Mock(side_effect=self._open)
        self.close_view = Mock(side_effect=self._close_view)
        self.close = Mock(side_effect=self._close)
        if attached:
            self._attach()

    def _attach(self):
        if self.tools is None:
            self.on_attach()
            self.agent = SimpleNamespace(
                closed=False, token="never-record-this-token",
                method_names={"scene.rename": "maya-outliner__scene_rename"},
            )
            self.agent.close = Mock(side_effect=lambda: setattr(self.agent, "closed", True))
            self.tools = SimpleNamespace(id="stable-owner", closed=False)
            self.tools.call = Mock(side_effect=lambda _name: {
                "hierarchy": self.scene.get_scene_hierarchy(), "selection": self.scene.get_selection(),
            })
            self.tools.close = Mock(side_effect=self._close_tools)
        return self.agent

    def _open(self, **_options):
        if self.closed:
            raise RuntimeError("runtime closed")
        if self.tools is None:
            self.attach()
        if self.panel is None:
            self.generation += 1
            self.panel = panel(self.generation)
        return self.panel

    def _close_view(self):
        if self.panel is not None:
            self.panel.close()
            self.panel = None

    def _close_tools(self):
        self.tools.closed = True
        if self.agent is not None:
            self.agent.close()

    def _close(self):
        self._close_view()
        if self.tools is not None:
            self.tools.close()
        self.agent, self.closed = None, True


@pytest.fixture(autouse=True)
def main_window(monkeypatch):
    monkeypatch.setattr(maya_outliner, "_maya_main_window", lambda: SimpleNamespace(winId=lambda: 1234))


def probe(tmp_path):
    result = object.__new__(GuiProbe)
    result.server = SimpleNamespace(is_running=True, mcp_url="http://127.0.0.1:12345/mcp", stop=Mock())
    result.cmds = SimpleNamespace(
        group=Mock(return_value="fixture"), createNode=Mock(), workspaceControl=Mock(return_value=False),
        objExists=Mock(return_value=True), delete=Mock(), select=Mock(),
    )
    result.report, result.source_commit = tmp_path / "gui.json", "candidate"
    result.main_thread = threading.get_ident()
    result.threads, result.previous_selection = [result.main_thread], ["|original"]
    result.root, result.workspace = "fixture", "fixtureWorkspaceControl"
    result.owner = Runtime(result.server)
    result._stable_tools, result._stable_agent = result.tools, result.agent
    result.view_generation, result._view_cleanup = 1, None
    result._fixture_restored, result.artifact = False, {}
    return result


def test_probe_delegates_final_cleanup_and_restores_selection_once(tmp_path):
    gate = probe(tmp_path)
    owner, agent, tools = gate.owner, gate.agent, gate.tools
    assert gate.close()["status"] == gate.close()["status"] == "cleanup-passed"
    owner.close.assert_called_once_with()
    gate.server.stop.assert_not_called()
    agent.close.assert_called_once_with()
    tools.close.assert_called_once_with()
    assert gate.owner is owner and owner.closed
    gate.cmds.delete.assert_called_once_with("fixture")
    gate.cmds.select.assert_called_once_with(["|original"], replace=True)


def test_probe_cleanup_failure_retains_runtime_panel_and_fixture_for_retry(tmp_path):
    gate = probe(tmp_path)
    owner, first_panel, agent, tools = gate.owner, gate.panel, gate.agent, gate.tools
    first_panel._callbacks.ids = [2]
    first_panel._callbacks.close.side_effect = RuntimeError("callback removal failed")
    with pytest.raises(RuntimeError, match="callback removal failed"):
        gate.close()
    assert gate.owner is owner and gate.panel is first_panel
    assert gate.agent is agent and gate.tools is tools
    agent.close.assert_not_called()
    tools.close.assert_not_called()
    gate.cmds.delete.assert_not_called()
    assert json.loads(gate.report.read_text(encoding="utf-8"))["status"] == "cleanup-failed"
    first_panel._callbacks.close.side_effect = lambda: first_panel._callbacks.ids.clear()
    assert gate.close()["status"] == "cleanup-passed"
    assert gate.panel is None and gate.agent is None and gate.tools.closed
    assert owner.close.call_count == 2
    gate.server.stop.assert_not_called()


def test_probe_records_view_generation_and_retention_without_token(tmp_path):
    gate = probe(tmp_path)
    state = gate.state()
    assert state["mcp_url"] == "http://127.0.0.1:12345/mcp"
    assert state["main_hwnd"] == 1234 and state["webview_hwnd"] == 5678
    assert state["frontend_ready"] and state["view_open"] and state["view_generation"] == 1
    assert state["tool_owner_retained"] and state["agent_binding_retained"]
    assert state["status"] == "awaiting-interactive-acceptance"
    assert gate.agent.token not in gate.report.read_text(encoding="utf-8")
    assert state["pixel_input_evidence"] == "required-separately"


@pytest.mark.parametrize("method", ["start", "state", "open_view", "close_view", "close"])
def test_probe_rejects_worker_entry_before_host_or_runtime_calls(tmp_path, method):
    gate = probe(tmp_path)
    with ThreadPoolExecutor(max_workers=1) as executor:
        with pytest.raises(AssertionError):
            executor.submit(getattr(gate, method)).result()
    gate.owner.open.assert_not_called()
    gate.owner.close_view.assert_not_called()
    gate.owner.close.assert_not_called()
    gate.tools.call.assert_not_called()
    gate.cmds.group.assert_not_called()
    gate.cmds.delete.assert_not_called()


def test_probe_final_owner_failure_retains_resources_until_runtime_retry_succeeds(tmp_path):
    gate = probe(tmp_path)
    owner, agent, tools = gate.owner, gate.agent, gate.tools
    agent.close.side_effect = [RuntimeError("unload busy"), None]
    with pytest.raises(RuntimeError, match="unload busy"):
        gate.close()
    assert gate.panel is None and gate.owner is owner and not owner.closed
    assert gate.agent is agent and gate.tools is tools
    gate.cmds.delete.assert_not_called()
    assert gate.close()["status"] == "cleanup-passed"
    assert owner.close.call_count == tools.close.call_count == agent.close.call_count == 2
    gate.cmds.delete.assert_called_once_with("fixture")


def test_probe_does_not_restore_fixture_when_borrowed_service_stops(tmp_path):
    gate = probe(tmp_path)
    gate.agent.close.side_effect = lambda: setattr(gate.server, "is_running", False)
    with pytest.raises(RuntimeError, match="borrowed Core service stopped"):
        gate.close()
    gate.server.stop.assert_not_called()
    gate.cmds.delete.assert_not_called()
    gate.server.is_running = True
    assert gate.close()["status"] == "cleanup-passed"
    gate.owner.close.assert_called_once_with()
    gate.cmds.delete.assert_called_once_with("fixture")


def test_probe_close_and_reopen_only_replace_view_generation(tmp_path):
    gate = probe(tmp_path)
    owner, first_panel, tools, agent = gate.owner, gate.panel, gate.tools, gate.agent
    closed = gate.close_view()
    assert closed["status"] == "view-closed" and not closed["view_open"]
    assert closed["view_generation"] == 1
    assert closed["tool_owner_retained"] and closed["agent_binding_retained"]
    owner.close_view.assert_called_once_with()
    owner.close.assert_not_called()
    tools.close.assert_not_called()
    agent.close.assert_not_called()
    gate.cmds.delete.assert_not_called()
    gate.cmds.select.assert_not_called()
    assert gate.root == "fixture"
    reopened = gate.open_view()
    assert gate.owner is owner and gate.panel is not first_panel
    assert gate.tools is tools and gate.agent is agent
    assert reopened["view_generation"] == 2
    assert reopened["tool_owner_retained"] and reopened["agent_binding_retained"]
    assert gate.open_view()["view_generation"] == 2
    owner.attach.assert_not_called()
    gate.server.stop.assert_not_called()


def test_probe_start_instruments_scene_before_attach_and_creates_fixture_once(tmp_path, monkeypatch):
    gate = probe(tmp_path)
    runtime = Runtime(gate.server, attached=False)
    original, checked = dict(vars(runtime.scene)), []
    runtime.on_attach = lambda: checked.append(all(
        getattr(runtime.scene, name) is not handler for name, handler in original.items()
    ))
    factory = Mock(return_value=runtime)
    monkeypatch.setattr(auroraview_maya_outliner, "OutlinerRuntime", factory, raising=False)
    gate.owner = gate.root = gate._stable_tools = gate._stable_agent = None
    gate.view_generation, gate.threads = 0, []
    assert gate.start()["view_generation"] == 1 and checked == [True]
    assert gate.threads and set(gate.threads) == {gate.main_thread}
    factory.assert_called_once_with(gate.server, commands=gate.cmds, singleton_key="fixture", dockable=True)
    gate.close_view()
    assert gate.start()["view_generation"] == 2
    assert gate.cmds.group.call_count == gate.cmds.createNode.call_count == 1
    runtime.attach.assert_called_once_with()
    factory.assert_called_once()


def test_probe_retains_failed_view_readback_and_blocks_reopen_until_retry(tmp_path):
    gate = probe(tmp_path)
    first_panel = gate.panel
    gate.cmds.workspaceControl.side_effect = [True, False]
    with pytest.raises(AssertionError):
        gate.close_view()
    assert gate.panel is None and gate._view_cleanup[0] is first_panel
    with pytest.raises(RuntimeError, match="cleanup is pending"):
        gate.open_view()
    gate.owner.open.assert_not_called()
    assert gate.close_view()["status"] == "view-closed"
    first_panel.close.assert_called_once_with()
    assert gate._view_cleanup is None
    gate.tools.close.assert_not_called()
    gate.cmds.delete.assert_not_called()


def test_probe_retries_fixture_restore_without_reclosing_successful_runtime(tmp_path):
    gate = probe(tmp_path)
    gate.cmds.select.side_effect = [RuntimeError("selection busy"), None]
    with pytest.raises(RuntimeError, match="selection busy"):
        gate.close()
    assert gate.owner.closed and not gate._fixture_restored
    assert gate.close()["status"] == "cleanup-passed"
    gate.owner.close.assert_called_once_with()
    gate.cmds.delete.assert_called_once_with("fixture")
    assert gate.cmds.select.call_count == 2


def test_probe_view_startup_failure_retains_original_owner_for_retry(tmp_path, monkeypatch):
    gate = probe(tmp_path)
    runtime = Runtime(gate.server, attached=False)
    retained = []

    def fail_view(**_options):
        runtime.attach()
        retained.append((runtime.tools, runtime.agent))
        raise RuntimeError("view startup failed")

    runtime.open.side_effect = fail_view
    factory = Mock(return_value=runtime)
    monkeypatch.setattr(auroraview_maya_outliner, "OutlinerRuntime", factory, raising=False)
    gate.owner = gate.root = gate._stable_tools = gate._stable_agent = None
    gate.view_generation = 0
    with pytest.raises(RuntimeError, match="view startup failed"):
        gate.start()
    assert gate.owner is runtime and gate.root == "fixture"
    assert not runtime.closed
    runtime.close.assert_not_called()
    gate.cmds.delete.assert_not_called()
    runtime.open.side_effect = runtime._open
    assert gate.open_view()["view_generation"] == 1
    assert (gate.tools, gate.agent) == retained[0]
    runtime.attach.assert_called_once_with()
    factory.assert_called_once()
    gate.cmds.group.assert_called_once()
    gate.cmds.createNode.assert_called_once()


def test_probe_construction_rollback_retains_owner_when_final_cleanup_needs_retry(tmp_path, monkeypatch):
    gate = probe(tmp_path)
    runtime = Runtime(gate.server, attached=False)
    del runtime.scene.rename_node
    runtime.close.side_effect = RuntimeError("owner cleanup busy")
    monkeypatch.setattr(auroraview_maya_outliner, "OutlinerRuntime", Mock(return_value=runtime), raising=False)
    gate.owner = gate.root = None
    with pytest.raises(RuntimeError, match="owner cleanup busy"):
        gate.start()
    assert gate.owner is runtime and gate.root == "fixture"
    runtime.open.assert_not_called()
    gate.cmds.delete.assert_not_called()
    runtime.close.side_effect = runtime._close
    assert gate.close()["status"] == "cleanup-passed"
    gate.cmds.delete.assert_called_once_with("fixture")


def test_probe_observer_preserves_scene_signature_and_records_handler_thread(tmp_path):
    gate = probe(tmp_path)

    def rename(old_name, new_name="after"):
        return old_name, new_name

    gate.owner.scene.rename_node = rename
    gate._observe("rename_node")
    observed = gate.owner.scene.rename_node
    assert observed.__wrapped__ is rename
    assert inspect.signature(observed) == inspect.signature(rename)
    assert observed("before") == ("before", "after")
    assert gate.threads[-1] == gate.main_thread
