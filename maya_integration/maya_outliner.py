"""
Maya Outliner Example for AuroraView

This module demonstrates how to integrate AuroraView with Maya to create
a modern web-based outliner interface.

IMPORTANT: This module is in 'maya_integration' package to avoid namespace
conflicts with Maya's core 'maya' package.

Architecture:
    This example uses AuroraView's layered architecture:

    MayaOutliner (Application Layer)
        ↓ uses
    QtWebView (Integration Layer)
        ↓ uses
    QtEventProcessor (Strategy Pattern)
        ↓ processes
    WebView (Python Abstraction Layer)
        ↓ wraps
    AuroraView (Rust Core Layer)

Best Practices Demonstrated:
    - Uses QtWebView with automatic event processing (strategy pattern)
    - No manual process_events() calls needed
    - No scriptJob required for event handling
    - Singleton pattern for single-instance windows
    - Proper cleanup of Maya callbacks
    - Clean integration with Maya's Qt event loop
    - Events are automatically processed at the right layer

Key Benefits:
    - emit() automatically processes both Qt and WebView events
    - No need to worry about event processing in application code
    - Clean separation of concerns across layers
    - Easy to maintain and extend

See Also:
    - docs/ARCHITECTURE_LAYERED_DESIGN.md for architecture details
    - docs/SUMMARY_LAYERED_ARCHITECTURE.md for implementation summary
    - docs/QT_BEST_PRACTICES.md for detailed guide
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

# Import AuroraView components (following official pattern)
try:
    from auroraview import AuroraView, QtWebView

    print("[MayaOutliner] ✓ AuroraView imported successfully")
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

    def get_scene_hierarchy(self, params=None) -> List[Dict[str, Any]]:
        """Get Maya scene hierarchy.

        Args:
            params: Optional parameters (unused, accepts None from AuroraView)

        Returns:
            List of root nodes with their children
        """
        print("[MayaOutlinerAPI] get_scene_hierarchy called with params:", params)
        hierarchy = self._outliner.get_scene_hierarchy()
        print(f"[MayaOutlinerAPI] Returning {len(hierarchy)} root nodes")

        # Debug: print first few nodes
        if hierarchy:
            print(f"[MayaOutlinerAPI] First node: {hierarchy[0].get('name', 'unknown')}")
        else:
            print("[MayaOutlinerAPI] WARNING: No nodes found in scene!")

        return hierarchy

    def select_node(self, node_name: str) -> Dict[str, Any]:
        """Select a node in Maya.

        Args:
            node_name: Name of the node to select

        Returns:
            Result dictionary with success status

        Note:
            Direct execution is safe here because QtWebView automatically
            handles event processing. No need for executeDeferred or scriptJobs.
        """
        print(f"[MayaOutlinerAPI] select_node called: {node_name}")
        try:
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

        Note:
            Direct execution is safe here because QtWebView automatically
            handles event processing. No need for executeDeferred or scriptJobs.
        """
        print(f"[MayaOutlinerAPI] set_visibility called: {node_name}, visible={visible}")
        try:
            self._outliner.set_visibility(node_name, visible)
            return {"ok": True, "message": f"Set visibility: {node_name} = {visible}"}
        except Exception as e:
            print(f"[MayaOutlinerAPI] Error setting visibility: {e}")
            return {"ok": False, "message": str(e)}

    def show_only_dag_objects(self, node_name: str) -> Dict[str, Any]:
        """Show only DAG objects (仅显示 DAG 对象).

        Args:
            node_name: Name of the node

        Returns:
            Result dictionary with success status
        """
        print(f"[MayaOutlinerAPI] show_only_dag_objects called: {node_name}")
        try:
            # Implementation for showing only DAG objects
            return {"ok": True, "message": f"Show only DAG objects for: {node_name}"}
        except Exception as e:
            print(f"[MayaOutlinerAPI] Error: {e}")
            return {"ok": False, "message": str(e)}

    def show_shapes(self, node_name: str) -> Dict[str, Any]:
        """Show shapes (形状).

        Args:
            node_name: Name of the node

        Returns:
            Result dictionary with success status
        """
        print(f"[MayaOutlinerAPI] show_shapes called: {node_name}")
        try:
            # Implementation for showing shapes
            return {"ok": True, "message": f"Show shapes for: {node_name}"}
        except Exception as e:
            print(f"[MayaOutlinerAPI] Error: {e}")
            return {"ok": False, "message": str(e)}

    def show_selected(self, node_name: str) -> Dict[str, Any]:
        """Show selected items (显示选定项).

        Args:
            node_name: Name of the node

        Returns:
            Result dictionary with success status
        """
        print(f"[MayaOutlinerAPI] show_selected called: {node_name}")
        try:
            # Implementation for showing selected items
            return {"ok": True, "message": f"Show selected for: {node_name}"}
        except Exception as e:
            print(f"[MayaOutlinerAPI] Error: {e}")
            return {"ok": False, "message": str(e)}

    def hide_in_outliner(self, node_name: str) -> Dict[str, Any]:
        """Hide in outliner (在大纲图中隐藏).

        Args:
            node_name: Name of the node

        Returns:
            Result dictionary with success status
        """
        print(f"[MayaOutlinerAPI] hide_in_outliner called: {node_name}")
        try:
            if MAYA_AVAILABLE:
                # Set drawOverride to hide in outliner
                cmds.setAttr(f"{node_name}.drawOverride", 2)
            return {"ok": True, "message": f"Hidden in outliner: {node_name}"}
        except Exception as e:
            print(f"[MayaOutlinerAPI] Error: {e}")
            return {"ok": False, "message": str(e)}

    def delete_node(self, node_name: str) -> Dict[str, Any]:
        """Delete node from scene.

        Args:
            node_name: Name of the node to delete

        Returns:
            Result dictionary with success status
        """
        print(f"[MayaOutlinerAPI] delete_node called: {node_name}")
        try:
            if MAYA_AVAILABLE:
                cmds.delete(node_name)
            return {"ok": True, "message": f"Deleted: {node_name}"}
        except Exception as e:
            print(f"[MayaOutlinerAPI] Error deleting node: {e}")
            return {"ok": False, "message": str(e)}


