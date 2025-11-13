"""
Maya userSetup.py for AuroraView Outliner

This file is automatically copied by justfile when you run:
    just maya-2022
    just maya-2024
    just maya-2025

It will be placed in:
- Windows: C:/Users/<username>/Documents/maya/<version>/scripts/userSetup.py
- macOS: ~/Library/Preferences/Autodesk/maya/<version>/scripts/userSetup.py
- Linux: ~/maya/<version>/scripts/userSetup.py

The justfile will inject the correct PROJECT_ROOT path during setup.
"""

import os
import sys

import maya.utils as mutils
from maya import cmds

# This will be replaced by justfile with the actual project path
PROJECT_ROOT = r"{{PROJECT_ROOT}}"


def setup_auroraview_outliner():
    """Setup AuroraView Outliner on Maya startup"""

    print("=" * 60)
    print("AuroraView Outliner - Setup")
    print("=" * 60)
    print(f"Project Root: {PROJECT_ROOT}")

    # Add maya-outliner project to Python path
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
        print(f"[AuroraView] Added to PYTHONPATH: {PROJECT_ROOT}")

    # Verify auroraview is available
    try:
        import auroraview
        print(f"[AuroraView] ✓ AuroraView {getattr(auroraview, '__version__', 'dev')} loaded")
    except ImportError as e:
        print(f"[AuroraView] ✗ Failed to import auroraview: {e}")
        print("[AuroraView]   Please install: mayapy -m pip install auroraview")
        return

    # Verify maya_integration is available
    try:
        from maya_integration import maya_outliner
        print(f"[AuroraView] ✓ Maya integration loaded")
    except ImportError as e:
        print(f"[AuroraView] ✗ Failed to import maya_integration: {e}")
        print(f"[AuroraView]   Check that PROJECT_ROOT is correct: {PROJECT_ROOT}")
        return

    # Create a shelf button for easy access
    def create_shelf_button():
        """Create a shelf button to launch the outliner"""

        # Get or create AuroraView shelf
        shelf_name = "AuroraView"
        if not cmds.shelfLayout(shelf_name, exists=True):
            cmds.shelfLayout(shelf_name, parent="ShelfLayout")
            print(f"[AuroraView] Created shelf: {shelf_name}")

        # Check if button already exists
        existing_buttons = cmds.shelfLayout(shelf_name, query=True, childArray=True) or []
        for button in existing_buttons:
            if cmds.shelfButton(button, query=True, label=True) == "Outliner":
                print("[AuroraView] Shelf button already exists")
                return

        # Create shelf button
        cmds.shelfButton(
            parent=shelf_name,
            label="Outliner",
            annotation="Launch AuroraView Outliner",
            image="outliner.png",
            command=f"""
import sys

# Ensure project path is set
project_root = r"{PROJECT_ROOT}"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Launch outliner
from maya_integration import maya_outliner
maya_outliner.main()
""",
            sourceType="python",
        )
        print("[AuroraView] ✓ Created shelf button: Outliner")

    # Create shelf button after Maya UI is ready
    mutils.executeDeferred(create_shelf_button)

    print("[AuroraView] ✓ Setup complete!")
    print("[AuroraView] Click the 'Outliner' button on the AuroraView shelf to launch")
    print("=" * 60)


# Run setup when Maya starts
try:
    setup_auroraview_outliner()
except Exception as e:
    print("=" * 60)
    print(f"[AuroraView] ✗ Error during setup: {e}")
    import traceback
    traceback.print_exc()
    print("=" * 60)
