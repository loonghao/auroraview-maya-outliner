"""Scene contract tests run without Maya, Qt or AuroraView."""
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from auroraview_maya_outliner.scene import MayaCallbacks, SceneAPI


class Commands:
    def __init__(self):
        self.selected = []
        self.nodes = {
            "|left": {"children": ["|left|same"], "visible": True},
            "|left|same": {"children": [], "visible": True},
            "|right": {"children": ["|right|same"], "visible": True},
            "|right|same": {"children": [], "visible": False},
        }

    def ls(self, name=None, selection=False, assemblies=False, **_kwargs):
        if selection:
            return self.selected[:]
        if assemblies:
            return [path for path in self.nodes if path.count("|") == 1]
        return [path for path in self.nodes if path == name or path.rsplit("|", 1)[-1] == name]

    def select(self, paths=None, clear=False, **_kwargs):
        self.selected = [] if clear else paths[:]

    def listRelatives(self, path, **_kwargs):
        return self.nodes[path]["children"]

    def nodeType(self, _path):
        return "transform"

    def attributeQuery(self, *_args, **_kwargs):
        return True

    def getAttr(self, attribute):
        return self.nodes[attribute.rsplit(".", 1)[0]]["visible"]

    def setAttr(self, attribute, value):
        self.nodes[attribute.rsplit(".", 1)[0]]["visible"] = value


@pytest.fixture
def commands():
    return Commands()


def test_duplicate_names_use_full_paths(commands):
    scene = SceneAPI(commands)
    scene.select_node("|left|same")
    roots = scene.get_scene_hierarchy()
    assert roots[0]["children"][0]["selected"] is True
    assert roots[1]["children"][0]["selected"] is False
    assert roots[0]["children"][0]["parent"] == "|left"
    assert roots[0]["children"][0]["name"] == "same"


@pytest.mark.parametrize("name", ["same", "missing"])
def test_missing_and_ambiguous_nodes_reject_before_mutation(commands, name):
    scene = SceneAPI(commands)
    with pytest.raises(ValueError):
        scene.select_node(name)
    assert commands.selected == []


def test_multiple_and_empty_selection(commands):
    scene = SceneAPI(commands)
    result = scene.select_multiple_nodes(["|left|same", "|right|same"])
    assert result["nodes"] == ["|left|same", "|right|same"]
    assert scene.select_multiple_nodes([])["nodes"] == []


def test_visibility_updates_real_target_and_notifies(commands):
    changed = Mock()
    scene = SceneAPI(commands, changed)
    scene.set_visibility("|left|same", False)
    assert commands.nodes["|left|same"]["visible"] is False
    assert commands.nodes["|right|same"]["visible"] is False
    changed.assert_called_once_with()


def test_host_error_propagates_to_rpc(commands):
    commands.setAttr = Mock(side_effect=RuntimeError("attribute locked"))
    with pytest.raises(RuntimeError, match="locked"):
        SceneAPI(commands).set_visibility("|left|same", False)


def test_worker_thread_cannot_call_maya(commands):
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(SceneAPI(commands).get_scene_hierarchy)
        with pytest.raises(RuntimeError, match="main thread"):
            future.result()


def test_parent_cycle_rejected_before_host_mutation(commands):
    commands.parent = Mock()
    with pytest.raises(ValueError, match="descendant"):
        SceneAPI(commands).parent_nodes("|left", "|left|same")
    commands.parent.assert_not_called()


def callback_api(fail=False):
    ids = iter(range(1, 30))
    register = Mock(side_effect=lambda *_: next(ids))
    return SimpleNamespace(
        MEventMessage=SimpleNamespace(
            getEventNames=lambda: ["SelectionChanged", "Undo"],
            addEventCallback=register,
        ),
        MDGMessage=SimpleNamespace(
            addNodeAddedCallback=register,
            addNodeRemovedCallback=register,
        ),
        MDagMessage=SimpleNamespace(
            addAllDagChangesCallback=Mock(side_effect=RuntimeError("host failed")) if fail else register,
        ),
        MMessage=SimpleNamespace(removeCallback=Mock()),
    )


def test_callbacks_register_once_and_remove_every_id():
    host = callback_api()
    callbacks = MayaCallbacks(host, Mock(), Mock())
    callbacks.start()
    registered = callbacks.ids[:]
    callbacks.start()
    assert callbacks.ids == registered
    callbacks.close()
    callbacks.close()
    assert callbacks.ids == []
    assert [call.args[0] for call in host.MMessage.removeCallback.call_args_list] == registered


def test_partial_callback_registration_rolls_back():
    host = callback_api(fail=True)
    callbacks = MayaCallbacks(host, Mock(), Mock())
    with pytest.raises(RuntimeError, match="host failed"):
        callbacks.start()
    assert callbacks.ids == []
    assert host.MMessage.removeCallback.call_count == 4


def test_callback_removal_failure_attempts_remaining_ids_and_can_retry():
    host = callback_api()
    callbacks = MayaCallbacks(host, Mock(), Mock())
    callbacks.start()
    registered = callbacks.ids[:]

    def remove(callback_id):
        if callback_id == registered[1]:
            raise RuntimeError("callback removal failed")

    host.MMessage.removeCallback.side_effect = remove
    with pytest.raises(RuntimeError, match="callback removal failed"):
        callbacks.close()
    assert [call.args[0] for call in host.MMessage.removeCallback.call_args_list] == registered
    assert callbacks.ids == [registered[1]]

    host.MMessage.removeCallback.side_effect = None
    callbacks.close()
    assert callbacks.ids == []
    assert host.MMessage.removeCallback.call_args.args == (registered[1],)

