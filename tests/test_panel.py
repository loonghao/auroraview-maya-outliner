"""Check host construction contracts without importing Maya, Qt or a native view."""

import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from auroraview_maya_outliner import maya_outliner


@pytest.fixture
def host(monkeypatch, tmp_path):
    class Dialog:
        def __init__(self, parent=None):
            self.parent = parent
            self.show = Mock()
            self.close = Mock()
            self.resize = Mock()

        def setObjectName(self, name):
            self.name = name

        def setAttribute(self, *_args):
            pass

        def setWindowTitle(self, *_args):
            pass

    class DockMixin:
        def setDockableParameters(self, **options):
            self.dock_options = options

    class View:
        def __init__(self, **options):
            self.options = options
            self.dock_configured = hasattr(options["parent"], "dock_options")
            self.routes = {}
            self.load_file = Mock()
            self.show = Mock()
            self.destroy = Mock()
            self.bind_api = Mock(wraps=self._bind_api)

        def bind_call(self, name, handler):
            self.routes.setdefault(name, []).append(handler)

        def _bind_api(self, api):
            for name in dir(api):
                if not name.startswith("_") and callable(getattr(api, name)):
                    self.bind_call("api." + name, getattr(api, name))

    modules = {
        "auroraview": SimpleNamespace(QtWebView=View),
        "qtpy": SimpleNamespace(),
        "qtpy.QtCore": SimpleNamespace(Qt=SimpleNamespace(WA_DeleteOnClose=1), QTimer=lambda *_: Mock()),
        "qtpy.QtWidgets": SimpleNamespace(QDialog=Dialog, QVBoxLayout=lambda *_: Mock()),
        "maya": SimpleNamespace(),
        "maya.api": SimpleNamespace(),
        "maya.api.OpenMaya": SimpleNamespace(),
        "maya.app": SimpleNamespace(),
        "maya.app.general": SimpleNamespace(),
        "maya.app.general.mayaMixin": SimpleNamespace(MayaQWidgetDockableMixin=DockMixin),
    }
    modules["maya"].api = modules["maya.api"]
    modules["maya.api"].OpenMaya = modules["maya.api.OpenMaya"]
    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)
    scene = SimpleNamespace(_check_thread=Mock())
    parent = object()
    monkeypatch.setattr(maya_outliner, "SceneAPI", Mock(return_value=scene))
    monkeypatch.setattr(maya_outliner, "MayaCallbacks", Mock())
    monkeypatch.setattr(maya_outliner, "_maya_main_window", Mock(return_value=parent))
    monkeypatch.setattr(maya_outliner, "get_index_html_path", lambda: tmp_path / "index.html")
    monkeypatch.setattr(maya_outliner, "get_frontend_url", lambda **_kw: "unused")
    return SimpleNamespace(parent=parent, mixin=DockMixin, scene=scene)


def test_stock_dialog_keeps_maya_parent_and_legacy_routes(host):
    panel = maya_outliner.MayaOutliner().run(use_local=True)
    assert panel.dialog.parent is host.parent
    assert not isinstance(panel.dialog, host.mixin)
    panel.dialog.show.assert_called_once_with()
    panel.webview.bind_api.assert_called_once_with(panel.api)
    assert panel._ui_binding is None
    host.scene._check_thread.assert_called_once_with()


def test_dock_uses_maya_mixin_parenting_and_nonretained_close_callback(host):
    first = maya_outliner.MayaOutliner(dockable=True).run(use_local=True)
    second = maya_outliner.MayaOutliner(dockable=True).run(use_local=True)
    assert isinstance(first.dialog, host.mixin)
    assert first.dialog.parent is None
    assert first.dialog.name != second.dialog.name
    first.dialog.show.assert_called_once_with()
    assert first.dialog.dock_options == {
        "dockable": True, "floating": False, "area": "right", "retain": False,
        "closeCallback": first._dispose,
    }
    assert first.webview.dock_configured
    maya_outliner._maya_main_window.assert_not_called()


def test_frontend_handshake_requires_live_main_thread_panel(host):
    panel = maya_outliner.MayaOutliner().run(use_local=True)
    assert not panel._frontend_ready
    assert panel.frontend_ready() == {"ok": True}
    assert panel._frontend_ready
    host.scene._check_thread.side_effect = RuntimeError("worker refused")
    with pytest.raises(RuntimeError, match="worker refused"):
        panel.frontend_ready()
    host.scene._check_thread.side_effect = None
    panel._closing = True
    with pytest.raises(RuntimeError, match="has closed"):
        panel.frontend_ready()


def test_run_rejects_wrong_thread_before_importing_native_gui(monkeypatch):
    panel = object.__new__(maya_outliner.MayaOutliner)
    panel.api = SimpleNamespace(_check_thread=Mock(side_effect=RuntimeError("worker refused")))
    monkeypatch.setitem(sys.modules, "auroraview", None)
    with pytest.raises(RuntimeError, match="worker refused"):
        panel.run(use_local=True)


@pytest.mark.parametrize("options", [{"dockable": True}, {"tools": object()}])
def test_singleton_does_not_silently_ignore_new_binding_or_dock(options):
    key = "panel-options"
    previous = maya_outliner.MayaOutliner._instances.get(key)
    maya_outliner.MayaOutliner._instances[key] = SimpleNamespace(
        dialog=object(), _dockable=False, _closing=False,
        api=SimpleNamespace(_check_thread=lambda: None),
    )
    try:
        with pytest.raises(RuntimeError, match="Close the existing outliner"):
            maya_outliner.main(singleton_key=key, **options)
    finally:
        if previous is None:
            maya_outliner.MayaOutliner._instances.pop(key)
        else:
            maya_outliner.MayaOutliner._instances[key] = previous


def test_failed_startup_retains_singleton_when_rollback_needs_retry(monkeypatch):
    panel = SimpleNamespace(
        run=Mock(side_effect=RuntimeError("startup failed")),
        close=Mock(side_effect=RuntimeError("cleanup busy")),
    )
    factory = Mock(return_value=panel)
    factory._instances = {}
    monkeypatch.setattr(maya_outliner, "MayaOutliner", factory)
    with pytest.raises(RuntimeError, match="cleanup busy"):
        maya_outliner.main(singleton_key="startup-retry")
    assert factory._instances["startup-retry"] is panel


def test_shared_run_registers_each_legacy_route_once_without_rebinding(host):
    host.scene.rename_node = Mock()
    binding = SimpleNamespace(list_tools=Mock(), call=Mock(return_value={"result": {"ok": True, "node": "|after"}}))
    tools = SimpleNamespace(bind=Mock(return_value=binding))
    panel = maya_outliner.MayaOutliner().run(use_local=True, tools=tools)
    assert all(len(handlers) == 1 for handlers in panel.webview.routes.values())
    handlers = panel.webview.routes["api.rename_node"]
    results = [handler(old_name="|before", new_name="after") for handler in handlers]
    assert results == [{"ok": True, "node": "|after"}]
    binding.call.assert_called_once_with("scene.rename", {"old_name": "|before", "new_name": "after"})
    host.scene.rename_node.assert_not_called()
