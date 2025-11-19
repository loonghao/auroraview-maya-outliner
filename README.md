# Maya Outliner - AuroraView Example

[![Vue 3](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![AuroraView](https://img.shields.io/badge/AuroraView-Rust-orange?logo=rust&logoColor=white)](../../README.md)

[中文文档](./README_zh.md) | [Quick Start](./QUICKSTART.md) | [Local Development](./LOCAL_DEVELOPMENT.md)

A modern, web-based Maya Outliner built with **AuroraView**, **Vue 3**, and **TypeScript**. This example demonstrates how to create high-performance DCC tools with modern web technologies embedded directly in Maya.

## ✨ Features

- 🌳 **Hierarchical Scene Tree** - Display Maya's scene hierarchy with expandable nodes
- 🎯 **Real-time Selection Sync** - Bidirectional selection synchronization between Maya and UI
- 👁️ **Visibility Toggle** - Show/hide objects directly from the outliner
- 🔍 **Search & Filter** - Quickly find nodes by name
- ⚡ **High Performance** - Handle 10,000+ nodes smoothly with AuroraView's optimized IPC
- 🎨 **Modern UI** - Clean, dark-themed interface built with Vue 3
- 🔄 **Live Updates** - Automatic UI updates when scene changes

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│           Maya (Python)                 │
│  ┌───────────────────────────────────┐  │
│  │   maya_outliner.py                │  │
│  │   - Scene hierarchy queries       │  │
│  │   - Selection management          │  │
│  │   - Visibility control            │  │
│  │   - Maya callbacks                │  │
│  └───────────┬───────────────────────┘  │
│              │ AuroraView IPC            │
│              │ (Thread-based, <1μs)      │
│  ┌───────────▼───────────────────────┐  │
│  │   WebView (Embedded)              │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │  Vue 3 Frontend             │  │  │
│  │  │  - OutlinerTree.vue         │  │  │
│  │  │  - TreeNode.vue             │  │  │
│  │  │  - useMayaIPC composable    │  │  │
│  │  └─────────────────────────────┘  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## 📦 Installation

### Prerequisites

- **Maya 2020+** (with Python 3.7+)
- **Node.js 18+** and npm
- **AuroraView** installed in Maya's Python environment

### Install AuroraView

**Option A: Qt Backend (Recommended)**
```bash
# Install with Qt support for better Maya integration
mayapy -m pip install auroraview[qt]
```
- ✅ Non-blocking by default
- ✅ Better integration with Maya's UI
- ✅ Seamless window management

**Option B: Native Backend (Fallback)**
```bash
# Install without Qt dependencies
mayapy -m pip install auroraview
```
- ✅ Works without Qt
- ✅ Uses `show_async()` for non-blocking
- ⚠️ Standalone window

**Local Development:**
```bash
cd /path/to/dcc_webview
mayapy -m pip install -e python/[qt]  # With Qt
# or
mayapy -m pip install -e python/      # Without Qt
```

### Install Frontend Dependencies

```bash
cd examples/maya-outliner
npm install
```

## 🚀 Usage

### Quick Start with Justfile (Recommended)

This project includes a `justfile` for easy Maya setup and launch.

**Prerequisites:**
- Install [just](https://github.com/casey/just) command runner
- Install AuroraView: `mayapy -m pip install auroraview`
- Install frontend dependencies: `npm install`

**Launch Maya with AuroraView Outliner:**

```bash
# For Maya 2022
just maya-2022

# For Maya 2024
just maya-2024

# For Maya 2025
just maya-2025
```

This will:
1. ✅ Copy `userSetup.py` to Maya's scripts folder with correct paths
2. ✅ Launch Maya
3. ✅ Create "AuroraView" shelf with "Outliner" button on startup

**Check your setup:**
```bash
just info
```

This shows:
- Project paths
- Maya installation status
- UserSetup installation status

**Local Development Mode:**

If you're developing AuroraView locally, use the `-local` suffix:

```bash
just maya-2024-local  # Use local AuroraView from custom path
```

See [LOCAL_DEVELOPMENT.md](./LOCAL_DEVELOPMENT.md) for details.

**Other useful commands:**
```bash
just install          # Install npm dependencies
just dev              # Start Vite dev server
just build            # Build for production
just clean-maya 2024  # Remove userSetup.py from Maya 2024
just clean-all-maya   # Remove userSetup.py from all Maya versions
```

📖 See [QUICKSTART.md](./QUICKSTART.md) for more details

### Quick Debug Workflow (For Testing)

**Using Just command:**
```bash
just maya-debug
```

This will:
1. Kill all Maya processes
2. Rebuild Rust core
3. Set PYTHONPATH
4. Launch Maya 2024

**Using batch script (Recommended):**
```bash
cd examples/maya-outliner
launch_maya_debug.bat
```

This script will:
- Kill all Maya processes
- Rebuild Rust core
- Set PYTHONPATH
- Launch Maya with AuroraView available

**Verify PYTHONPATH in Maya:**
After Maya starts, run this in Script Editor:
```python
exec(open(r'C:\path\to\examples\maya-outliner\test_pythonpath.py').read())
```

You should see:
```
✅ SUCCESS: auroraview imported successfully!
✅ SUCCESS: WebView class imported!
```

**Auto-load on Maya startup:**
Copy `userSetup.py` to Maya's scripts folder:
```bash
# Windows
copy userSetup.py "C:\Users\<username>\Documents\maya\2024\scripts\"
```

Then restart Maya - you'll see an "Outliner" button on the AuroraView shelf!

### Development Mode

1. **Start the Vite dev server:**

```bash
npm run dev
```

This will start the development server at `http://localhost:5173` with hot-reload.

2. **Run in Maya:**

Open Maya's Script Editor and run:

```python
import sys
sys.path.append(r"C:\path\to\dcc_webview\examples\maya-outliner")

from maya_integration import maya_outliner
maya_outliner.main()
```

The outliner window will open and connect to the Vite dev server automatically.

### Production Mode

1. **Build the frontend:**

```bash
npm run build
```

2. **Serve the built files:**

```bash
npm run preview
```

3. **Run in Maya** (same as development mode)

## 🎯 Features Demonstration

## 🪟 Windows WebView2 Backend (Experimental)

AuroraView provides a Windows-native WebView2 backend designed for DCC hosts (Qt event loop). Build the core with the feature enabled:

```bash
# Build wheel with WebView2 (Windows only)
# Example with maturin (inside repo root)
set RUSTFLAGS=
set CARGO_BUILD_TARGET=
python -m pip uninstall -y auroraview || echo .
maturin develop --release --features win-webview2
```

Then inside Maya's Script Editor (Python):

```python
import sys
sys.path.append(r"C:\path\to\dcc_webview\examples\maya-outliner")
from maya_integration.launch_webview2 import launch
h = launch("http://localhost:5173", 1000, 700)
print("WebView2 handle:", h)
```

If you see an error about the feature not enabled, rebuild AuroraView with `--features win-webview2`.




### Scene Hierarchy

The outliner displays your Maya scene as a hierarchical tree:

- **Transform nodes** 📁
- **Mesh nodes** 🔷
- **Camera nodes** 📷
- **Light nodes** 💡
- **Joint nodes** 🦴
- **Locator nodes** 📍

### Selection Synchronization

- **Click a node** in the outliner → Maya selects it
- **Select in Maya** → Outliner highlights it
- **Real-time updates** with <1ms latency

### Visibility Control

- Click the 👁️ icon to toggle visibility
- Changes reflect immediately in Maya viewport
- Supports hierarchical visibility

### Search & Filter

- Type in the search box to filter nodes
- Matches node names (case-insensitive)
- Shows matching nodes and their parents

## 📊 Performance Benchmarks

Tested on Windows 10, Intel i7-9700K, 32GB RAM:

| Nodes | Load Time | Selection Latency | Memory Usage |
|-------|-----------|-------------------|--------------|
| 100   | <10ms     | <1ms              | ~15MB        |
| 1,000 | ~50ms     | <1ms              | ~25MB        |
| 10,000| ~300ms    | <2ms              | ~80MB        |

**Why so fast?**

- **Thread-based IPC** instead of HTTP/WebSocket
- **Crossbeam channels** for lock-free communication
- **Message batching** (16ms window, ~60 FPS)
- **Efficient Vue 3 rendering** with virtual DOM
- **EventTimer** for automatic event processing at 60 FPS

## 🔄 Event Processing

This example uses AuroraView's modern Qt integration instead of manually creating an `EventTimer`.

- The `QtWebView` widget embeds the core WebView backend.
- The `AuroraView` facade keeps the IPC/event loop alive for you.
- You do not need to create or manage an `EventTimer` in your own code for this outliner.

If you are interested in the lower-level `WebView` + `EventTimer` APIs, please refer to the main AuroraView README.

## 🛠️ Development

### Project Structure

```
maya-outliner/
├── src/
│   ├── components/
│   │   ├── OutlinerTree.vue    # Main tree component
│   │   └── TreeNode.vue         # Individual node component
│   ├── composables/
│   │   └── useMayaIPC.ts        # IPC communication layer
│   ├── types.ts                 # TypeScript type definitions
│   ├── App.vue                  # Root component
│   ├── main.ts                  # Entry point
│   └── style.css                # Global styles
├── maya_integration/
│   ├── maya_outliner.py         # Maya backend (AuroraView + QtWebView)
│   └── __init__.py
├── package.json
├── vite.config.ts
├── tsconfig.json
└── README.md
```

### Adding New Features

**1. Add a new API method (recommended):**

Backend (`maya_outliner.py`):
```python
class MayaOutlinerAPI:
    ...

    def frame_node(self, node_name: str) -> dict[str, Any]:
        """Frame a node in Maya's viewport."""
        cmds.viewFit(node_name)
        return {"ok": True, "message": f"Framed: {node_name}"}
```

Frontend (`useMayaIPC.ts`):
```typescript
const frameNode = (nodeName: string) =>
  callAPI<{ ok: boolean; message: string }>('frame_node', { node_name: nodeName })
```

Then call it from your component:
```typescript
await frameNode('pCube1')
```

#### Parameter encoding rules for auroraview.call / callAPI

- JavaScript calls use `window.auroraview.call(method, params)` (or `callAPI` as a helper).
- The payload is encoded using a `params` field:
  - If you call `callAPI('refresh')` **without** a second argument, no `params` key is sent and the bound Python function is invoked with **no arguments** (use this for zero-parameter methods like `API.get_scene_hierarchy(self)`).
  - If you pass an object (e.g. `{ node_name: 'pCube1' }`), it becomes keyword arguments on the Python side (`def frame_node(self, node_name: str)`).
  - If you pass an array (e.g. `[x, y]`), it becomes positional arguments (`def move(self, x, y)`).
  - If you explicitly pass `null`, Python receives a single argument `None` (this is different from omitting the parameter entirely).


**1.1 (optional) Add a new push event from Maya:**

Backend (`maya_outliner.py`):
```python
self.webview.emit("my_event", {"foo": "bar"})
```

Frontend (`useMayaIPC.ts`):
```typescript
onMayaEvent('my_event', (payload) => {
  console.log('Received from Maya', payload)
})
```

**2. Add a new UI component:**

Create `src/components/MyComponent.vue` and import it in `App.vue`.

**3. Add new node properties:**

Update `MayaNode` interface in `src/types.ts` and modify `get_scene_hierarchy()` in `maya_outliner.py`.

## 🐛 Troubleshooting

### Common Issues

**Blank WebView / Cannot read data:**
- Ensure the dev server is running (npm run dev) or use a packaged build (npm run build && npm run preview)

**Module not found:**
```bash
npm install  # Install frontend dependencies
mayapy -m pip install auroraview  # Install AuroraView
```

**Vite server not running:**
```bash
npm run dev  # Start development server
```

## 📚 Learn More

- [AuroraView Documentation](../../README.md)
- [Vue 3 Documentation](https://vuejs.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Maya Python API](https://help.autodesk.com/view/MAYAUL/2024/ENU/?guid=Maya_SDK_py_ref_index_html)

## 📄 License

This example is part of the AuroraView project and follows the same license.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

**Built with ❤️ using AuroraView**

