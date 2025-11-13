"""
Test script to verify Maya setup
Run this in Maya's Script Editor to check if everything is configured correctly
"""

import sys
import os

print("=" * 80)
print("AuroraView Maya Outliner - Setup Test")
print("=" * 80)

# Test 1: Check Python version
print("\n[Test 1] Python Version")
print(f"  Version: {sys.version}")
print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor}")

# Test 2: Check if project root is in path
print("\n[Test 2] Python Path")
project_root = r"C:\github\auroraview-maya-outliner"
if project_root in sys.path:
    print(f"  ✓ Project root in PYTHONPATH: {project_root}")
else:
    print(f"  ✗ Project root NOT in PYTHONPATH")
    print(f"  Adding it now...")
    sys.path.insert(0, project_root)
    print(f"  ✓ Added: {project_root}")

# Test 3: Try to import auroraview
print("\n[Test 3] AuroraView Import")
try:
    import auroraview
    print(f"  ✓ AuroraView imported successfully")
    print(f"  Version: {getattr(auroraview, '__version__', 'dev')}")
    print(f"  Location: {auroraview.__file__}")
except ImportError as e:
    print(f"  ✗ Failed to import auroraview: {e}")
    print(f"  Install with: mayapy -m pip install auroraview")

# Test 4: Try to import maya_integration
print("\n[Test 4] Maya Integration Import")
try:
    from maya_integration import maya_outliner
    print(f"  ✓ Maya integration imported successfully")
    print(f"  Location: {maya_outliner.__file__}")
except ImportError as e:
    print(f"  ✗ Failed to import maya_integration: {e}")
    print(f"  Check that project root is correct")

# Test 5: Check if shelf exists
print("\n[Test 5] Shelf Check")
try:
    from maya import cmds
    shelf_name = "AuroraView"
    if cmds.shelfLayout(shelf_name, exists=True):
        print(f"  ✓ Shelf '{shelf_name}' exists")
        buttons = cmds.shelfLayout(shelf_name, query=True, childArray=True) or []
        print(f"  Buttons: {len(buttons)}")
        for button in buttons:
            label = cmds.shelfButton(button, query=True, label=True)
            print(f"    - {label}")
    else:
        print(f"  ✗ Shelf '{shelf_name}' does not exist")
        print(f"  It should be created automatically on Maya startup")
except Exception as e:
    print(f"  ✗ Error checking shelf: {e}")

# Test 6: Try to launch outliner
print("\n[Test 6] Launch Outliner")
try:
    from maya_integration import maya_outliner
    print(f"  Attempting to launch outliner...")
    maya_outliner.main()
    print(f"  ✓ Outliner launched successfully!")
except Exception as e:
    print(f"  ✗ Failed to launch outliner: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Test Complete!")
print("=" * 80)

