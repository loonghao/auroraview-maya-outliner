"""Shared contract behavior; no Maya SDK, Qt or native view is imported."""

from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

contracts = pytest.importorskip("auroraview_dcc_mcp", reason="Run vx just test-contracts <wheel>")

from auroraview_maya_outliner.scene import SceneAPI
from auroraview_maya_outliner.tools import create_tools
from auroraview_maya_outliner.maya_outliner import MayaOutliner
from tests.test_scene import Commands


@pytest.fixture
def scene():
    commands = Commands()

    def rename(path, name):
        new_path = path.rsplit("|", 1)[0] + "|" + name
        commands.nodes[new_path] = commands.nodes.pop(path)
        parent = path.rsplit("|", 1)[0]
        children = commands.nodes[parent]["children"]
        children[children.index(path)] = new_path
        return new_path

    commands.rename = Mock(side_effect=rename)
    return SceneAPI(commands)


def test_explicit_tools_share_existing_handlers_and_host_readback(scene):
    with create_tools(scene) as tools:
        descriptors = {tool["name"]: tool for tool in tools.list_tools()}
        assert set(descriptors) == {"scene.snapshot", "scene.rename"}
        assert tools.dcc == "maya"
        assert descriptors["scene.snapshot"]["annotations"]["readOnlyHint"]
        result = tools.call("scene.rename", {"old_name": "|left|same", "new_name": "renamed"})
        scene._cmds.rename.assert_called_once_with("|left|same", "renamed")
        assert result["result"] == {"ok": True, "node": "|left|renamed"}
        assert result["scene"] == tools.call("scene.snapshot")
        assert result["scene"]["hierarchy"][0]["children"][0]["path"] == "|left|renamed"


@pytest.mark.parametrize("params", [
    {"old_name": "|left|same", "new_name": ""},
    {"old_name": "|left|same", "new_name": "|bad"},
    {"old_name": "|left|same", "new_name": "valid", "unexpected": True},
])
def test_invalid_rename_is_refused_before_maya_mutation(scene, params):
    with create_tools(scene) as tools:
        with pytest.raises(contracts.ContractError):
            tools.call("scene.rename", params)
        scene._cmds.rename.assert_not_called()


def test_ui_binding_and_borrowed_session_have_independent_lifetimes(scene):
    routes = {}
    view = SimpleNamespace(bind_call=lambda name, handler: routes.update({name: handler}))
    tools = create_tools(scene)
    session = tools.borrow()
    ui = tools.bind(view)
    snapshot = routes["scene.snapshot"]
    assert snapshot() == session.call("scene.snapshot")
    ui.close()
    with pytest.raises(contracts.ClosedError):
        snapshot()
    assert session.call("scene.snapshot")["hierarchy"]
    tools.close()
    with pytest.raises(contracts.ClosedError):
        session.call("scene.snapshot")


def test_host_subscription_is_removed_when_owner_closes(scene):
    unsubscribe = Mock()
    subscribe = Mock(return_value=unsubscribe)
    tools = create_tools(scene, subscribe=subscribe)
    session = tools.borrow()
    session.subscribe("scene.changed", Mock())
    subscribe.assert_called_once()
    tools.close()
    unsubscribe.assert_called_once_with()


def test_worker_call_is_refused_before_business_handler(scene):
    with create_tools(scene) as tools, ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(tools.call, "scene.rename", {"old_name": "|left|same", "new_name": "after"})
        with pytest.raises(contracts.ThreadError):
            future.result()
        scene._cmds.rename.assert_not_called()


def test_panel_borrows_shared_rename_and_preserves_legacy_result(scene):
    class AccumulatingView:
        def __init__(self):
            self.routes = {}

        def bind_call(self, name, handler):
            self.routes.setdefault(name, []).append(handler)

        def bind_api(self, api):
            for name in dir(api):
                if not name.startswith("_") and callable(getattr(api, name)):
                    self.bind_call("api." + name, getattr(api, name))

        def dispatch(self, name, **params):
            return [handler(**params) for handler in self.routes[name]]

    panel = object.__new__(MayaOutliner)
    panel._ui_binding = None
    panel.api = scene
    panel.webview = AccumulatingView()
    original_rename = scene.rename_node
    scene.get_scene_hierarchy = Mock(wraps=scene.get_scene_hierarchy)
    scene.get_selection = Mock(wraps=scene.get_selection)
    tools = create_tools(scene)
    try:
        panel._bind_tools(tools)
        assert {"scene.snapshot", "scene.rename", "api.rename_node"} <= set(panel.webview.routes)
        assert all(len(handlers) == 1 for handlers in panel.webview.routes.values())
        assert scene.rename_node == original_rename
        with pytest.raises(contracts.ContractError):
            panel.webview.dispatch("api.rename_node", old_name="|left|same", new_name="|invalid")
        scene._cmds.rename.assert_not_called()
        result = panel.webview.dispatch("api.rename_node", old_name="|left|same", new_name="shared")
        assert result == [{"ok": True, "node": "|left|shared"}]
        scene._cmds.rename.assert_called_once_with("|left|same", "shared")
        scene.get_scene_hierarchy.assert_called_once_with()
        scene.get_selection.assert_called_with()
        assert panel.webview.dispatch("scene.snapshot") == [tools.call("scene.snapshot")]
        panel._ui_binding.close()
        with pytest.raises(contracts.ClosedError):
            panel.webview.dispatch("api.rename_node", old_name="|left|shared", new_name="stale")
        assert not tools.closed
        assert tools.call("scene.snapshot")["hierarchy"]
    finally:
        tools.close()


def test_stock_panel_does_not_import_or_bind_optional_contracts():
    panel = object.__new__(MayaOutliner)
    panel._ui_binding = None
    panel.api = object()
    panel.webview = SimpleNamespace(bind_call=Mock(), bind_api=Mock())
    panel._bind_tools(None)
    panel.webview.bind_api.assert_called_once_with(panel.api)
    panel.webview.bind_call.assert_not_called()
    assert panel._ui_binding is None


def test_closed_ui_binding_with_failed_unsubscribe_is_retried_before_release(scene):
    unsubscribe = Mock(side_effect=[RuntimeError("host busy"), None])
    tools = create_tools(scene, subscribe=Mock(return_value=unsubscribe))
    panel = object.__new__(MayaOutliner)
    panel._singleton_key = "binding-retry"
    panel._scene_timer = None
    panel._callbacks = SimpleNamespace(ids=[], close=Mock())
    panel.api = scene
    view = SimpleNamespace(bind_call=Mock(), destroy=Mock())
    dialog = SimpleNamespace(close=Mock())
    panel.webview, panel.dialog = view, dialog
    panel._ui_binding = tools.bind(view)
    panel._ui_binding.subscribe("scene.changed", Mock())
    try:
        with pytest.raises(contracts.CleanupError):
            panel.close()
        assert panel._ui_binding.closed
        assert panel.dialog is dialog and not tools.closed
        unsubscribe.assert_called_once_with()
        dialog.close.assert_not_called()
        panel.close()
        assert unsubscribe.call_count == 2
        assert panel.dialog is None and not tools.closed
        view.destroy.assert_called_once_with()
        dialog.close.assert_called_once_with()
        assert tools.call("scene.snapshot")["hierarchy"]
    finally:
        tools.close()
