# AuroraView Maya Outliner v{VERSION}

## 📦 Installation

### Quick Install

1. **Download** `maya-outliner-{VERSION}.zip` from the assets below
2. **Extract** the zip file to any location
3. **Run** the installer:
   - Windows: `install.bat` or `install.ps1`
   - Linux/macOS: `./install.sh`
4. **Restart** Maya
5. **Launch** in Maya Script Editor:
   ```python
   from maya_integration import main
   main()
   ```

### Requirements

- Maya 2020+ (Python 3.7+)
- AuroraView installed in Maya's Python environment

### First Time Setup

If you haven't installed AuroraView yet:

```bash
# In Maya's Python (mayapy)
mayapy -m pip install auroraview[qt]
```

## 📚 Documentation

- [Installation Guide](https://github.com/loonghao/auroraview-maya-outliner/blob/main/INSTALLATION.md)
- [Quick Start](https://github.com/loonghao/auroraview-maya-outliner/blob/main/QUICKSTART.md)
- [Deployment Guide](https://github.com/loonghao/auroraview-maya-outliner/blob/main/DEPLOYMENT.md)
- [Local Development](https://github.com/loonghao/auroraview-maya-outliner/blob/main/LOCAL_DEVELOPMENT.md)

## ✨ Features

- 🌳 Hierarchical scene tree with expandable nodes
- 🎯 Real-time bidirectional selection sync
- 👁️ Visibility toggle for objects
- 🔍 Search and filter by name
- ⚡ High performance (10,000+ nodes)
- 🎨 Modern dark-themed UI
- 🔄 Live updates on scene changes

## 🔧 Configuration

### Environment Modes

Control the frontend loading mode with `AURORAVIEW_ENV`:

**Production Mode** (uses built static files):
```bash
# Windows
set AURORAVIEW_ENV=production

# Linux/macOS
export AURORAVIEW_ENV=production
```

**Development Mode** (uses Vite dev server):
```bash
# Windows
set AURORAVIEW_ENV=development

# Linux/macOS
export AURORAVIEW_ENV=development
```

## 🐛 Known Issues

- None reported for this release

## 🙏 Acknowledgments

Built with:
- [AuroraView](https://github.com/loonghao/auroraview) - Rust-powered WebView framework
- [Vue 3](https://vuejs.org/) - Progressive JavaScript framework
- [TypeScript](https://www.typescriptlang.org/) - Typed JavaScript
- [Vite](https://vitejs.dev/) - Next generation frontend tooling

## 📝 Changelog

{CHANGELOG_CONTENT}

## 🔗 Links

- [GitHub Repository](https://github.com/loonghao/auroraview-maya-outliner)
- [Report Issues](https://github.com/loonghao/auroraview-maya-outliner/issues)
- [Discussions](https://github.com/loonghao/auroraview-maya-outliner/discussions)

---

**Full Changelog**: {COMPARE_URL}

