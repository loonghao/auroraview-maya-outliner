"""Public facade over controlled Core/Qt/Maya boundaries; no native host proof."""

import sys
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

contracts = pytest.importorskip("auroraview_dcc_mcp", reason="Run vx just test-contracts <wheel>")

from auroraview_maya_outliner import OutlinerRuntime, maya_outliner
from tests.test_panel import host
from tests.test_scene import Commands


@pytest.fixture
def runtime(host, monkeypatch):
    class Server:
        """Controlled public Core boundary, including retained unloaded metadata."""

        def __init__(self):
            self.skills = {"unrelated": object()}
            self.loaded = {"unrelated"}
            self.loads = []
            self.unload_skill = Mock(side_effect=self._unload)
            self.registry = SimpleNamespace(get_action=lambda _name: None)
            self.register_quit_hook = Mock()
            self.unregister_quit_hook = Mock()
            self.stop = Mock()
            self.is_running = True

        def get_skill(self, name):
            return self.skills.get(name)

        get_skill_info = get_skill

        def load_skill_object(self, skill):
            self.skills[skill.name] = skill
            self.loaded.add(skill.name)
            self.loads.append(skill)
            return True

        def _unload(self, name):
            self.loaded.discard(name)
            return True

        def is_skill_loaded(self, name):
            return name in self.loaded

    # Exercise the actual published AgentBinding; only its Core host boundary
    # is controlled here. Core native catalog behavior has a separate receipt.
    monkeypatch.setitem(sys.modules, "dcc_mcp_core", SimpleNamespace(
        SkillMetadata=SimpleNamespace, ToolDeclaration=SimpleNamespace,
    ))
    monkeypatch.setitem(sys.modules, "dcc_mcp_core.server_base", SimpleNamespace(DccServerBase=Server))

    callbacks = []

    class Callbacks:
        def __init__(self, _api, on_selection, on_scene):
            self.ids = []
            self.on_selection, self.on_scene = on_selection, on_scene
            self.close = Mock(side_effect=self.ids.clear)
            callbacks.append(self)

        def start(self):
            self.ids[:] = [1, 2, 3]

    monkeypatch.setattr(maya_outliner, "MayaCallbacks", Callbacks)
    monkeypatch.setattr(sys.modules["qtpy.QtCore"], "QTimer",
                        lambda *_args: Mock(isActive=Mock(return_value=False)))
    commands = Commands()

    def rename(path, name):
        new_path = path.rsplit("|", 1)[0] + "|" + name
        commands.nodes[new_path] = commands.nodes.pop(path)
        parent = path.rsplit("|", 1)[0]
        children = commands.nodes[parent]["children"]
        children[children.index(path)] = new_path
        return new_path

    commands.rename = Mock(side_effect=rename)
    commands.ls = Mock(wraps=commands.ls)
    server = Server()
    owner = OutlinerRuntime(server, commands=commands, dockable=True)
    return SimpleNamespace(owner=owner, server=server, commands=commands, callbacks=callbacks)


def test_same_owner_and_agent_survive_view_close_and_reopen(runtime):
    owner, server, commands = runtime.owner, runtime.server, runtime.commands
    first = owner.open(use_local=True)
    tools, agent = owner.tools, owner.agent
    old_view, old_timer, old_routes = first.webview, first._scene_timer, first.webview.routes
    old_view.emit = Mock()
    assert owner.attach() is agent
    first.dialog.raise_ = Mock()
    assert owner.open(use_local=True) is first
    first.dialog.raise_.assert_called_once_with()
    owner.close_view()
    assert owner.panel is None and not owner.closed and not tools.closed and not agent.closed
    assert runtime.callbacks[0].ids == []
    runtime.callbacks[0].close.assert_called_once_with()
    assert agent.call("scene.snapshot")["hierarchy"]

    second = owner.open(use_local=True)
    second.webview.emit = Mock()
    assert second is not first and second.api is first.api is owner.scene
    assert owner.tools is tools and owner.agent is agent and len(server.loads) == 1
    assert set(agent.method_names.values()) == {"maya-outliner__scene_snapshot", "maya-outliner__scene_rename"}
    assert runtime.callbacks[1].ids == [1, 2, 3]
    assert all(len(handlers) == 1 for handlers in second.webview.routes.values())
    assert second.webview.routes["scene.snapshot"][0]() == tools.call("scene.snapshot")

    # Every old route rejects before a scene read or mutation, even while the
    # retained owner and a new view are live.
    commands.ls.reset_mock()
    for name, params in (
        ("scene.snapshot", {}),
        ("scene.rename", {"old_name": "|left|same", "new_name": "stale"}),
        ("api.rename_node", {"old_name": "|left|same", "new_name": "stale"}),
        ("api.get_scene_hierarchy", {}),
        ("api.select_node", {"node_name": "|left|same"}),
        ("api.resize_window", {"width": 640, "height": 480}),
        ("api.get_window_size", {}),
        ("api.frontend_ready", {}),
    ):
        with pytest.raises(contracts.ClosedError):
            old_routes[name][0](**params)
    commands.ls.assert_not_called()
    commands.rename.assert_not_called()

    result = agent.call("scene.rename", {"old_name": "|left|same", "new_name": "current"})
    assert result["result"]["node"] == "|left|current"
    commands.rename.assert_called_once_with("|left|same", "current")
    second._scene_timer.start.assert_called_once_with()
    old_timer.start.assert_not_called()
    runtime.callbacks[0].on_scene()
    runtime.callbacks[0].on_selection()
    old_view.emit.assert_not_called()
    second.send_scene_update()
    assert second.webview.emit.call_args_list[0].args[0] == "scene_updated"
    owner.close()
    assert owner.closed and tools.closed and owner.agent is None and owner.panel is None
    assert runtime.callbacks[1].ids == []
    server.stop.assert_not_called()
    assert server.is_running and server.is_skill_loaded("unrelated")
    with pytest.raises(contracts.ClosedError):
        agent.call("scene.snapshot")
    assert server.get_skill("maya-outliner") is not None  # Published catalog limitation.


