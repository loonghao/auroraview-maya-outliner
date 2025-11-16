"""
Maya Outliner Example for AuroraView

This module demonstrates how to integrate AuroraView with Maya to create
a modern web-based outliner interface.

IMPORTANT: This module is in 'maya_integration' package to avoid namespace
conflicts with Maya's core 'maya' package.
"""

from typing import Any, Dict, List, Optional

try:
    import maya.api.OpenMaya as om
    import maya.cmds as cmds
    import maya.utils as mutils

    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False
    print("[MayaOutliner] Warning: Maya not available, using mock data")

# Import AuroraView components (Qt backend only)
try:
    from auroraview import QtWebView

    print("[MayaOutliner] ✓ AuroraView QtWebView imported successfully")
except ImportError as e:
    print(f"[MayaOutliner] ✗ Failed to import auroraview: {e}")
    print("[MayaOutliner] Make sure auroraview is installed and PYTHONPATH is set correctly")
    raise

# Import Maya Qt components for window handle
omui = None
wrapInstance = None
QWidget = None
QDialog = None
QVBoxLayout = None
try:
    import maya.OpenMayaUI as omui
    from PySide2.QtWidgets import QDialog, QVBoxLayout, QWidget
    from shiboken2 import wrapInstance

    print("[MayaOutliner] ✓ Maya Qt components available")
except ImportError as e:
    print(f"[MayaOutliner] ⚠ Maya Qt components not available: {e}")
    print("[MayaOutliner] Will use standalone mode")


class MayaOutlinerAPI:
    """API object exposed to JavaScript via auroraview.api.*

    This class contains all the methods that can be called from JavaScript.
    Methods on this class become `auroraview.api.<name>` on the JS side.
    """

    def __init__(self, outliner: "MayaOutliner"):
        """Initialize API with reference to parent outliner.

        Args:
            outliner: Parent MayaOutliner instance
        """
        self._outliner = outliner

    def get_scene_hierarchy(self) -> List[Dict[str, Any]]:
        """Get Maya scene hierarchy.

        Returns:
            List of root nodes with their children
        """
        print("[MayaOutlinerAPI] get_scene_hierarchy called")
        hierarchy = self._outliner.get_scene_hierarchy()
        print(f"[MayaOutlinerAPI] Returning {len(hierarchy)} root nodes")
        return hierarchy

    def select_node(self, node_name: str) -> Dict[str, Any]:
        """Select a node in Maya.

        Args:
            node_name: Name of the node to select

        Returns:
            Result dictionary with success status
        """
        print(f"[MayaOutlinerAPI] select_node called: {node_name}")
        try:
            # Direct execution - QtWebView runs in Qt event loop, no need for executeDeferred
            self._outliner.select_node(node_name)
            return {"ok": True, "message": f"Selected: {node_name}"}
        except Exception as e:
            print(f"[MayaOutlinerAPI] Error selecting node: {e}")
            return {"ok": False, "message": str(e)}

    def set_visibility(self, node_name: str, visible: bool = True) -> Dict[str, Any]:
        """Set node visibility in Maya.

        Args:
            node_name: Name of the node
            visible: Whether the node should be visible

        Returns:
            Result dictionary with success status
        """
        print(f"[MayaOutlinerAPI] set_visibility called: {node_name}, visible={visible}")
        try:
            # Direct execution - QtWebView runs in Qt event loop, no need for executeDeferred
            self._outliner.set_visibility(node_name, visible)
            return {"ok": True, "message": f"Set visibility: {node_name} = {visible}"}
        except Exception as e:
            print(f"[MayaOutlinerAPI] Error setting visibility: {e}")
            return {"ok": False, "message": str(e)}


