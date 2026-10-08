# AuroraView Maya Outliner

A runnable tutorial for building a scene tool with Vue inside Maya. The frontend displays the DAG; Python owns Maya commands; AuroraView carries Promise-based calls and events through an embedded QtWebView.

[中文教程](README_zh.md) · [AuroraView](https://github.com/try-auroraview/auroraview) · [Organization website](https://try-auroraview.github.io/) · [Validation](docs/VALIDATION.md) · [Origin and rights](docs/PROVENANCE.md)

[Shared UI and agent tools](docs/SHARED_TOOLS.md) adds an explicit ToolSet factory
and a separate public-wheel Maya standalone consumer gate.

This is the original **Maya Outliner Example**, moved from Long Hao's repository with its history intact. It is separate from the [Maya host adapter](https://github.com/try-auroraview/auroraview-maya).

![Original Maya Outliner preview](docs/preview.png)

*Preview retained from the original project. See the validation record for what has been checked after migration.*

## What you will learn

- Embed a Vue interface in Maya's existing Qt event loop.
- Query full DAG paths, including objects with identical leaf names.
- Select one or several objects, clear selection, and synchronize Maya selections back into Vue.
- Toggle visibility, rename, duplicate, group, delete and reparent through explicit Python methods.
- Load a production frontend without a Vite server, then remove callbacks and dispose of the WebView on close.

## Prerequisites

The maintained tutorial path is **Windows x64, Maya with Python 3, its bundled PySide binding, and WebView2 Runtime**. Maya 2022–2024 use PySide2; Maya 2025–2026 use PySide6. These are code paths, not a claim of interactive acceptance for every version. See [validation](docs/VALIDATION.md).

Use [vx](https://github.com/loonghao/vx) for Node.js, uv and just. The demo installs `auroraview` and `qtpy` into a local directory; it uses Maya's Qt binding rather than installing another one.

## 1. Build the frontend

```powershell
vx git clone https://github.com/try-auroraview/auroraview-maya-outliner.git
cd auroraview-maya-outliner
vx just install
vx just build
```

The build runs TypeScript checks and creates `dist/index.html` plus its assets.

## 2. Prepare Maya's runtime

Change the interpreter path to your installed Maya version:

```powershell
vx just maya-runtime "C:/Program Files/Autodesk/Maya2026/bin/mayapy.exe" ".maya-runtime"
```

This installs into the repository's `.maya-runtime` directory. It does not edit Maya's `userSetup.py` or replace the PySide shipped with Maya. Restart Maya after changing native wheel versions.

## 3. Open inside Maya

In Maya's Script Editor, choose **Python** and run:

```python
import sys
from pathlib import Path

repo = Path(r"C:/path/to/auroraview-maya-outliner")
sys.path.insert(0, str(repo))
sys.path.insert(0, str(repo / ".maya-runtime"))

from auroraview_maya_outliner import main
outliner = main(use_local=True)
```

`use_local=True` requires a built frontend and reports a missing build clearly. The widget serves the files through AuroraView's asset protocol; no HTTP server is needed. Calling `main()` again raises the existing window.

For hot reload, run `vx just dev` in a separate terminal, then use `main(url="http://127.0.0.1:5173")` in a fresh outliner instance.

## 4. Try a small scene

The following adds a group and two objects to the current scene; it does not reset your scene:

```python
import maya.cmds as cmds

root = cmds.group(empty=True, name="av_demo")
cube = cmds.polyCube(name="av_cube")[0]
sphere = cmds.polySphere(name="av_sphere")[0]
cmds.parent([cube, sphere], root)
cmds.select(cube)
```

Select a row in the web outliner and confirm Maya's selection changes. Select the sphere in Maya and confirm the row changes. Ctrl-click selects several rows; Ctrl-click the last selected row clears selection. Use the eye control to hide/show an object. Double-click a label to rename it. Try drag/drop parenting and the context menu on this disposable sample.

## How the bridge works

```text
Vue component -> auroraview.call("api.select_node", params)
              -> SceneAPI.select_node() -> maya.cmds on Maya's main thread

Maya SelectionChanged callback -> QtWebView.emit("selection_changed", payload)
                              -> auroraview.on(...) -> Vue state
```

The Python side binds a small API object:

```python
webview.bind_api(scene_api)
# The api namespace includes get_scene_hierarchy, select_node and set_visibility.
```

The frontend uses the same protocol for queries and mutations:

```typescript
const nodes = await window.auroraview.call('api.get_scene_hierarchy')
await window.auroraview.call('api.select_node', {
  node_name: '|av_demo|av_cube',
})
const unsubscribe = window.auroraview.on('selection_changed', payload => {
  // payload.nodes contains every selected full DAG path, including [].
})
// Call unsubscribe() when the Vue component is unmounted.
```

Full DAG paths are identities; short names are labels. Ambiguous or missing nodes and Maya command failures reject the call. QtWebView owns WebView processing inside Maya's Qt event loop. Scene callbacks coalesce refreshes with a Qt timer rather than taking over the message pump.

## Shared runtime direction

AuroraView focuses on modern Web interfaces, rendering and native host docking. The planned thin integration will reuse DCC-MCP Core's existing server/MCP transport, tool and Skill registration, host execution bridge, thread scheduling and lifecycle. DCC-MCP keeps those responsibilities; it does not become a frontend framework.

The intended ownership rule is to attach to an existing host service when available. A panel releases its own subscriptions and tasks on close, and shuts down a service only when it owns that service. Page actions and explicitly registered agent tools should call the same host business capabilities.

This shared runtime integration is **planned, not delivered by this demo**. The current tutorial uses a Maya-parented Qt dialog and its own scene callbacks; native Maya docking and DCC-MCP service attachment are not implemented or certified here. It does not define a new Core API or automatically expose the interface as agent tools.

## Close and verify cleanup

```python
outliner.close()
assert not outliner._callbacks.ids
outliner = main(use_local=True)
```

Closing with the window's close button uses the same cleanup path: stop the refresh timer, unregister Maya callbacks, destroy the WebView, and release the instance registry. The Vue composable also removes its event subscriptions on unmount.

## Tests and source archive

```powershell
vx just check
vx just maya-smoke "C:/Program Files/Autodesk/Maya2026/bin/mayapy.exe"
vx just package 0.1.0-test
```

`check` builds the frontend and runs scene/config/package contract tests outside Maya. `maya-smoke` starts a separate Maya standalone process and checks real DAG queries, duplicate names, selection, visibility and callback removal. It does not certify WebView rendering or an interactive Maya session.

The source demo archive in `dist/` contains the built frontend, frontend source, Python code, recipes, tests, tutorials and provenance. After extraction, use its `maya-outliner` directory as `repo` in the launch example. The included `dist/` needs rebuilding only when you change the frontend. Install the runtime separately with the included `maya-runtime` recipe as above. Older installers and development scripts remain as legacy project material; the steps above are the maintained tutorial workflow.

## Troubleshooting

| Symptom | Next step |
| --- | --- |
| Missing `dist/index.html` | Run `vx just install` and `vx just build`. |
| `No module named auroraview` or `qtpy` | Run the runtime recipe with the same Maya interpreter, then add `.maya-runtime` to `sys.path`. |
| Maya main window unavailable | Run `main()` in interactive Maya after startup; mayapy has no main window. |
| Frontend shown in a browser but no Maya data | Open it through the Maya launcher; a browser tab has no Maya bridge. |
| Missing/ambiguous node error | Refresh after edits and use full DAG paths. |
| Native wheel or WebView initialization failure | Check Maya's Python ABI, Windows x64 and WebView2 Runtime; capture the Script Editor traceback. |

The project is originally by **Long Hao (loonghao)**. The source repository has no LICENSE file at the preserved migration commit; see [provenance](docs/PROVENANCE.md). AuroraView's own MIT license does not automatically license this separate demo.
