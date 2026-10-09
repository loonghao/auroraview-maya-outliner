"""Interactive probe, called through the registered Maya host after UI binding.

This module does not launch Maya or automate input. The caller owns its existing
Core server and the DCC-CUA session. Pixel/input evidence is recorded separately.
"""

import importlib.metadata
import json
import os
import threading
from pathlib import Path
from uuid import uuid4

if __package__:
    from .check_maya_gui_runtime import NATIVE_SHA, verify_native
    from .contract_runtime import inside, verify_runtime
else:
    from check_maya_gui_runtime import NATIVE_SHA, verify_native
    from contract_runtime import inside, verify_runtime


class GuiProbe:
    def __init__(self, server, runtime, wheel, contract_runtime, report, source_commit):
        """Require already-imported fixed public dependencies and a borrowed server."""
        import auroraview
        import auroraview_dcc_mcp
        import dcc_mcp_core
        import qtpy
        import maya.cmds as cmds

        verify_native(runtime, wheel)
        self.artifact = verify_runtime(contract_runtime)
        for module in (auroraview, qtpy):
            assert inside(module.__file__, runtime), module.__file__
        for module in (auroraview_dcc_mcp, dcc_mcp_core):
            assert inside(module.__file__, contract_runtime), module.__file__
        assert importlib.metadata.version("auroraview") == "0.5.12"
        assert importlib.metadata.version("dcc-mcp-core") == "0.20.41"
        assert qtpy.API_NAME == "PySide6"
        assert server.is_running, "Attach to the registered host's running server"
        assert threading.current_thread() is threading.main_thread()
        self.server, self.cmds = server, cmds
        self.report, self.source_commit = Path(report).resolve(), source_commit
        self.main_thread = threading.get_ident()
        self.threads = []
        self.previous_selection = cmds.ls(selection=True, long=True) or []
        self.root = None
        self.panel = self.tools = self.agent = None
        self.workspace = None

    def start(self):
        """Create only a disposable fixture and a docked panel; do not reset the scene."""
        from auroraview_maya_outliner import MayaOutliner
        from auroraview_maya_outliner.tools import create_tools

        assert threading.get_ident() == self.main_thread
        try:
            self.root = self.cmds.group(empty=True, name="av_gui_" + uuid4().hex[:12])
            self.cmds.createNode("transform", name="before", parent=self.root)
            self.cmds.select(self.root + "|before", replace=True)
            self.panel = MayaOutliner(singleton_key=self.root, dockable=True)
            for name in ("rename_node", "get_scene_hierarchy", "get_selection", "select_multiple_nodes"):
                self._observe(name)
            self.tools = create_tools(self.panel.api)
            self.agent = self.tools.attach(self.server)
            self.panel.run(use_local=True, tools=self.tools)
            self.workspace = self.panel.dialog.objectName() + "WorkspaceControl"
        except Exception:
            self.close()
            raise
        return self.state()

    def _observe(self, name):
        handler = getattr(self.panel.api, name)

        def call(*args, **kwargs):
            self.threads.append(threading.get_ident())
            return handler(*args, **kwargs)

        setattr(self.panel.api, name, call)

    def state(self):
        """Typed host readback; invoke only after the exact DCC-CUA target is bound."""
        from auroraview_maya_outliner.maya_outliner import _maya_main_window

        assert threading.get_ident() == self.main_thread
        scene = self.tools.call("scene.snapshot")
        assert self.threads and set(self.threads) == {self.main_thread}
        dock_exists = self.cmds.workspaceControl(self.workspace, query=True, exists=True)
        result = {
            "status": "awaiting-interactive-acceptance", "source_commit": self.source_commit,
            "pid": os.getpid(), "main_hwnd": int(_maya_main_window().winId()),
            "webview_hwnd": self.panel.webview.get_hwnd(),
            "main_thread": self.main_thread, "handler_threads": sorted(set(self.threads)),
            "frontend_ready": self.panel._frontend_ready,
            "workspace": self.workspace, "workspace_exists": dock_exists,
            "floating": self.cmds.workspaceControl(self.workspace, query=True, floating=True) if dock_exists else None,
            "device_pixel_ratio": self.panel.dialog.devicePixelRatioF(),
            "registered_callbacks": len(self.panel._callbacks.ids),
            "scene": scene,
            "tools": dict(self.agent.method_names), "mcp_url": self.server.mcp_url,
            "native_wheel_sha256": NATIVE_SHA, "contract": self.artifact,
            "pixel_input_evidence": "required-separately",
        }
        self._write(result)
        return result

    def close(self):
        """Release this panel's bindings and nodes; preserve the borrowed Core service."""
        assert threading.get_ident() == self.main_thread
        errors = []
        panel = self.panel
        if panel:
            try:
                panel.close()
                assert not (panel._callbacks and panel._callbacks.ids)
                assert panel._ui_binding is None or panel._ui_binding.closed
                assert not getattr(panel, "_cleanup_pending", [])
                assert panel.webview is None and panel.dialog is None
                assert self.tools is None or not self.tools.closed
                assert self.server.is_running
                if self.workspace:
                    assert not self.cmds.workspaceControl(self.workspace, query=True, exists=True)
            except Exception as error:
                errors.append(error)
            else:
                self.panel = None
        for name in ("agent", "tools"):
            resource = getattr(self, name)
            if resource and not errors:
                try:
                    resource.close()
                except Exception as error:
                    errors.append(error)
                else:
                    setattr(self, name, None)
        if not errors and not self.server.is_running:
            errors.append(RuntimeError("The borrowed Core service stopped during cleanup"))
        if not errors:
            try:
                if self.root and self.cmds.objExists(self.root):
                    self.cmds.delete(self.root)
                self.root = None
                selection = [path for path in self.previous_selection if self.cmds.objExists(path)]
                if selection:
                    self.cmds.select(selection, replace=True)
                else:
                    self.cmds.select(clear=True)
            except Exception as error:
                errors.append(error)
        result = {
            "status": "cleanup-failed" if errors else "cleanup-passed",
            "source_commit": self.source_commit, "borrowed_server_running": self.server.is_running,
            "errors": [str(error) for error in errors], "interactive_acceptance": "recorded-separately",
        }
        self._write(result)
        if errors:
            raise RuntimeError("Maya GUI cleanup failed: " + "; ".join(result["errors"]))
        return result

    def _write(self, result):
        self._history = getattr(self, "_history", []) + [result]
        self.report.parent.mkdir(parents=True, exist_ok=True)
        receipt = {"status": result["status"], "stages": self._history}
        self.report.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
