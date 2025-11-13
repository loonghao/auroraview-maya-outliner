# Local Development Setup

This guide explains how to set up the project for local development with a custom AuroraView installation.

## Overview

When developing AuroraView locally, you may want to use your local development version instead of the installed package. This project supports this workflow through local development configuration files.

## Setup

### 1. Create Local Configuration

The project includes a template `userSetup.local.py` that you can customize for your local environment.

**Default local AuroraView path:**
```
C:\Users\hallo\Documents\augment-projects\dcc_webview\python
```

If your local AuroraView is in a different location, edit `userSetup.local.py`:

```python
# Change this to your local AuroraView path
LOCAL_AURORAVIEW_PATH = r"C:\path\to\your\dcc_webview\python"
```

### 2. Launch Maya with Local Development Mode

Use the `-local` suffix commands to launch Maya with your local AuroraView:

```bash
# Launch Maya 2024 with local development version
just maya-2024-local

# Launch Maya 2022 with local development version
just maya-2022-local

# Launch Maya 2025 with local development version
just maya-2025-local
```

### 3. Verify Local Version is Loaded

When Maya starts, check the Script Editor output:

```
============================================================
AuroraView Outliner - Setup (LOCAL DEVELOPMENT)
============================================================
Project Root: C:\github\auroraview-maya-outliner
Local AuroraView: C:\Users\hallo\Documents\augment-projects\dcc_webview\python
[AuroraView] Added LOCAL dev path to PYTHONPATH: C:\Users\hallo\Documents\augment-projects\dcc_webview\python
[AuroraView] Added to PYTHONPATH: C:\github\auroraview-maya-outliner
[AuroraView] ✓ AuroraView dev loaded
[AuroraView]   Location: C:\Users\hallo\Documents\augment-projects\dcc_webview\python\auroraview\__init__.py
```

The key indicator is the **Location** line showing your local path.

## How It Works

### File Structure

- `userSetup.py` - Production version (uses installed auroraview)
- `userSetup.local.py` - Local development version (uses local auroraview path)
- `.gitignore` - Ignores `*.local.py` files

### Path Priority

When using local development mode, Python paths are set in this order:

1. **Local AuroraView path** (highest priority)
2. **Project root** (maya-outliner)
3. **System paths**

This ensures your local AuroraView code is used instead of the installed package.

### Commands

| Command | Description | Uses |
|---------|-------------|------|
| `just maya-2024` | Production mode | Installed auroraview |
| `just maya-2024-local` | Development mode | Local auroraview |

## Switching Between Modes

You can easily switch between production and development modes:

```bash
# Use production version
just clean-maya 2024
just maya-2024

# Use local development version
just clean-maya 2024
just maya-2024-local
```

The `clean-maya` command removes the current `userSetup.py` from Maya's scripts folder, allowing you to switch modes cleanly.

## Customizing Local Paths

If you need to customize the local AuroraView path:

1. Edit `userSetup.local.py`
2. Change the `LOCAL_AURORAVIEW_PATH` variable
3. Run `just maya-2024-local` to apply changes

Example:

```python
# userSetup.local.py
LOCAL_AURORAVIEW_PATH = r"D:\my-projects\auroraview\python"
```

## Git Ignore

The `.gitignore` file is configured to ignore:
- `userSetup.local.py` (after first commit as template)
- `*.local.py` (any other local configuration files)

This prevents your local paths from being committed to the repository.

## Troubleshooting

### Wrong AuroraView Version Loaded

Check the Script Editor output for the "Location" line. If it's not showing your local path:

1. Verify `LOCAL_AURORAVIEW_PATH` in `userSetup.local.py`
2. Run `just clean-maya 2024` to remove old configuration
3. Run `just maya-2024-local` again

### Import Errors

If you see import errors:

1. Verify your local AuroraView path exists
2. Check that the path contains the `auroraview` module
3. Ensure the path structure is: `<LOCAL_PATH>/auroraview/__init__.py`

### Shelf Button Not Working

The shelf button in local development mode includes the local path in its command. If it's not working:

1. Check Script Editor for errors
2. Verify the shelf button annotation says "(LOCAL DEV)"
3. Try running the outliner manually:

```python
import sys
sys.path.insert(0, r"C:\Users\hallo\Documents\augment-projects\dcc_webview\python")
sys.path.insert(0, r"C:\github\auroraview-maya-outliner")

from maya_integration import maya_outliner
maya_outliner.main()
```

## Best Practices

1. **Always use `-local` commands** when developing AuroraView
2. **Test with production mode** before committing changes
3. **Don't commit** `userSetup.local.py` with your personal paths
4. **Document** any changes to the local development workflow

