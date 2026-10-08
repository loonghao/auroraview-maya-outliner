"""Shared contract behavior; no Maya SDK, Qt or native view is imported."""

from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

contracts = pytest.importorskip("auroraview_dcc_mcp", reason="Run vx just test-contracts <wheel>")

from auroraview_maya_outliner.scene import SceneAPI
from auroraview_maya_outliner.tools import create_tools
from tests.test_scene import Commands


@pytest.fixture
def scene():
    commands = Commands()

    def rename(path, name):
        new_path = path.rsplit("|", 1)[0] + "|" + name
        commands.nodes[new_path] = commands.nodes.pop(path)
        parent = path.rsplit("|", 1)[0]
        children = commands.nodes[parent]["children"]
        children[children.index(path)] = new_path
        return new_path

    commands.rename = Mock(side_effect=rename)
    return SceneAPI(commands)


def test_explicit_tools_share_existing_handlers_and_host_readback(scene):
    with create_tools(scene) as tools:
        descriptors = {tool["name"]: tool for tool in tools.list_tools()}
        assert set(descriptors) == {"scene.snapshot", "scene.rename"}
        assert tools.dcc == "maya"
        assert descriptors["scene.snapshot"]["annotations"]["readOnlyHint"]
        result = tools.call("scene.rename", {"old_name": "|left|same", "new_name": "renamed"})
        scene._cmds.rename.assert_called_once_with("|left|same", "renamed")
        assert result["result"] == {"ok": True, "node": "|left|renamed"}
        assert result["scene"] == tools.call("scene.snapshot")
        assert result["scene"]["hierarchy"][0]["children"][0]["path"] == "|left|renamed"


@pytest.mark.parametrize("params", [
    {"old_name": "|left|same", "new_name": ""},
    {"old_name": "|left|same", "new_name": "|bad"},
    {"old_name": "|left|same", "new_name": "valid", "unexpected": True},
])
def test_invalid_rename_is_refused_before_maya_mutation(scene, params):
    with create_tools(scene) as tools:
        with pytest.raises(contracts.ContractError):
            tools.call("scene.rename", params)
        scene._cmds.rename.assert_not_called()


def test_ui_binding_and_borrowed_session_have_independent_lifetimes(scene):
    routes = {}
    view = SimpleNamespace(bind_call=lambda name, handler: routes.update({name: handler}))
    tools = create_tools(scene)
    session = tools.borrow()
    ui = tools.bind(view)
    snapshot = routes["scene.snapshot"]
    assert snapshot() == session.call("scene.snapshot")
    ui.close()
    with pytest.raises(contracts.ClosedError):
        snapshot()
    assert session.call("scene.snapshot")["hierarchy"]
    tools.close()
    with pytest.raises(contracts.ClosedError):
        session.call("scene.snapshot")


def test_host_subscription_is_removed_when_owner_closes(scene):
    unsubscribe = Mock()
    subscribe = Mock(return_value=unsubscribe)
    tools = create_tools(scene, subscribe=subscribe)
    session = tools.borrow()
    session.subscribe("scene.changed", Mock())
    subscribe.assert_called_once()
    tools.close()
    unsubscribe.assert_called_once_with()


def test_worker_call_is_refused_before_business_handler(scene):
    with create_tools(scene) as tools, ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(tools.call, "scene.rename", {"old_name": "|left|same", "new_name": "after"})
        with pytest.raises(contracts.ThreadError):
            future.result()
        scene._cmds.rename.assert_not_called()
