"""Qt-hosted Maya Outliner. Run main() inside Maya's Script Editor."""

from pathlib import Path
from uuid import uuid4

from .config import get_frontend_url, get_index_html_path, is_production
from .scene import MayaCallbacks, SceneAPI


def _maya_main_window():
    import maya.OpenMayaUI as omui
    from qtpy.QtWidgets import QWidget

    try:
        from shiboken6 import wrapInstance
    except ImportError:
        from shiboken2 import wrapInstance

    pointer = omui.MQtUtil.mainWindow()
    if not pointer:
        raise RuntimeError("Start this demo in interactive Maya, after its UI has loaded.")
    return wrapInstance(int(pointer), QWidget)


class MayaOutliner:
    """Own the Qt dialog, bridge and Maya callbacks on Maya's UI thread."""

    _instances = {}

    def __init__(self, singleton_key="maya-outliner", context_menu=False, dockable=False):
        self._singleton_key = singleton_key
        self._context_menu = context_menu
        self._dockable = dockable
        self._ui_binding = None
        self._frontend_ready = False
        self.dialog = None
        self.webview = None
        self._scene_timer = None
        self._callbacks = None
        self._cleanup_pending = None
        self._closing = False
        self.api = SceneAPI(on_change=self._schedule_scene_update)

    def run(self, url=None, use_local=False, tools=None):
        self.api._check_thread()
        from auroraview import QtWebView
        from qtpy.QtCore import QTimer, Qt
        from qtpy.QtWidgets import QDialog, QVBoxLayout
        import maya.api.OpenMaya as om

        static = url is None and (use_local or is_production())
        index = get_index_html_path() if static else None
        if static and index is None:
            raise FileNotFoundError("Frontend missing. Run vx just install and vx just build first.")
        frontend_url = url or get_frontend_url(force_production=use_local)
        owner = self

        class OutlinerDialog(QDialog):
            def closeEvent(self, event):
                try:
                    owner._dispose()
                except Exception:
                    event.ignore()
                    raise
                super().closeEvent(event)

        if self._dockable:
            from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

            class DockedOutliner(MayaQWidgetDockableMixin, OutlinerDialog):
                pass

            # Maya's mixin owns workspaceControl parenting. Parenting directly
            # to the main window first can create a separate native window.
            self.dialog = DockedOutliner(parent=None)
            self.dialog.setObjectName("AuroraViewMayaOutliner_" + uuid4().hex)
        else:
            self.dialog = OutlinerDialog(_maya_main_window())
            self.dialog.setObjectName("AuroraViewMayaOutliner")
        self.dialog.setAttribute(Qt.WA_DeleteOnClose, True)
        self.dialog.setWindowTitle("AuroraView Maya Outliner")
        self.dialog.resize(500, 800)
        layout = QVBoxLayout(self.dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        if self._dockable:
            # The public QtWebView constructor captures its native HWND.
            # Establish Maya's final parent before constructing that child.
            self.dialog.setDockableParameters(
                dockable=True, floating=False, area="right", retain=False,
                closeCallback=self._dispose,
            )
        self.webview = QtWebView(
            parent=self.dialog,
            dev_tools=True,
            context_menu=self._context_menu,
            asset_root=str(Path(index).parent) if index else None,
        )
        layout.addWidget(self.webview)
        self.webview.bind_api(self.api)
        self._bind_tools(tools)
        self.webview.bind_call("api.resize_window", self.resize_window)
        self.webview.bind_call("api.get_window_size", self.get_window_size)
        self.webview.bind_call("api.frontend_ready", self.frontend_ready)
        self._scene_timer = QTimer(self.dialog)
        self._scene_timer.setSingleShot(True)
        self._scene_timer.setInterval(50)
        self._scene_timer.timeout.connect(self.send_scene_update)
        self._callbacks = MayaCallbacks(om, self.send_selection_changed, self._schedule_scene_update)
        self._callbacks.start()
        try:
            if index:
                self.webview.load_file(str(index))
            else:
                self.webview.load_url(frontend_url)
            self.dialog.show()
            self.webview.show()
        except Exception:
            self.close()
            raise
        return self

    def _bind_tools(self, tools):
        """Borrow UI routes; the caller retains the ToolSet and Core service."""
        if tools is None:
            return
        binding = tools.bind(self.webview)
        self._ui_binding = binding

        def rename(old_name, new_name):
            # Preserve the stock Vue call and result while sharing the exact
            # schema, handler and scene readback with registered agent tools.
            return binding.call(
                "scene.rename", {"old_name": old_name, "new_name": new_name},
            )["result"]

        self.webview.bind_call("api.rename_node", rename)

    def frontend_ready(self):
        """Acknowledge the Vue mount, initial scene read and event subscription."""
        self.api._check_thread()
        if self._closing:
            raise RuntimeError("The outliner has closed.")
        self._frontend_ready = True
        return {"ok": True}

    def resize_window(self, width, height):
        self.api._check_thread()
        self.dialog.resize(max(320, min(int(width), 4096)), max(240, min(int(height), 4096)))
        return self.get_window_size()

    def get_window_size(self):
        self.api._check_thread()
        return {"ok": True, "width": self.dialog.width(), "height": self.dialog.height()}

    def _schedule_scene_update(self, *_args):
        if not self._closing and self._scene_timer and not self._scene_timer.isActive():
            self._scene_timer.start()

    def send_scene_update(self):
        if self.webview and not self._closing:
            self.webview.emit("scene_updated", {"nodes": self.api.get_scene_hierarchy()})
            self.send_selection_changed()

    def send_selection_changed(self, *_args):
        if self.webview and not self._closing:
            nodes = self.api.get_selection()
            self.webview.emit("selection_changed", {"nodes": nodes, "node": nodes[-1] if nodes else None})

    def _dispose(self):
        self._closing = True
        self._frontend_ready = False
        if getattr(self, "_cleanup_pending", None) is None:
            self._cleanup_pending = []
            binding = getattr(self, "_ui_binding", None)
            for name, resource, method in (
                ("_scene_timer", self._scene_timer, "stop"),
                ("_ui_binding", binding, "close"),
                ("_callbacks", self._callbacks, "close"),
                ("webview", self.webview, "destroy"),
            ):
                if resource:
                    self._cleanup_pending.append((name, getattr(resource, method)))
        errors = []
        for entry in tuple(self._cleanup_pending):
            name, action = entry
            try:
                action()
            except Exception as error:
                errors.append(error)
            else:
                self._cleanup_pending.remove(entry)
                if name in ("_scene_timer", "webview"):
                    setattr(self, name, None)
        if not self._cleanup_pending:
            self.dialog = None
            if self._instances.get(self._singleton_key) is self:
                self._instances.pop(self._singleton_key)
        if errors:
            raise errors[0]

    def close(self):
        self.api._check_thread()
        dialog = self.dialog
        registered = self._instances.get(self._singleton_key) is self
        self._dispose()
        if dialog:
            try:
                if dialog.close() is False:
                    raise RuntimeError("The native outliner window refused to close.")
            except Exception:
                self.dialog = dialog
                if registered:
                    self._instances[self._singleton_key] = self
                raise


def main(url=None, use_local=False, singleton_key="maya-outliner", context_menu=False,
         dockable=False, tools=None):
    """Show or raise one outliner. use_local=True requires a built dist directory."""
    existing = MayaOutliner._instances.get(singleton_key)
    if existing and existing.dialog:
        existing.api._check_thread()
        if existing._closing:
            raise RuntimeError("Previous outliner cleanup is pending. Retry close() first.")
        if existing._dockable != dockable or tools is not None:
            raise RuntimeError("Close the existing outliner before changing its dock or tool binding.")
        existing.dialog.show()
        existing.dialog.raise_()
        return existing
    outliner = MayaOutliner(singleton_key, context_menu, dockable)
    # Retain the cleanup owner even when startup and its rollback both fail.
    MayaOutliner._instances[singleton_key] = outliner
    try:
        outliner.run(url=url, use_local=use_local, tools=tools)
    except Exception:
        outliner.close()
        raise
    return outliner
