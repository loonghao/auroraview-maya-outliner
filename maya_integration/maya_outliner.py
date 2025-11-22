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
except ImportError as e:
    print(f"[MayaOutliner] Failed to import auroraview: {e}")
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
except ImportError as e:
    pass  # Will use standalone mode


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

    def select_multiple_nodes(self, node_names: List[str]) -> Dict[str, Any]:
        """Select multiple nodes in Maya.

        Args:
            node_names: List of node names to select

        Returns:
            Result dictionary with success status
        """
        print(f"[MayaOutlinerAPI] select_multiple_nodes called: {node_names}")
        try:
            if MAYA_AVAILABLE:
                cmds.select(node_names, replace=True)
            return {"ok": True, "message": f"Selected {len(node_names)} nodes"}
        except Exception as e:
            print(f"[MayaOutlinerAPI] Error selecting multiple nodes: {e}")
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

    def group_nodes(self, node_name: str) -> Dict[str, Any]:
        """Group selected nodes (成组).

        Args:
            node_name: Name of the node (will group current selection)

        Returns:
            Result dictionary with success status and group name
        """
        print(f"[MayaOutlinerAPI] group_nodes called: {node_name}")
        try:
            if MAYA_AVAILABLE:
                # Select the node first
                cmds.select(node_name, replace=True)
                # Group the selection
                group_name = cmds.group(name=f"{node_name}_grp")
                return {"ok": True, "message": f"Grouped: {group_name}", "group_name": group_name}
            return {"ok": True, "message": "Group created (standalone mode)"}
        except Exception as e:
            print(f"[MayaOutlinerAPI] Error grouping nodes: {e}")
            return {"ok": False, "message": str(e)}

    def ungroup_nodes(self, node_name: str) -> Dict[str, Any]:
        """Ungroup nodes (取消成组).

        Args:
            node_name: Name of the group to ungroup

        Returns:
            Result dictionary with success status
        """
        print(f"[MayaOutlinerAPI] ungroup_nodes called: {node_name}")
        try:
            if MAYA_AVAILABLE:
                cmds.ungroup(node_name)
            return {"ok": True, "message": f"Ungrouped: {node_name}"}
        except Exception as e:
            print(f"[MayaOutlinerAPI] Error ungrouping nodes: {e}")
            return {"ok": False, "message": str(e)}

    def parent_nodes(self, child_name: str, parent_name: str = None) -> Dict[str, Any]:
        """Parent node to another node or to world (父级).

        Args:
            child_name: Name of the child node
            parent_name: Name of the parent node (None for world)

        Returns:
            Result dictionary with success status
        """
        print(f"[MayaOutlinerAPI] parent_nodes called: child={child_name}, parent={parent_name}")
        try:
            if MAYA_AVAILABLE:
                if parent_name:
                    cmds.parent(child_name, parent_name)
                    return {"ok": True, "message": f"Parented {child_name} to {parent_name}"}
                else:
                    cmds.parent(child_name, world=True)
                    return {"ok": True, "message": f"Parented {child_name} to world"}
            return {"ok": True, "message": "Parent operation completed (standalone mode)"}
        except Exception as e:
            print(f"[MayaOutlinerAPI] Error parenting nodes: {e}")
            return {"ok": False, "message": str(e)}

    def duplicate_node(self, node_name: str) -> Dict[str, Any]:
        """Duplicate node (复制).

        Args:
            node_name: Name of the node to duplicate

        Returns:
            Result dictionary with success status and new node name
        """
        print(f"[MayaOutlinerAPI] duplicate_node called: {node_name}")
        try:
            if MAYA_AVAILABLE:
                duplicated = cmds.duplicate(node_name, returnRootsOnly=True)
                new_name = duplicated[0] if duplicated else None
                return {"ok": True, "message": f"Duplicated: {new_name}", "new_name": new_name}
            return {"ok": True, "message": "Duplicate created (standalone mode)"}
        except Exception as e:
            print(f"[MayaOutlinerAPI] Error duplicating node: {e}")
            return {"ok": False, "message": str(e)}

    def rename_node(self, old_name: str, new_name: str) -> Dict[str, Any]:
        """Rename node (重命名).

        Args:
            old_name: Current name of the node
            new_name: New name for the node

        Returns:
            Result dictionary with success status
        """
        print(f"[MayaOutlinerAPI] rename_node called: {old_name} -> {new_name}")
        try:
            if MAYA_AVAILABLE:
                cmds.rename(old_name, new_name)
            return {"ok": True, "message": f"Renamed: {old_name} -> {new_name}"}
        except Exception as e:
            print(f"[MayaOutlinerAPI] Error renaming node: {e}")
            return {"ok": False, "message": str(e)}

    def create_quick_select_set(self, node_name: str, set_name: str = None) -> Dict[str, Any]:
        """Create quick select set (创建快速选择集).

        Args:
            node_name: Name of the node to add to set
            set_name: Name of the set (auto-generated if None)

        Returns:
            Result dictionary with success status and set name
        """
        print(f"[MayaOutlinerAPI] create_quick_select_set called: {node_name}, set={set_name}")
        try:
            if MAYA_AVAILABLE:
                if not set_name:
                    set_name = f"{node_name}_set"
                # Create a quick select set
                new_set = cmds.sets(node_name, name=set_name)
                return {"ok": True, "message": f"Created set: {new_set}", "set_name": new_set}
            return {"ok": True, "message": "Quick select set created (standalone mode)"}
        except Exception as e:
            print(f"[MayaOutlinerAPI] Error creating quick select set: {e}")
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
        if not self.webview:
            return

        hierarchy = self.get_scene_hierarchy()

        # IMPORTANT: Frontend expects payload.value (array) or direct array
        # See src/App.vue lines 69-73:
        #   const nodes = Array.isArray(payload)
        #     ? payload
        #     : payload && Array.isArray((payload as any).value)
        #       ? (payload as any).value
        #       : []
        try:
            self.webview.emit("scene_updated", {"value": hierarchy})
        except Exception as e:
            print(f"[MayaOutliner] Error in emit: {e}")

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
            self.send_selection_changed()

        # Scene changed callback
        def on_scene_changed(*_args):
            self.send_scene_update()

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

            except Exception as e:
                print(f"[MayaOutliner] Warning: Could not register MDagMessage callbacks: {e}")

            self.callback_ids.extend(callbacks)
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
                return existing

            # Otherwise treat it as closed/stale and recreate on the next call
            try:
                existing.close()
            except Exception as e:
                pass

            if singleton_key in cls._instances and cls._instances[singleton_key] is existing:
                del cls._instances[singleton_key]

        # Create new instance
        instance = factory_fn()
        instance._singleton_key = singleton_key
        cls._instances[singleton_key] = instance
        return instance

    def _remove_from_registry(self):
        """Remove this instance from singleton registry"""
        if self._singleton_key and self._singleton_key in self._instances:
            del self._instances[self._singleton_key]

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
                else:
                    url = "http://localhost:5173"
            else:
                # Use dev server
                url = "http://localhost:5173"

        # Get Maya main window as QWidget (for Qt backend)
        maya_window = None
        try:
            if omui is not None and wrapInstance is not None and QWidget is not None:
                # Get Maya main window pointer
                main_window_ptr = omui.MQtUtil.mainWindow()
                if main_window_ptr:
                    # Wrap the pointer to get the QWidget
                    maya_window = wrapInstance(int(main_window_ptr), QWidget)
        except Exception as e:
            pass

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
        # Event processing is automatic with QtWebView!
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

        # Load URL
        self.webview.load_url(url)

        # Show WebView (following official pattern)
        self.webview.show()

        # Setup Maya callbacks
        self.setup_maya_callbacks()

        # Show QDialog (simplified - Qt backend only)
        self.dialog.show()

    def close(self):
        """Close the WebView window and cleanup (simplified - Qt backend only)"""
        if self._is_closing:
            return

        if self.dialog is None and self.webview is None:
            self._remove_from_registry()
            return

        self._is_closing = True

        try:
            # Remove Maya callbacks
            self.cleanup_callbacks()

            # Close QDialog (which contains QtWebView)
            if self.dialog is not None:
                self.dialog.close()
                self.dialog = None

            # Clear references
            self.auroraview = None
            self.webview = None
            self.api = None

            # Remove from singleton registry
            self._remove_from_registry()

        except Exception as e:
            print(f"[MayaOutliner] Error closing: {e}")
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
    print("Maya Outliner started successfully!")
    print("=" * 60)
    print()

    return outliner


if __name__ == "__main__":
    main()
