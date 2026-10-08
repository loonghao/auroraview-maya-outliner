"""Real Maya standalone consumption of a verified public contract wheel."""

import argparse
import importlib.metadata
import importlib.util
import json
import os
import socket
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

if __package__:
    from .contract_runtime import CORE_VERSION, inside, verify_runtime
else:
    from contract_runtime import CORE_VERSION, inside, verify_runtime


def rpc(url, pump, method, params=None):
    def post():
        request = Request(
            url,
            data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}).encode(),
            headers={"Accept": "application/json, text/event-stream", "Content-Type": "application/json"},
        )
        with urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8")
            if response.headers.get("Content-Type", "").startswith("text/event-stream"):
                body = next(line[6:] for line in body.splitlines() if line.startswith("data: "))
            return json.loads(body)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(post)
        deadline = time.monotonic() + 12
        while not future.done() and time.monotonic() < deadline:
            pump.drain_queue(8)
            time.sleep(0.002)
        return future.result(timeout=1)


def result_value(response):
    assert "error" not in response, response
    result = response["result"]
    assert not result.get("isError", False), result
    if "structuredContent" in result:
        return result["structuredContent"]
    return json.loads(result["content"][0]["text"])


def paths(snapshot):
    def walk(nodes):
        for node in nodes:
            yield node["path"]
            yield from walk(node["children"])
    return set(walk(snapshot["hierarchy"]))


def endpoint_closed(url):
    target = urlparse(url)
    with socket.socket() as connection:
        connection.settimeout(0.2)
        return connection.connect_ex((target.hostname, target.port)) != 0


