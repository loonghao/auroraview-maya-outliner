# Quick Start Guide

## 🚀 3-Minute Setup with Justfile

### Prerequisites

1. **Install just command runner:**
   - Windows: `scoop install just` or `choco install just`
   - macOS: `brew install just`
   - Linux: See [just installation guide](https://github.com/casey/just#installation)

2. **Install AuroraView:**
   ```bash
   mayapy -m pip install auroraview
   ```

3. **Install frontend dependencies:**
   ```bash
   npm install
   ```

### Quick Launch

**Step 1: Check your setup**
```bash
just info
```

This shows which Maya versions are installed and ready to use.

**Step 2: Launch Maya**
```bash
# Choose your Maya version
just maya-2022
just maya-2024
just maya-2025
```

**Step 3: Use the Outliner**
- Maya will start automatically
- Look for the "AuroraView" shelf
- Click the "Outliner" button
- The outliner window will open!

That's it! 🎉

## 🔧 Manual Setup (Alternative)

If you prefer not to use justfile:

### Step 1: Install Dependencies

```bash
npm install
```

### Step 2: Start Dev Server

```bash
npm run dev
```

You should see:
```
VITE v6.4.1  ready in 650 ms
➜  Local:   http://localhost:5173/
```

### Step 3: Run in Maya

Open Maya's Script Editor and paste:

```python
import sys
sys.path.append(r"C:\path\to\auroraview-maya-outliner")

# Launch outliner
from maya_integration import maya_outliner
maya_outliner.main()

# Or launch Windows WebView2 backend directly (experimental)
from maya_integration.launch_webview2 import launch
h = launch("http://localhost:5173", 1000, 700)
```

**Replace the path** with your actual project path!

## ✅ What You Should See

1. **WebView Window** opens with title "Maya Outliner"
2. **Connection Status** shows "Connected" (green dot)
3. **Scene Tree** displays your Maya scene hierarchy
4. **Click a node** → Maya selects it
5. **Select in Maya** → UI highlights it
6. **Click 👁️ icon** → Toggle visibility

## 🐛 Troubleshooting

### "Cannot find module 'auroraview'"

Install AuroraView in Maya's Python:
```bash
mayapy -m pip install auroraview
```

### "Connection Status: Disconnected"

1. Check Vite dev server is running (`npm run dev`)
2. Verify URL is `http://localhost:5173`
3. Check firewall settings

### WebView doesn't open

1. Check Maya's Script Editor for errors
2. Verify path in `sys.path.append()` is correct
3. Try running `test_standalone.py` first

## 📚 Next Steps

- Read [README.md](./README.md) for full documentation
- Explore the code in `src/` directory
- Modify `maya/maya_outliner.py` to add features
- Check performance with large scenes (10,000+ nodes)

## 🎯 Key Files

- `src/App.vue` - Main UI component
- `src/components/TreeNode.vue` - Individual node rendering
- `src/composables/useMayaIPC.ts` - IPC communication
- `maya/maya_outliner.py` - Maya backend

Happy coding! 🎉