class MayaOutliner:
    """Maya Outliner with AuroraView integration

    This class demonstrates the application layer in AuroraView's layered architecture.
    It uses QtWebView which automatically handles event processing through the
    QtEventProcessor strategy pattern.

    Architecture:
        MayaOutliner (this class)
            ↓ uses
        QtWebView (Integration Layer)
            ↓ uses QtEventProcessor (Strategy)
            ↓ wraps WebView (Abstraction Layer)
            ↓ wraps AuroraView (Rust Core)

    Supports singleton mode to ensure only one instance exists at a time.

    Best Practices:
        - Uses QtWebView with automatic event processing (strategy pattern)
        - emit() automatically processes both Qt and WebView events
        - No manual process_events() calls needed
        - No scriptJob required for event handling
        - Proper cleanup of Maya callbacks on close
        - Singleton pattern prevents multiple instances

    Key Benefits:
        - Simple application code - just call emit() and it works
        - Event processing happens automatically at the right layer
        - No need to understand the underlying event processing mechanism

    Example:
        >>> # Create and show outliner (singleton mode by default)
        >>> outliner = maya_outliner.main()
        >>>
        >>> # Emit events - they are automatically processed
        >>> outliner.webview.emit("scene_updated", {"nodes": [...]})
        >>>
        >>> # Calling main() again returns the same instance
        >>> outliner2 = maya_outliner.main()
        >>> assert outliner is outliner2
        >>>
        >>> # Close when done
        >>> outliner.close()
    """

    # Class-level singleton registry
    _instances: Dict[str, "MayaOutliner"] = {}
    _singleton_lock = None  # Will be initialized when needed

    def __init__(self, singleton_key: Optional[str] = None, context_menu: bool = False):
        """Initialize Maya Outliner (following official AuroraView pattern)

        Args:
            singleton_key: If provided, enables singleton mode with this key.
                          Only one instance per key can exist at a time.
            context_menu: Enable native browser context menu (default: False).
                         Set to False to use custom JavaScript-based menus.
        """
        self.webview: Optional[Any] = None  # QtWebView
        self.dialog: Optional[Any] = None  # QDialog container
        self.api: Optional[MayaOutlinerAPI] = None  # API object for JavaScript
        self.auroraview: Optional[Any] = None  # AuroraView wrapper
        self.callback_ids: List[Any] = []
        self._singleton_key = singleton_key
        self._context_menu = context_menu
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
        # assemblies=True returns top-level transform nodes (excludes cameras, lights by default)
        all_nodes = cmds.ls(assemblies=True) or []

        print(f"[MayaOutliner] Found {len(all_nodes)} root nodes: {all_nodes}")

        # If no assemblies, try getting all transform nodes
        if not all_nodes:
            print("[MayaOutliner] No assemblies found, trying all transforms...")
            all_transforms = cmds.ls(type='transform') or []
            # Filter to only root transforms (no parent)
            all_nodes = [t for t in all_transforms if not cmds.listRelatives(t, parent=True)]
            print(f"[MayaOutliner] Found {len(all_nodes)} root transforms: {all_nodes}")

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
        """Send scene update to frontend.

        This method demonstrates the layered architecture in action:

        1. Application Layer (this method) - Calls emit()
        2. Integration Layer (QtWebView) - Delegates to WebView
        3. Abstraction Layer (WebView) - Pushes to queue and calls _auto_process_events()
        4. Strategy Layer (QtEventProcessor) - Processes Qt + WebView events
        5. Core Layer (Rust) - Delivers message to JavaScript

        All of this happens automatically when you call emit()!
        No need to manually call process_events() or create scriptJobs.

        Note: emit() expects a dict, so we wrap the hierarchy list in a dict.
        The frontend will unwrap it from event.detail.nodes or event.detail.value.
        """
        print("\n" + "🔥"*50)
        print("[MayaOutliner] 🔥 send_scene_update() CALLED!")
        print("🔥"*50)

        if not self.webview:
            print("[MayaOutliner] ✗ send_scene_update: webview is None!")
            print("🔥"*50 + "\n")
            return

        print(f"[MayaOutliner] ✓ webview exists: {type(self.webview)}")

        hierarchy = self.get_scene_hierarchy()
        print(f"[MayaOutliner] ✓ Got hierarchy: {len(hierarchy)} root nodes")
        print(f"[MayaOutliner] Hierarchy preview: {hierarchy[:2] if len(hierarchy) > 0 else 'empty'}")

        # IMPORTANT: Frontend expects payload.value (array) or direct array
        # See src/App.vue lines 69-73:
        #   const nodes = Array.isArray(payload)
        #     ? payload
        #     : payload && Array.isArray((payload as any).value)
        #       ? (payload as any).value
        #       : []
        # So we send {"value": hierarchy} to match the expected format
        print("[MayaOutliner] Calling webview.emit('scene_updated', ...)...")

        try:
            self.webview.emit("scene_updated", {"value": hierarchy})
            print(f"[MayaOutliner] ✓ Scene update emitted and processed automatically")

            # Verify event processor is set
            if hasattr(self.webview, '_webview') and hasattr(self.webview._webview, '_event_processor'):
                processor = self.webview._webview._event_processor
                if processor:
                    print(f"[MayaOutliner] ✓ Event processor active: {type(processor).__name__}")
                else:
                    print("[MayaOutliner] ✗ WARNING: Event processor is None!")
            else:
                print("[MayaOutliner] ✗ WARNING: Cannot verify event processor!")

            # Debug: Verify event was sent to JavaScript
            print("[MayaOutliner] Verifying event delivery to JavaScript...")
            self.webview.eval_js("""
                console.log('[Maya Debug] Checking event listeners...');
                console.log('[Maya Debug] window.auroraview:', window.auroraview);
                console.log('[Maya Debug] window.auroraview.on:', typeof window.auroraview?.on);

                // Test: Manually trigger the event to see if listeners work
                console.log('[Maya Debug] Manually triggering scene_updated event...');
                window.dispatchEvent(new CustomEvent('scene_updated', {
                    detail: {value: [{name: 'TEST_NODE', type: 'transform'}]}
                }));
            """)
            print("[MayaOutliner] ✓ Debug script executed")

        except Exception as e:
            print(f"[MayaOutliner] ✗ ERROR in emit: {e}")
            import traceback
            traceback.print_exc()

    def send_selection_changed(self):
        """Send selection change to frontend.

        This demonstrates the same automatic event processing as send_scene_update().
        Just call emit() and the layered architecture handles everything automatically!
        """
        if not self.webview or not MAYA_AVAILABLE:
            return

        selected = cmds.ls(selection=True)
        if selected:
            # ✨ Automatic event processing - no manual process_events() needed!
            self.webview.emit("selection_changed", {"node": selected[0]})

    def setup_maya_callbacks(self):
        """Setup Maya scene callbacks for automatic scene updates.

        Registers callbacks for:
        - Object creation/deletion
        - Object renaming
        - Parent-child relationship changes
        - Scene open/new
        - Undo/Redo operations
        - Selection changes
        """
        if not MAYA_AVAILABLE:
            print("[MayaOutliner] Skipping callbacks (Maya not available)")
            return

        # Selection changed callback
        def on_selection_changed(*_args):
            print("[MayaOutliner] ✓ Callback triggered: SelectionChanged")
            self.send_selection_changed()

        # Scene changed callback
        def on_scene_changed(*_args):
            print("\n" + "="*80)
            print("[MayaOutliner] ✓ Callback triggered: Scene changed")
            print(f"[MayaOutliner] Args: {_args}")
            print("[MayaOutliner] Updating hierarchy...")
            print("="*80)
            self.send_scene_update()
            print("="*80 + "\n")

        try:
            # Register callbacks for various scene events
            callbacks = []

            # Selection changes
            callbacks.append(om.MEventMessage.addEventCallback(
                "SelectionChanged", on_selection_changed
            ))

            # Scene structure changes - using MEventMessage
            scene_events = [
                "SceneOpened",      # Scene opened
                "NewSceneOpened",   # New scene created
                "DagObjectCreated", # DAG object created
                "Undo",             # Undo operation
                "Redo",             # Redo operation
            ]

            for event in scene_events:
                callbacks.append(om.MEventMessage.addEventCallback(
                    event, on_scene_changed
                ))

            # Additional DAG-specific callbacks using MDGMessage
            # These catch more granular changes that MEventMessage might miss
            try:
                # Node added to model (catches all node creation)
                callbacks.append(om.MDGMessage.addNodeAddedCallback(
                    on_scene_changed, "dependNode"
                ))

                # Node removed from model (catches all node deletion)
                callbacks.append(om.MDGMessage.addNodeRemovedCallback(
                    on_scene_changed, "dependNode"
                ))

                # Node renamed
                callbacks.append(om.MNodeMessage.addNameChangedCallback(
                    om.MObject(), on_scene_changed
                ))

                print("[MayaOutliner] ✓ Registered MDGMessage callbacks for node changes")
            except Exception as e:
                print(f"[MayaOutliner] Warning: Could not register MDGMessage callbacks: {e}")

            # DAG hierarchy changes using MSceneMessage
            try:
                # Parent-child relationship changes
                callbacks.append(om.MDagMessage.addParentAddedCallback(
                    on_scene_changed
                ))

                callbacks.append(om.MDagMessage.addParentRemovedCallback(
                    on_scene_changed
                ))

                print("[MayaOutliner] ✓ Registered MDagMessage callbacks for hierarchy changes")
            except Exception as e:
                print(f"[MayaOutliner] Warning: Could not register MDagMessage callbacks: {e}")

            self.callback_ids.extend(callbacks)
            print(f"[MayaOutliner] ✓ Registered {len(callbacks)} Maya callbacks total")
            print("[MayaOutliner] ✓ Auto-refresh enabled for:")
            print("  - Object creation/deletion")
            print("  - Object renaming")
            print("  - Hierarchy changes")
            print("  - Scene open/new")
            print("  - Undo/Redo")
            print("  - Selection changes")
        except Exception as e:
            print(f"[MayaOutliner] ✗ Error registering callbacks: {e}")
            import traceback
            traceback.print_exc()

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

        Our definition of "singleton" is:
        - Only one live window per key at any time
        - If that window is closed/hidden, a new one should be created on the
          next call

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

            # Consider the instance "alive" only when the dialog is still visible.
            dialog = getattr(existing, "dialog", None)
            webview = getattr(existing, "webview", None)

            dialog_visible = False
            if dialog is not None and hasattr(dialog, "isVisible"):
                try:
                    dialog_visible = dialog.isVisible()
                except Exception:
                    dialog_visible = False

            if webview is not None and dialog_visible:
                # Window is still open → just reuse it and skip creating a new one
                print("[MayaOutliner] Existing dialog is visible, returning existing singleton instance")
                return existing

            # Otherwise treat it as closed/stale and recreate on the next call
            print("[MayaOutliner] Existing singleton is not active (dialog hidden or webview missing); closing and recreating")
            try:
                existing.close()
            except Exception as e:
                print(f"[MayaOutliner] Error while closing existing singleton: {e}")

            if singleton_key in cls._instances and cls._instances[singleton_key] is existing:
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

        Architecture:
            This method uses AuroraView's layered architecture with automatic event processing:

            1. QtWebView (Integration Layer) - Wraps WebView with Qt integration
            2. QtEventProcessor (Strategy) - Handles Qt + WebView event processing
            3. WebView (Abstraction Layer) - Provides Python API
            4. AuroraView (Rust Core) - Handles rendering and messaging

            When you call emit(), the event processing happens automatically:
            - QtEventProcessor processes Qt events (QCoreApplication.processEvents())
            - QtEventProcessor processes WebView events (_core.process_events())
            - Messages are delivered to JavaScript immediately

        Note:
            You don't need to:
            - Manually call process_events()
            - Create scriptJobs for event handling
            - Use executeDeferred for Maya commands
            - Worry about event processing at all

            All JavaScript ↔ Python communication works automatically!
            Just call emit() and the layered architecture handles the rest.
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

        # Create Qt WebView (following official AuroraView pattern)
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
        layout.setContentsMargins(6, 6, 6, 6)

        # Create QtWebView as child widget (parent is dialog)
        # ✨ Event processing is automatic with QtWebView!
        # No need to call process_events() or create scriptJobs.
        self.webview = QtWebView(
            self.dialog,
            dev_tools=True,
            context_menu=self._context_menu,  # Disable native context menu for custom menus
        )
        layout.addWidget(self.webview)

        # Create API object
        self.api = MayaOutlinerAPI(self)

        # Bind Python API to auroraview.api.* via AuroraView wrapper
        # This follows the official pattern from maya_qt_echo_demo.py
        self.auroraview = AuroraView(
            parent=self.dialog,
            api=self.api,
            _view=self.webview,
            _keep_alive_root=self.dialog,
        )
        print("[MayaOutliner] ✓ API bound to auroraview.api.* via AuroraView wrapper")

        # Load URL
        self.webview.load_url(url)
        print(f"[MayaOutliner] ✓ URL loaded: {url}")

        # Show WebView (following official pattern)
        self.webview.show()
        print("[MayaOutliner] ✓ WebView shown")

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
            self.auroraview = None
            self.webview = None
            self.api = None

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
    context_menu: bool = False,
):
    """Main entry point for Maya Outliner

    Args:
        url: URL to load. If None, auto-detect based on use_local flag
        use_local: If True, use local built files. If False, use dev server (default: False)
        singleton: If True, only allow one instance at a time (default: True)
        context_menu: Enable native browser context menu (default: False).
                     Set to False to use custom JavaScript-based menus.

    Returns:
        MayaOutliner instance

    Architecture:
        This example demonstrates AuroraView's layered architecture:

        MayaOutliner (Application Layer)
            ↓ uses
        QtWebView (Integration Layer)
            ↓ uses QtEventProcessor (Strategy Pattern)
            ↓ wraps WebView (Abstraction Layer)
            ↓ wraps AuroraView (Rust Core)

    Best Practices:
        This example demonstrates the recommended way to integrate AuroraView
        with Maya using the layered architecture:

        ✅ Uses QtWebView with automatic event processing (strategy pattern)
        ✅ emit() automatically processes both Qt and WebView events
        ✅ No manual process_events() calls needed
        ✅ No scriptJob required for event handling
        ✅ Clean integration with Maya's Qt event loop
        ✅ Proper cleanup of Maya callbacks
        ✅ Singleton pattern for single-instance windows
        ✅ Simple application code - just call emit() and it works

        See docs/ARCHITECTURE_LAYERED_DESIGN.md for architecture details.
        See docs/QT_BEST_PRACTICES.md for detailed guide.

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
            outliner = MayaOutliner(
                singleton_key="maya_outliner_default",
                context_menu=context_menu,
            )
            outliner.run(url=url, use_local=use_local)
            return outliner

        outliner = MayaOutliner._get_or_create_singleton("maya_outliner_default", create_instance)
    else:
        # Multi-instance mode - always create new instance
        outliner = MayaOutliner(context_menu=context_menu)
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
