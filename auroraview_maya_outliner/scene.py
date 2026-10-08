"""Maya scene operations, independent of Qt and AuroraView for host-side tests."""

import threading


class SceneAPI:
    """The only Maya commands exposed to the frontend. DAG paths are identities."""

    def __init__(self, commands=None, on_change=None):
        if commands is None:
            import maya.cmds as commands
        self._cmds = commands
        self._on_change = on_change or (lambda: None)

    def _check_thread(self):
        if threading.current_thread() is not threading.main_thread():
            raise RuntimeError("Maya scene operations must run on Maya's main thread.")

    def _path(self, name):
        self._check_thread()
        matches = self._cmds.ls(name, long=True) or []
        if len(matches) != 1:
            raise ValueError("Node is missing or ambiguous: {}".format(name))
        return matches[0]

    def _changed(self, **result):
        self._on_change()
        return dict(ok=True, **result)

    def get_selection(self):
        self._check_thread()
        return self._cmds.ls(selection=True, long=True, objectsOnly=True) or []

    def get_scene_hierarchy(self):
        self._check_thread()
        selected = set(self.get_selection())

        def node(path, parent=None):
            children = self._cmds.listRelatives(path, children=True, fullPath=True) or []
            kind = self._cmds.nodeType(path)
            visible = True
            if self._cmds.attributeQuery("visibility", node=path, exists=True):
                visible = bool(self._cmds.getAttr(path + ".visibility"))
            return {
                "name": path.rsplit("|", 1)[-1], "path": path, "parent": parent,
                "type": "group" if kind == "transform" and not children else kind,
                "visible": visible, "selected": path in selected,
                "children": [node(child, path) for child in children],
            }

        return [node(path) for path in (self._cmds.ls(assemblies=True, long=True) or [])]

    def select_node(self, node_name):
        return self.select_multiple_nodes([node_name])

    def select_multiple_nodes(self, node_names):
        self._check_thread()
        paths = [self._path(name) for name in node_names]
        if paths:
            self._cmds.select(paths, replace=True)
        else:
            self._cmds.select(clear=True)
        return {"ok": True, "nodes": self.get_selection()}

    def set_visibility(self, node_name, visible=True):
        self._cmds.setAttr(self._path(node_name) + ".visibility", bool(visible))
        return self._changed()

    def create_node(self, type="transform", name="group"):
        self._check_thread()
        if type != "transform":
            raise ValueError("This demo creates transform groups only.")
        return self._changed(node=self._cmds.createNode(type, name=name))

    def delete_node(self, node_name):
        self._cmds.delete(self._path(node_name))
        return self._changed()

    def rename_node(self, old_name, new_name):
        if not new_name or "|" in new_name:
            raise ValueError("Use a non-empty leaf name, without a DAG path.")
        return self._changed(node=self._cmds.rename(self._path(old_name), new_name))

    def parent_nodes(self, child_name, parent_name=None):
        child = self._path(child_name)
        if parent_name is None:
            result = self._cmds.parent(child, world=True)
        else:
            parent = self._path(parent_name)
            if parent == child or parent.startswith(child + "|"):
                raise ValueError("A node cannot be parented to itself or its descendant.")
            result = self._cmds.parent(child, parent)
        return self._changed(nodes=result)

    def group_nodes(self, node_name):
        return self._changed(node=self._cmds.group(self._path(node_name), name="group"))

    def ungroup_nodes(self, node_name):
        return self._changed(nodes=self._cmds.ungroup(self._path(node_name)))

    def duplicate_node(self, node_name):
        return self._changed(nodes=self._cmds.duplicate(self._path(node_name), returnRootsOnly=True))

    def hide_in_outliner(self, node_name):
        self._cmds.setAttr(self._path(node_name) + ".hiddenInOutliner", True)
        return self._changed()

    def create_quick_select_set(self, node_name, set_name=None):
        return self._changed(node=self._cmds.sets(self._path(node_name), name=set_name or "quickSelectSet"))


class MayaCallbacks:
    """Register once; remove every callback on close or partial setup failure."""

    def __init__(self, api, on_selection, on_scene):
        self._api = api
        self._on_selection = on_selection
        self._on_scene = on_scene
        self.ids = []

    def start(self):
        if self.ids:
            return
        try:
            events = set(self._api.MEventMessage.getEventNames())
            self.ids.append(self._api.MEventMessage.addEventCallback("SelectionChanged", self._on_selection))
            for name in ("SceneOpened", "NewSceneOpened", "DagObjectCreated", "Undo", "Redo", "NameChanged"):
                if name in events:
                    self.ids.append(self._api.MEventMessage.addEventCallback(name, self._on_scene))
            self.ids.append(self._api.MDGMessage.addNodeAddedCallback(self._on_scene, "dependNode"))
            self.ids.append(self._api.MDGMessage.addNodeRemovedCallback(self._on_scene, "dependNode"))
            self.ids.append(self._api.MDagMessage.addAllDagChangesCallback(self._on_scene))
        except Exception:
            self.close()
            raise

    def close(self):
        callback_ids, self.ids = self.ids, []
        errors = []
        for callback_id in callback_ids:
            try:
                self._api.MMessage.removeCallback(callback_id)
            except Exception as error:
                self.ids.append(callback_id)
                errors.append(error)
        if errors:
            raise errors[0]
