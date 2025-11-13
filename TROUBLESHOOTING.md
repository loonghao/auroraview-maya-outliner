# Troubleshooting Guide

## Shelf Not Appearing

If the AuroraView shelf doesn't appear when you launch Maya, follow these steps:

### 1. Check Maya Script Editor Output

Open Maya's Script Editor (Windows → General Editors → Script Editor) and look for messages starting with `[AuroraView]`.

**Expected output:**
```
============================================================
AuroraView Outliner - Setup
============================================================
Project Root: C:\github\auroraview-maya-outliner
[AuroraView] Added to PYTHONPATH: C:\github\auroraview-maya-outliner
[AuroraView] ✓ AuroraView dev loaded
[AuroraView] ✓ Maya integration loaded
[AuroraView] Created shelf: AuroraView
[AuroraView] ✓ Created shelf button: Outliner
[AuroraView] ✓ Setup complete!
[AuroraView] Click the 'Outliner' button on the AuroraView shelf to launch
============================================================
```

### 2. Common Issues and Solutions

#### Issue: "Failed to import auroraview"
**Solution:** Install AuroraView
```bash
mayapy -m pip install auroraview
```

#### Issue: "Failed to import maya_integration"
**Solution:** Check that PROJECT_ROOT is correct
```powershell
# Verify userSetup.py has correct path
Get-Content "$env:USERPROFILE\Documents\maya\2024\scripts\userSetup.py" | Select-String "PROJECT_ROOT"
```

Should show:
```python
PROJECT_ROOT = r"C:\github\auroraview-maya-outliner"
```

#### Issue: No output in Script Editor
**Solution:** userSetup.py might not be loaded

1. Check if file exists:
```powershell
Test-Path "$env:USERPROFILE\Documents\maya\2024\scripts\userSetup.py"
```

2. Re-run setup:
```bash
just clean-maya 2024
just maya-2024
```

3. Restart Maya

### 3. Manual Testing

If automatic setup doesn't work, try running the setup manually in Maya's Script Editor:

```python
import sys
sys.path.insert(0, r"C:\github\auroraview-maya-outliner")

from maya_integration import maya_outliner
maya_outliner.main()
```

### 4. Check Maya Version

Make sure you're using the correct Maya version command:
```bash
just maya-2022  # For Maya 2022
just maya-2024  # For Maya 2024
just maya-2025  # For Maya 2025
```

### 5. Verify Installation

Run the info command to check your setup:
```bash
just info
```

Expected output:
```
=== AuroraView Maya Outliner ===
Project Root: C:\github\auroraview-maya-outliner
UserSetup File: C:\github\auroraview-maya-outliner\userSetup.py

=== Maya Installations ===
✓ Maya 2024: C:/Program Files/Autodesk/Maya2024/bin/maya.exe

=== UserSetup Status ===
✓ Maya 2024: Installed
```

### 6. Enable Debug Mode

Add this to the top of userSetup.py for more verbose output:
```python
import sys
print("=" * 80)
print("DEBUG: Python version:", sys.version)
print("DEBUG: Python path:", sys.path)
print("=" * 80)
```

### 7. Check for Conflicts

If you have other userSetup.py files or Maya modules, they might conflict. Check:
```powershell
# Check for other userSetup.py files
Get-ChildItem "$env:USERPROFILE\Documents\maya" -Recurse -Filter "userSetup.py"

# Check for Maya modules
Get-ChildItem "$env:USERPROFILE\Documents\maya\modules" -Filter "*.mod"
```

## Still Having Issues?

1. Check the Maya Output Window (not just Script Editor)
2. Look for Python errors in Maya's console
3. Try running Maya from command line to see startup messages:
```bash
"C:\Program Files\Autodesk\Maya2024\bin\maya.exe"
```

4. Create an issue on GitHub with:
   - Maya version
   - Python version (run `mayapy --version`)
   - Full Script Editor output
   - Output of `just info`

