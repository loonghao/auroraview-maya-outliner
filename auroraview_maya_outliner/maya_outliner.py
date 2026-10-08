"""Qt-hosted Maya Outliner. Run main() inside Maya's Script Editor."""

from pathlib import Path

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

    def __init__(self, singleton_key="maya-outliner", context_menu=False):
        self._singleton_key = singleton_key
        self._context_menu = context_menu
        self.dialog = None
        self.webview = None
        self._scene_timer = None
        self._callbacks = None
        self._closing = False
        self.api = SceneAPI(on_change=self._schedule_scene_update)

    def run(self, url=None, use_local=False):
        from auroraview import QtWebView
        from qtpy.QtCore import QTimer, Qt
        from qtpy.QtWidgets import QDialog, QVBoxLayout
        import maya.api.OpenMaya as om

        self.api._check_thread()
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
                finally:
                    super().closeEvent(event)

        self.dialog = OutlinerDialog(_maya_main_window())
        self.dialog.setObjectName("AuroraViewMayaOutliner")
        self.dialog.setAttribute(Qt.WA_DeleteOnClose, True)
        self.dialog.setWindowTitle("AuroraView Maya Outliner")
        self.dialog.resize(500, 800)
        layout = QVBoxLayout(self.dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        self.webview = QtWebView(
            parent=self.dialog,
            dev_tools=True,
            context_menu=self._context_menu,
            asset_root=str(Path(index).parent) if index else None,
        )
        layout.addWidget(self.webview)
        self.webview.bind_api(self.api)
        self.webview.bind_call("api.resize_window", self.resize_window)
        self.webview.bind_call("api.get_window_size", self.get_window_size)
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
        if self._closing and not (self._callbacks and self._callbacks.ids):
            return
        self._closing = True
        cleanup = []
        if self._scene_timer:
            cleanup.append(self._scene_timer.stop)
        if self._callbacks:
            cleanup.append(self._callbacks.close)
        if self.webview:
            cleanup.append(self.webview.destroy)
        errors = []
        for action in cleanup:
            try:
                action()
            except Exception as error:
                errors.append(error)
        self.webview = None
        self._scene_timer = None
        self.dialog = None
        if self._instances.get(self._singleton_key) is self:
            self._instances.pop(self._singleton_key)
        if errors:
            raise errors[0]

    def close(self):
        self.api._check_thread()
        dialog = self.dialog
        try:
            self._dispose()
        finally:
            if dialog:
                dialog.close()


def main(url=None, use_local=False, singleton_key="maya-outliner", context_menu=False):
    """Show or raise one outliner. use_local=True requires a built dist directory."""
    existing = MayaOutliner._instances.get(singleton_key)
    if existing and existing.dialog:
        existing.dialog.show()
        existing.dialog.raise_()
        return existing
    outliner = MayaOutliner(singleton_key, context_menu)
    try:
        outliner.run(url=url, use_local=use_local)
    except Exception:
        outliner.close()
        raise
    MayaOutliner._instances[singleton_key] = outliner
    return outliner
