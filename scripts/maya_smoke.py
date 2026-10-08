"""Real Maya DAG/callback smoke test; runs in an isolated mayapy process."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import maya.standalone
maya.standalone.initialize(name="python")

try:
    import maya.cmds as cmds
    import maya.api.OpenMaya as om
    from auroraview_maya_outliner.scene import MayaCallbacks, SceneAPI

    cmds.file(new=True, force=True)
    cmds.group(empty=True, name="av_demo_left")
    cmds.group(empty=True, name="av_demo_right")
    cmds.createNode("transform", name="same", parent="av_demo_left")
    cmds.createNode("transform", name="same", parent="av_demo_right")
    left_path = "|av_demo_left|same"
    right_path = "|av_demo_right|same"
    scene = SceneAPI()
    assert scene.select_node(left_path)["nodes"] == [left_path]
    scene.select_multiple_nodes([left_path, right_path])
    assert set(scene.get_selection()) == {left_path, right_path}
    scene.select_multiple_nodes([])
    assert scene.get_selection() == []
    try:
        scene.select_node("same")
    except ValueError:
        pass
    else:
        raise AssertionError("Ambiguous short names must be refused")
    scene.set_visibility(right_path, False)
    assert not cmds.getAttr(right_path + ".visibility")
    roots = scene.get_scene_hierarchy()
    assert any(node["path"] == "|av_demo_left" for node in roots)
    selections = []
    callbacks = MayaCallbacks(om, lambda *_: selections.append(scene.get_selection()), lambda *_: None)
    callbacks.start()
    registered = len(callbacks.ids)
    assert registered > 0
    scene.select_node(right_path)
    assert selections and selections[-1] == [right_path]
    callbacks.close()
    callbacks.close()
    assert not callbacks.ids
    before = len(selections)
    scene.select_node(left_path)
    assert len(selections) == before, "Callback was not removed"
    print(json.dumps({
        "host": "Maya", "version": cmds.about(version=True),
        "level": "native-scene-smoke", "status": "passed",
        "checks": ["hierarchy", "duplicate-DAG-names", "selection", "multi-selection",
                   "clear-selection", "visibility", "callback-registration", "callback-removal"],
        "registered_callbacks": registered,
        "webview_rendering": "not-tested", "interactive_demo": "not-tested",
    }, indent=2))
finally:
    maya.standalone.uninitialize()
