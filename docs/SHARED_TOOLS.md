# Share explicit Maya scene tools

`auroraview_maya_outliner.tools.create_tools` declares two capabilities over the
existing `SceneAPI`: `scene.snapshot` and `scene.rename`. Rename invokes
`SceneAPI.rename_node` and returns its result together with hierarchy and
selection read back from Maya. The factory contains no second scene model.

The independent `auroraview-dcc-mcp` preview package supplies `Tool` and
`ToolSet`. AuroraView owns the view and page bridge; Maya owns scene operations;
DCC-MCP Core owns MCP and host execution. Registration is explicit.

## Use the same owner in a panel and an agent service

Create the owner on Maya's main thread. Supply the existing SceneAPI, view and
Core server from the host integration:

```python
from auroraview_maya_outliner.tools import create_tools

tools = create_tools(scene_api, subscribe=host_subscribe)
ui = tools.bind(webview)
agent = tools.attach(existing_core_server)

# Frontend: window.auroraview.call('scene.rename', {
#   old_name: '|group|before', new_name: 'after'
# })
# MCP name: agent.method_names['scene.rename']
# MCP arguments: {"params": {"old_name": "|group|before", "new_name": "after"}}

agent.close()  # unload these tools; the borrowed server remains running
ui.close()     # revoke this panel's routes
tools.close()  # close remaining consumers and their subscriptions
```

`host_subscribe(event, callback)` is optional and must return an unsubscribe
callable. The host owns this event source. Both the view's call dispatcher and
Core's execution bridge must dispatch to the thread that created the owner.
The factory neither starts nor stops a service or dispatcher. The existing
tutorial's `api.*` UI routes remain available; adopting `scene.*` is explicit.

## Standalone Maya consumer gate

The gate creates its own disposable scene and Core service in an isolated
`mayapy` process. It opens no interactive Maya window. It consumes only a wheel
downloaded from a public HTTPS URL and verified against a supplied release
SHA256. Core is pinned to `0.20.41`.

After the preview artifact is published, supply its **direct wheel URL** and
**64-character SHA256**, taken from the published `SHA256SUMS`:

```powershell
vx just maya-contract-runtime "C:/Program Files/Autodesk/Maya2026/bin/mayapy.exe" ".maya-contract-runtime" "<public-wheel-url>" "<release-sha256>"
vx just maya-contract "C:/Program Files/Autodesk/Maya2026/bin/mayapy.exe" ".maya-contract-runtime"
```

Use an empty runtime directory. Preparation downloads and verifies the wheel
before invoking `vx uv pip install` with the wheel's `[core]` extra and the
exact Core pin. It retains the original wheel and artifact receipt. The
launcher verifies that receipt again, disables user startup and `PYTHONPATH`,
then starts the supplied Maya interpreter. The consumer asserts that both
contract and Core modules come from this isolated runtime. Only the tutorial's
business package is imported from the checkout.

The gate performs actual HTTP/MCP initialize, discovery and calls. HTTP runs
on a client worker while Maya's main thread drains Core's dispatcher. A rename
must produce the expected full DAG path and host readback; Maya Undo must
restore the original snapshot. It then unloads the binding, refuses a stale
tool token, confirms that the borrowed service is still running, removes every
Maya callback, stops its owned service and verifies endpoint and registry
cleanup. Core retains unloaded catalog metadata; the gate checks tool removal
from `tools/list` rather than claiming catalog deletion.

The JSON receipt defaults to `.build/maya-contract-acceptance.json`. It records
artifact URL/hash, package and Core versions, import paths, Maya/Python/PID and
thread identity, MCP tool names, before/after/Undo snapshots and cleanup checks.
This gate does not establish interactive WebView rendering, docking, input or
DPI behavior.

## Preparation tests

```powershell
vx just test
vx just test-contracts "<contract-wheel-path>"
```

Ordinary tests validate artifact checks and launcher isolation without Maya.
The second recipe tests the factory against the supplied installed wheel;
using a local wheel here is development evidence only. The original
`vx just maya-smoke "<mayapy>"` eight-check scene/callback gate is unchanged.

Public-wheel Maya consumption has not yet been recorded. See
[validation](VALIDATION.md) for the evidence gates.