class MayaOutliner:
    """Maya Outliner with AuroraView integration

    Supports singleton mode to ensure only one instance exists at a time.
    """

    # Class-level singleton registry
    _instances: Dict[str, "MayaOutliner"] = {}
    _singleton_lock = None  # Will be initialized when needed

    def __init__(self, singleton_key: Optional[str] = None):
        """Initialize Maya Outliner (simplified - Qt backend only)

        Args:
            singleton_key: If provided, enables singleton mode with this key.
                          Only one instance per key can exist at a time.
        """
        self.webview: Optional[Any] = None  # QtWebView
        self.dialog: Optional[Any] = None  # QDialog container
        self.api: Optional[MayaOutlinerAPI] = None  # API object for JavaScript
        self.callback_ids: List[Any] = []
        self._singleton_key = singleton_key
        self._is_closing = False  # Prevent re-entrant close calls

    def get_node_type(self, node: str) -> str:
        """Get the type of a Maya node"""
        if not MAYA_AVAILABLE:
            return "transform"

        node_type = cmds.nodeType(node)

        # Map Maya node types to simplified types
        type_mapping = {
            "mesh": "mesh",
            "camera": "camera",
            "light": "light",
            "pointLight": "light",
            "directionalLight": "light",
            "spotLight": "light",
            "joint": "joint",
            "locator": "locator",
            "transform": "transform",
        }

        return type_mapping.get(node_type, "unknown")

    def get_scene_hierarchy(self) -> List[Dict[str, Any]]:
        """Get the complete scene hierarchy"""
        if not MAYA_AVAILABLE:
            return self._get_mock_hierarchy()

        def build_node_tree(node: str, parent: Optional[str] = None) -> Dict[str, Any]:
            """Recursively build node tree"""
            children_names = cmds.listRelatives(node, children=True, fullPath=False) or []
            children = [build_node_tree(child, node) for child in children_names]

            # Get visibility
            visible = True
            try:
                visible = cmds.getAttr(f"{node}.visibility")
            except Exception:
                pass

            # Check if selected
            selected = node in (cmds.ls(selection=True) or [])

            return {
                "name": node,
                "type": self.get_node_type(node),
                "path": cmds.ls(node, long=True)[0] if cmds.objExists(node) else node,
                "parent": parent,
                "children": children,
                "visible": visible,
                "selected": selected,
            }

        # Get all root nodes (nodes without parents)
        all_nodes = cmds.ls(assemblies=True) or []
        return [build_node_tree(node) for node in all_nodes]

    def _get_mock_hierarchy(self) -> List[Dict[str, Any]]:
        """Get mock hierarchy for testing without Maya"""
        return [
            {
                "name": "pCube1",
                "type": "transform",
                "path": "|pCube1",
                "parent": None,
                "visible": True,
                "selected": False,
                "children": [
                    {
                        "name": "pCubeShape1",
                        "type": "mesh",
                        "path": "|pCube1|pCubeShape1",
                        "parent": "pCube1",
                        "visible": True,
                        "selected": False,
                        "children": [],
                    }
                ],
            },
            {
                "name": "pSphere1",
                "type": "transform",
                "path": "|pSphere1",
                "parent": None,
                "visible": True,
                "selected": True,
                "children": [
                    {
                        "name": "pSphereShape1",
                        "type": "mesh",
                        "path": "|pSphere1|pSphereShape1",
                        "parent": "pSphere1",
                        "visible": True,
                        "selected": False,
                        "children": [],
                    }
                ],
            },
            {
                "name": "persp",
                "type": "camera",
                "path": "|persp",
                "parent": None,
                "visible": True,
                "selected": False,
                "children": [],
            },
        ]

    def select_node(self, node_name: str):
        """Select a node in Maya"""
        if not MAYA_AVAILABLE:
            print(f"[MayaOutliner] Mock: Select node '{node_name}'")
            return

        try:
            cmds.select(node_name, replace=True)
            print(f"[MayaOutliner] Selected: {node_name}")
        except Exception as e:
            print(f"[MayaOutliner] Error selecting node: {e}")

    def set_visibility(self, node_name: str, visible: bool):
        """Set node visibility"""
        if not MAYA_AVAILABLE:
            print(f"[MayaOutliner] Mock: Set '{node_name}' visibility to {visible}")
            return

        try:
            cmds.setAttr(f"{node_name}.visibility", visible)
            print(f"[MayaOutliner] Set '{node_name}' visibility to {visible}")

            # Notify frontend
            if self.webview:
                self.send_scene_update()
        except Exception as e:
            print(f"[MayaOutliner] Error setting visibility: {e}")

    def send_scene_update(self):
        """Send scene update to frontend"""
        if not self.webview:
            return

        hierarchy = self.get_scene_hierarchy()
        self.webview.emit("scene_updated", hierarchy)

    def send_selection_changed(self):
        """Send selection change to frontend"""
        if not self.webview or not MAYA_AVAILABLE:
            return

        selected = cmds.ls(selection=True)
        if selected:
            self.webview.emit("selection_changed", {"node": selected[0]})

    def setup_maya_callbacks(self):
        """Setup Maya scene callbacks"""
        if not MAYA_AVAILABLE:
            print("[MayaOutliner] Skipping callbacks (Maya not available)")
            return

        # Selection changed callback
        def on_selection_changed(*args):
            self.send_selection_changed()

        # Scene changed callback
        def on_scene_changed(*args):
            self.send_scene_update()

        try:
            # Register callbacks
            sel_callback = om.MEventMessage.addEventCallback(
                "SelectionChanged", on_selection_changed
            )
            scene_callback = om.MEventMessage.addEventCallback("SceneOpened", on_scene_changed)

            self.callback_ids.extend([sel_callback, scene_callback])
            print("[MayaOutliner] Maya callbacks registered")
        except Exception as e:
            print(f"[MayaOutliner] Error registering callbacks: {e}")

    def cleanup_callbacks(self):
        """Remove Maya callbacks"""
        if not MAYA_AVAILABLE:
            return

        for callback_id in self.callback_ids:
            try:
                om.MMessage.removeCallback(callback_id)
            except Exception:
                pass

        self.callback_ids.clear()
        print("[MayaOutliner] Maya callbacks removed")

    @classmethod
    def _get_or_create_singleton(cls, singleton_key: str, factory_fn) -> "MayaOutliner":
        """Get existing singleton instance or create new one

        Args:
            singleton_key: Unique key for this singleton instance
            factory_fn: Function to create new instance if needed

        Returns:
            MayaOutliner instance (existing or newly created)
        """
        # Check if instance already exists
        if singleton_key in cls._instances:
            existing = cls._instances[singleton_key]
            print(f"[MayaOutliner] Singleton '{singleton_key}' already exists")

            # Check if it's still valid (webview not closed)
            if existing.webview is not None:
                print("[MayaOutliner] Returning existing singleton instance")
                return existing
            else:
                print("[MayaOutliner] Existing singleton is closed, creating new one")
                # Remove dead instance
                del cls._instances[singleton_key]

        # Create new instance
        print(f"[MayaOutliner] Creating new singleton instance: '{singleton_key}'")
        instance = factory_fn()
        instance._singleton_key = singleton_key
        cls._instances[singleton_key] = instance
        return instance

    def _remove_from_registry(self):
        """Remove this instance from singleton registry"""
        if self._singleton_key and self._singleton_key in self._instances:
            del self._instances[self._singleton_key]
            print(f"[MayaOutliner] Removed from singleton registry: '{self._singleton_key}'")

    def run(self, url: Optional[str] = None, use_local: bool = False):
        """Run the Maya Outliner WebView

        Args:
            url: URL to load. If None, auto-detect based on use_local flag
            use_local: If True, use local built files. If False, use dev server (default: False)
        """
        # Auto-detect URL if not provided
        if url is None:
            if use_local:
                # Use local built files
                import os

                dist_dir = os.path.join(os.path.dirname(__file__), "..", "dist")
                index_html = os.path.join(dist_dir, "index.html")
                if os.path.exists(index_html):
                    url = f"file:///{os.path.abspath(index_html).replace(os.sep, '/')}"
                    print(f"[MayaOutliner] Using local build: {url}")
                else:
                    print(f"[MayaOutliner] Warning: Local build not found at {dist_dir}")
                    print("[MayaOutliner] Run 'npm run build' to create local build")
                    print("[MayaOutliner] Falling back to dev server")
                    url = "http://localhost:5173"
            else:
                # Use dev server
                url = "http://localhost:5173"
                print(f"[MayaOutliner] Using dev server: {url}")

        print("[MayaOutliner] Creating WebView...")
        print("[MayaOutliner] Backend: Qt (QtWebView)")

        # Get Maya main window as QWidget (for Qt backend)
        maya_window = None
        try:
            if omui is not None and wrapInstance is not None and QWidget is not None:
                # Get Maya main window pointer
                main_window_ptr = omui.MQtUtil.mainWindow()
                if main_window_ptr:
                    # Wrap the pointer to get the QWidget
                    maya_window = wrapInstance(int(main_window_ptr), QWidget)
                    print(f"[MayaOutliner] ✓ Maya main window found")
                else:
                    print("[MayaOutliner] ✗ Could not get Maya main window pointer")
            else:
                print("[MayaOutliner] ✗ Maya Qt not available")
        except Exception as e:
            print(f"[MayaOutliner] ✗ Failed to get Maya window: {e}")
            import traceback
            traceback.print_exc()

        # Create Qt backend WebView (simplified - Qt backend only)
        print("[MayaOutliner] Creating Qt WebView...")

        if maya_window is None:
            raise RuntimeError("Maya main window not found. Cannot create Qt WebView.")

        from qtpy.QtWidgets import QDialog, QVBoxLayout

        # Create QDialog container (parent is Maya main window)
        self.dialog = QDialog(maya_window)
        self.dialog.setWindowTitle("Maya Outliner")
        self.dialog.resize(400, 800)
        self.dialog.setSizeGripEnabled(True)
        self.dialog.setStyleSheet("background-color: #2b2b2b;")

        # Create layout with no margins for full WebView
        layout = QVBoxLayout(self.dialog)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create QtWebView as child widget (parent is dialog, not Maya window!)
        self.webview = QtWebView(self.dialog, dev_tools=True)
        layout.addWidget(self.webview)

        # Load URL
        self.webview.load_url(url)
        print(f"[MayaOutliner] ✓ QtWebView created and loaded: {url}")

        print("[MayaOutliner] Binding API...")

        # Create API object and bind it to auroraview.api.*
        self.api = MayaOutlinerAPI(self)

        # Bind API methods to JavaScript
        if hasattr(self.webview, "bind_api"):
            self.webview.bind_api(self.api, namespace="api")
            print("[MayaOutliner] ✓ API bound to auroraview.api.*")
        else:
            print("[MayaOutliner] ⚠ WebView does not support bind_api, using legacy event handlers")
            # Fallback to legacy event handlers for older backends
            @self.webview.on("get_scene_hierarchy")
            def handle_get_hierarchy(data):
                hierarchy = self.api.get_scene_hierarchy()
                self.webview.emit("scene_updated", hierarchy)

            @self.webview.on("select_node")
            def handle_select_node(data):
                node_name = data.get("node_name")
                if node_name:
                    self.api.select_node(node_name)

            @self.webview.on("set_visibility")
            def handle_set_visibility(data):
                node_name = data.get("node_name")
                visible = data.get("visible", True)
                if node_name is not None:
                    self.api.set_visibility(node_name, visible)

        # Setup Maya callbacks
        self.setup_maya_callbacks()

        # Show QDialog (simplified - Qt backend only)
        print("[MayaOutliner] Showing dialog...")
        self.dialog.show()
        print("[MayaOutliner] ✓ Maya Outliner is running!")
        print("[MayaOutliner] Use outliner.close() to close the window")

    def close(self):
        """Close the WebView window and cleanup (simplified - Qt backend only)"""
        if self._is_closing:
            print("[MayaOutliner] Already closing, skipping...")
            return

        if self.dialog is None and self.webview is None:
            print("[MayaOutliner] Nothing to close")
            self._remove_from_registry()
            return

        print("[MayaOutliner] Closing...")
        self._is_closing = True

        try:
            # Remove Maya callbacks
            self.cleanup_callbacks()

            # Close QDialog (which contains QtWebView)
            if self.dialog is not None:
                self.dialog.close()
                self.dialog = None
                print("[MayaOutliner] ✓ QDialog closed")

            # Clear references
            self.webview = None

            # Remove from singleton registry
            self._remove_from_registry()

            print("[MayaOutliner] ✓ Cleanup complete")

        except Exception as e:
            print(f"[MayaOutliner] ✗ Error closing: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._is_closing = False


def main(
    url: Optional[str] = None,
    use_local: bool = False,
    singleton: bool = True,
):
    """Main entry point (simplified - Qt backend only)

    Args:
        url: URL to load. If None, auto-detect based on use_local flag
        use_local: If True, use local built files. If False, use dev server (default: False)
        singleton: If True, only allow one instance at a time (default: True)

    Usage in Maya:
        >>> from maya_integration import maya_outliner
        >>>
        >>> # Use dev server with singleton mode (default)
        >>> outliner = maya_outliner.main()
        >>>
        >>> # Calling again returns the same instance
        >>> outliner2 = maya_outliner.main()  # Returns existing instance
        >>> assert outliner is outliner2
        >>>
        >>> # Use local build
        >>> outliner = maya_outliner.main(use_local=True)
        >>>
        >>> # Allow multiple instances
        >>> outliner1 = maya_outliner.main(singleton=False)
        >>> outliner2 = maya_outliner.main(singleton=False)  # Creates new instance
        >>>
        >>> # Close the window
        >>> outliner.close()
    """
    print("=" * 60)
    print("Maya Outliner - AuroraView Example")
    print("=" * 60)
    print()

    if not MAYA_AVAILABLE:
        print("⚠ Warning: Running without Maya (using mock data)")
        print()

    print("Backend: Qt (QtWebView)")
    print()

    if singleton:
        # Singleton mode - return existing instance or create new one
        def create_instance():
            outliner = MayaOutliner(singleton_key="maya_outliner_default")
            outliner.run(url=url, use_local=use_local)
            return outliner

        outliner = MayaOutliner._get_or_create_singleton("maya_outliner_default", create_instance)
    else:
        # Multi-instance mode - always create new instance
        outliner = MayaOutliner()
        outliner.run(url=url, use_local=use_local)

    print()
    print("=" * 60)
    print("✓ Maya Outliner started successfully!")
    print("=" * 60)
    print()
    print("Tips:")
    print("  • Click nodes to select them in Maya")
    print("  • Toggle visibility with the eye icon")
    print("  • Use search to filter nodes")
    print("  • Press F12 to open DevTools")
    print("  • Use outliner.close() to close the window")
    if singleton:
        print("  • Singleton mode: Only one instance allowed at a time")
    else:
        print("  • Multi-instance mode: Multiple windows can coexist")
    print()

    return outliner


if __name__ == "__main__":
    main()