def test_pending_view_cleanup_blocks_reopen_but_preserves_host_tools(runtime):
    owner = runtime.owner
    first = owner.open(use_local=True)
    agent, tools = owner.agent, owner.tools
    callbacks = runtime.callbacks[0]
    callbacks.close.side_effect = [RuntimeError("callback busy"), None]
    with pytest.raises(RuntimeError, match="callback busy"):
        owner.close_view()
    assert owner.panel is first and owner.agent is agent and owner.tools is tools
    assert agent.call("scene.snapshot")["hierarchy"]
    with pytest.raises(RuntimeError, match="cleanup is pending"):
        owner.open(use_local=True)
    callbacks.close.side_effect = callbacks.ids.clear
    owner.close_view()
    owner.open(use_local=True)
    assert len(runtime.server.loads) == 1 and callbacks.close.call_count == 2
    owner.close()


@pytest.mark.parametrize("failure", ["construct", "load"])
def test_partial_view_startup_keeps_original_agent_for_next_open(runtime, monkeypatch, failure):
    owner = runtime.owner
    native = sys.modules["auroraview"]
    original = native.QtWebView
    created = []

    def create(**options):
        if not created and failure == "construct":
            created.append(None)
            raise RuntimeError("view startup failed")
        view = original(**options)
        if not created:
            view.load_file.side_effect = RuntimeError("view startup failed")
        created.append(view)
        return view

    monkeypatch.setattr(native, "QtWebView", create)
    with pytest.raises(RuntimeError, match="view startup failed"):
        owner.open(use_local=True)
    agent, tools = owner.agent, owner.tools
    assert owner.panel is None and not tools.closed and not agent.closed
    assert agent.call("scene.snapshot")["hierarchy"]
    owner.open(use_local=True)
    assert len(runtime.server.loads) == 1 and owner.agent is agent and owner.tools is tools
    if created[0] is not None:
        with pytest.raises(contracts.ClosedError):
            created[0].routes["scene.snapshot"][0]()
    owner.close()


def test_final_cleanup_failure_retains_agent_for_retry_and_cannot_reopen(runtime):
    owner, server = runtime.owner, runtime.server
    owner.open(use_local=True)
    tools, agent = owner.tools, owner.agent
    session = tools.borrow()
    server.unload_skill.side_effect = [False, True]
    with pytest.raises(contracts.CleanupError):
        owner.close()
    assert not owner.closed and owner.panel is None
    assert owner.tools is tools and owner.agent is agent and tools.closed and agent.closed
    with pytest.raises(RuntimeError, match="closing or closed"):
        owner.open(use_local=True)
    for lease in (session, agent):
        with pytest.raises(contracts.ClosedError):
            lease.call("scene.snapshot")
    owner.close()
    owner.close()
    assert owner.closed and owner.agent is None and server.unload_skill.call_count == 2
    server.stop.assert_not_called()
    assert server.is_running and server.is_skill_loaded("unrelated")


def test_runtime_rejects_worker_calls_before_attachment_or_view(runtime):
    owner = runtime.owner
    with ThreadPoolExecutor(max_workers=1) as executor:
        for action in (owner.open, owner.close_view, owner.close):
            with pytest.raises(RuntimeError, match="main thread"):
                executor.submit(action).result()
    assert owner.tools is None and owner.agent is None and owner.panel is None
    assert not runtime.server.loads
    runtime.commands.ls.assert_not_called()


def test_failed_attach_retains_tool_owner_for_cleanup_without_second_registration(runtime):
    owner, server = runtime.owner, runtime.server
    original = server.load_skill_object

    def partial_load(skill):
        original(skill)
        raise RuntimeError("partial Core load")

    server.load_skill_object = Mock(side_effect=partial_load)
    server.unload_skill.side_effect = [False, True]
    with pytest.raises(contracts.CleanupError):
        owner.attach()
    tools = owner.tools
    assert tools is not None and owner.agent is None and not owner.closed
    with pytest.raises(RuntimeError, match="closing or closed"):
        owner.open(use_local=True)
    assert server.load_skill_object.call_count == 1 and owner.panel is None
    owner.close()
    assert owner.closed and owner.tools is tools and tools.closed
    assert server.unload_skill.call_count == 2
    assert server.is_running and server.is_skill_loaded("unrelated")
    server.stop.assert_not_called()
