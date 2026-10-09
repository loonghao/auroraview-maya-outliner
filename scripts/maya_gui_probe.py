"""Interactive probe, called through the registered Maya host after UI binding.

This module does not launch Maya or automate input. The caller owns its existing
Core server and the DCC-CUA session. Pixel/input evidence is recorded separately.
"""

import importlib.metadata
import json
import os
import threading
from functools import wraps
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
        self.owner = None
        self.workspace = None
        self.view_generation = 0
        self._stable_tools = self._stable_agent = None
        self._view_cleanup = None
        self._fixture_restored = False

    @property
    def panel(self):
        return self.owner.panel if self.owner is not None else None

    @property
    def tools(self):
        return self.owner.tools if self.owner is not None else None

    @property
    def agent(self):
        return self.owner.agent if self.owner is not None else None

    def start(self):
        """Create one disposable fixture and retain its host-owned tool runtime."""
        assert threading.get_ident() == self.main_thread
        from auroraview_maya_outliner import OutlinerRuntime
        if self.owner is not None:
            return self.open_view()
        try:
            self.root = self.cmds.group(empty=True, name="av_gui_" + uuid4().hex[:12])
            self.cmds.createNode("transform", name="before", parent=self.root)
            self.cmds.select(self.root + "|before", replace=True)
            self.owner = OutlinerRuntime(self.server, commands=self.cmds, singleton_key=self.root, dockable=True)
            for name in ("rename_node", "get_scene_hierarchy", "get_selection", "select_multiple_nodes"):
                self._observe(name)
        except Exception:
            self.close()
            raise
        return self.open_view()

    def open_view(self, url=None, use_local=True):
        """Open a new UI generation without replacing its tools or agent binding."""
        assert threading.get_ident() == self.main_thread
        if self.owner is None or self.owner.closed:
            raise RuntimeError("Start a live probe runtime before opening its view")
        if self._view_cleanup is not None:
            raise RuntimeError("Previous view cleanup is pending. Retry close_view() first.")
        previous = self.panel
        panel = self.owner.open(url=url, use_local=use_local)
        if self._stable_tools is None:
            self._stable_tools, self._stable_agent = self.tools, self.agent
        else:
            assert self.tools is self._stable_tools and self.agent is self._stable_agent
        if panel is not previous:
            self.view_generation += 1
        self.workspace = panel.dialog.objectName() + "WorkspaceControl"
        return self.state()

    def close_view(self):
        """Release only this UI generation and verify the host owner is retained."""
        assert threading.get_ident() == self.main_thread
        if self.owner is None or self.owner.closed:
            raise RuntimeError("The probe runtime is not live")
        if self._view_cleanup is None and self.panel is not None:
            self._view_cleanup = (self.panel, self.workspace)
        try:
            self.owner.close_view()
            if self._view_cleanup is not None:
                self._check_view_cleanup(*self._view_cleanup)
            assert not self.tools.closed
            assert self.tools is self._stable_tools and self.agent is self._stable_agent
            assert self.server.is_running, "The borrowed Core service stopped during view cleanup"
        except Exception as error:
            self._write({
                "status": "view-cleanup-failed", "source_commit": self.source_commit,
                "view_generation": self.view_generation, "errors": [str(error)],
                **self._retention(),
            })
            raise
        self._view_cleanup = None
        self.workspace = None
        return self.state()

    def _observe(self, name):
        handler = getattr(self.owner.scene, name)

        @wraps(handler)
        def call(*args, **kwargs):
            self.threads.append(threading.get_ident())
            return handler(*args, **kwargs)

        setattr(self.owner.scene, name, call)

    def _retention(self):
        return {
            "tool_owner_id": getattr(self.tools, "id", None),
            "tool_owner_retained": self.tools is not None and self.tools is self._stable_tools and not self.tools.closed,
            "agent_binding_retained": self.agent is not None and self.agent is self._stable_agent and not self.agent.closed,
        }

    def _check_view_cleanup(self, panel, workspace):
        assert not (panel._callbacks and panel._callbacks.ids)
        assert panel._ui_binding is None or panel._ui_binding.closed
        assert not getattr(panel, "_cleanup_pending", [])
        assert panel.webview is None and panel.dialog is None
        if workspace:
            assert not self.cmds.workspaceControl(workspace, query=True, exists=True)

    def state(self):
        """Typed host readback; invoke only after the exact DCC-CUA target is bound."""
        assert threading.get_ident() == self.main_thread
        from auroraview_maya_outliner.maya_outliner import _maya_main_window
        if self.tools is None or self.tools.closed or self.agent is None:
            raise RuntimeError("The probe runtime is not live")
        scene = self.tools.call("scene.snapshot")
        assert self.threads and set(self.threads) == {self.main_thread}
        panel = self.panel
        dock_exists = bool(self.workspace and self.cmds.workspaceControl(self.workspace, query=True, exists=True))
        result = {
            "status": "awaiting-interactive-acceptance" if panel else "view-closed", "source_commit": self.source_commit,
            "pid": os.getpid(), "main_hwnd": int(_maya_main_window().winId()),
            "webview_hwnd": panel.webview.get_hwnd() if panel else None,
            "main_thread": self.main_thread, "handler_threads": sorted(set(self.threads)),
            "frontend_ready": bool(panel and panel._frontend_ready),
            "view_generation": self.view_generation, "view_open": panel is not None,
            **self._retention(),
            "workspace": self.workspace, "workspace_exists": dock_exists,
            "floating": self.cmds.workspaceControl(self.workspace, query=True, floating=True) if dock_exists else None,
            "device_pixel_ratio": panel.dialog.devicePixelRatioF() if panel else None,
            "registered_callbacks": len(panel._callbacks.ids) if panel and panel._callbacks else 0,
            "scene": scene,
            "tools": dict(self.agent.method_names), "mcp_url": self.server.mcp_url,
            "native_wheel_sha256": NATIVE_SHA, "contract": self.artifact,
            "pixel_input_evidence": "required-separately",
        }
        self._write(result)
        return result

    def close(self):
        """Close the host owner, then restore its fixture; retain failures for retry."""
        assert threading.get_ident() == self.main_thread
        errors = []
        if self.owner is not None:
            if self._view_cleanup is None and self.panel is not None:
                self._view_cleanup = (self.panel, self.workspace)
            try:
                if not self.owner.closed:
                    self.owner.close()
                assert self.owner.closed
                if self._view_cleanup is not None:
                    self._check_view_cleanup(*self._view_cleanup)
            except Exception as error:
                errors.append(error)
            else:
                self._view_cleanup = None
                self.workspace = None
        if not errors and not self.server.is_running:
            errors.append(RuntimeError("The borrowed Core service stopped during cleanup"))
        if not errors and not self._fixture_restored:
            try:
                if self.root and self.cmds.objExists(self.root):
                    self.cmds.delete(self.root)
                self.root = None
                selection = [path for path in self.previous_selection if self.cmds.objExists(path)]
                if selection:
                    self.cmds.select(selection, replace=True)
                else:
                    self.cmds.select(clear=True)
                self._fixture_restored = True
            except Exception as error:
                errors.append(error)
        result = {
            "status": "cleanup-failed" if errors else "cleanup-passed",
            "source_commit": self.source_commit, "borrowed_server_running": self.server.is_running,
            "view_generation": self.view_generation,
            "owner_closed": bool(self.owner and self.owner.closed),
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