def run_gate(runtime):
    runtime = Path(runtime).resolve()
    receipt = verify_runtime(runtime)
    sys.path.insert(0, str(runtime))
    # Only the tutorial business package is read from this checkout.
    sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
    import auroraview_dcc_mcp
    import dcc_mcp_core
    from auroraview_dcc_mcp import ClosedError
    from dcc_mcp_core import (
        BridgeExecution, DccServerOptions, ExecutionOptions, GatewayOptions,
        HostExecutionBridge, HostUiDispatcherBase, ObservabilityOptions,
    )
    from dcc_mcp_core.server_base import DccServerBase

    for module in (auroraview_dcc_mcp, dcc_mcp_core):
        assert inside(module.__file__, runtime), "Runtime import escaped isolated target: " + module.__file__
    assert importlib.metadata.version("dcc-mcp-core") == CORE_VERSION
    assert "auroraview" not in sys.modules and "qtpy" not in sys.modules

    import maya.standalone
    maya.standalone.initialize(name="python")
    with ExitStack() as cleanup:
        cleanup.callback(maya.standalone.uninitialize)
        temporary = cleanup.enter_context(tempfile.TemporaryDirectory(prefix="maya-contract-"))
        import maya.cmds as cmds
        import maya.api.OpenMaya as om
        from auroraview_maya_outliner.scene import MayaCallbacks, SceneAPI
        from auroraview_maya_outliner.tools import create_tools

        class Pump(HostUiDispatcherBase):
            def poke_host_pump(self):
                pass

        main_thread = threading.get_ident()
        threads, callback_groups, events = [], [], []
        scene = SceneAPI()

        def observe(handler):
            def call(*args, **kwargs):
                threads.append(threading.get_ident())
                return handler(*args, **kwargs)
            return call

        for name in ("rename_node", "get_scene_hierarchy", "get_selection"):
            setattr(scene, name, observe(getattr(scene, name)))

        def subscribe(event, callback):
            if event != "scene.changed":
                raise ValueError("Unknown scene event: " + event)
            callbacks = MayaCallbacks(om, lambda *_: callback(), lambda *_: callback())
            callbacks.start()
            callback_groups.append(callbacks)
            return callbacks.close

        pump = Pump()
        cleanup.callback(pump.shutdown)
        registry = Path(temporary) / "registry"
        server = DccServerBase(DccServerOptions(
            dcc_name="maya", builtin_skills_dir=Path(temporary) / "skills", port=0,
            gateway=GatewayOptions(port=0, registry_dir=str(registry), enable_failover=False),
            observability=ObservabilityOptions(
                enable_file_logging=False, enable_job_persistence=False, enable_telemetry=False,
            ),
            execution=ExecutionOptions(mode=BridgeExecution(HostExecutionBridge(dispatcher=pump))),
        ))
        cleanup.callback(server.stop)
        handle = server.start(install_atexit_hook=False)
        url = handle.mcp_url()
        owner = create_tools(scene, subscribe=subscribe)
        cleanup.callback(owner.close)
        session = owner.borrow()
        session.subscribe("scene.changed", lambda: events.append(threading.get_ident()))
        callback_count = sum(len(group.ids) for group in callback_groups)
        assert callback_count > 0
        binding = owner.attach(server)
        tool_names = dict(binding.method_names)
        skill = server.get_skill(binding.skill_name)
        script = Path(skill.tools[0].source_file)
        spec = importlib.util.spec_from_file_location("stale_maya_contract", str(script))
        stale = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(stale)

        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.group(empty=True, name="av_contract_root")
        cmds.createNode("transform", name="before", parent="av_contract_root")
        original, renamed = "|av_contract_root|before", "|av_contract_root|after"
        scene.select_node(original)
        cmds.flushUndo()
        initialized = rpc(url, pump, "initialize", {
            "protocolVersion": "2025-03-26", "capabilities": {},
            "clientInfo": {"name": "maya-outliner-consumer", "version": "1.0.0"},
        })
        assert initialized["result"]["serverInfo"]
        listed = rpc(url, pump, "tools/list")["result"]["tools"]
        assert set(tool_names.values()).issubset({tool["name"] for tool in listed})

        def call(method, params=None):
            return result_value(rpc(url, pump, "tools/call", {
                "name": tool_names[method], "arguments": {"params": params or {}},
            }))

        before = call("scene.snapshot")
        changed = call("scene.rename", {"old_name": original, "new_name": "after"})
        assert changed["result"]["ok"]
        assert renamed in paths(changed["scene"]) and original not in paths(changed["scene"])
        assert cmds.objExists(renamed) and not cmds.objExists(original)
        assert call("scene.snapshot") == changed["scene"]
        cmds.undo()
        restored = call("scene.snapshot")
        assert restored == before
        assert cmds.objExists(original) and not cmds.objExists(renamed)
        assert threads and set(threads) == {main_thread}
        assert events and set(events) == {main_thread}
        binding.close()
        assert not script.exists() and not server.is_skill_loaded(binding.skill_name)
        assert server.get_skill(binding.skill_name) is not None  # Core retains catalog metadata.
        try:
            stale.main(params={})
        except ClosedError:
            pass
        else:
            raise AssertionError("Unloaded tool token was still callable")
        listed_after = rpc(url, pump, "tools/list")["result"]["tools"]
        assert not set(tool_names.values()).intersection(tool["name"] for tool in listed_after)
        assert server.is_running
        assert session.call("scene.snapshot") == restored
        owner.close()
        assert all(not group.ids for group in callback_groups)
        before_events = len(events)
        scene.select_multiple_nodes([])
        assert len(events) == before_events
        server.stop()
        pump.shutdown()
        deadline = time.monotonic() + 5
        while not endpoint_closed(url) and time.monotonic() < deadline:
            time.sleep(0.05)
        assert endpoint_closed(url) and not server.is_running
        registry_file = registry / "services.json"
        if registry_file.exists():
            rows = json.loads(registry_file.read_text(encoding="utf-8"))
            rows = rows if isinstance(rows, list) else rows.get("services", [])
            assert not any(row.get("dcc_type") == "maya" for row in rows)
        return {
            "status": "passed", "level": "standalone-maya-public-contract-consumer",
            "host": "Maya", "maya_version": cmds.about(version=True),
            "python": sys.version, "pid": os.getpid(), "main_thread": main_thread,
            "artifact": receipt, "contract_version": importlib.metadata.version("auroraview-dcc-mcp"),
            "core_version": CORE_VERSION,
            "imports": {"contract": auroraview_dcc_mcp.__file__, "core": dcc_mcp_core.__file__},
            "mcp_url": url, "tools": tool_names, "registered_callbacks": callback_count,
            "checks": ["public-wheel-hash", "isolated-imports", "http-initialize", "tools-list",
                       "http-rename", "host-scene-readback", "main-thread-dispatch", "undo-readback",
                       "binding-unload", "stale-token-refused", "borrowed-server-preserved",
                       "callback-cleanup", "endpoint-and-registry-cleanup"],
            "before": before, "after": changed, "undo": restored,
            "interactive_webview": "not-tested", "docking": "not-tested",
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    result = run_gate(args.runtime)
    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
