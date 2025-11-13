"""
Maya userSetup.py for AuroraView Outliner - LOCAL DEVELOPMENT VERSION

This file is for local development only and is ignored by git.
It uses the local development version of auroraview from:
C:\Users\hallo\Documents\augment-projects\dcc_webview\python

For production use, copy userSetup.py instead.
"""

import os
import sys

import maya.utils as mutils
from maya import cmds

# Local development paths
LOCAL_AURORAVIEW_PATH = r"C:\Users\hallo\Documents\augment-projects\dcc_webview\python"
PROJECT_ROOT = r"{{PROJECT_ROOT}}"


def setup_auroraview_outliner():
    """Setup AuroraView Outliner on Maya startup - LOCAL DEV VERSION"""

    print("=" * 60)
    print("AuroraView Outliner - Setup (LOCAL DEVELOPMENT)")
    print("=" * 60)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Local AuroraView: {LOCAL_AURORAVIEW_PATH}")

    # Add local auroraview development path FIRST (highest priority)
    if LOCAL_AURORAVIEW_PATH not in sys.path:
        sys.path.insert(0, LOCAL_AURORAVIEW_PATH)
        print(f"[AuroraView] Added LOCAL dev path to PYTHONPATH: {LOCAL_AURORAVIEW_PATH}")

    # Add maya-outliner project to Python path
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
        print(f"[AuroraView] Added to PYTHONPATH: {PROJECT_ROOT}")

    # Verify auroraview is available
    try:
        import auroraview
        print(f"[AuroraView] ✓ AuroraView {getattr(auroraview, '__version__', 'dev')} loaded")
        print(f"[AuroraView]   Location: {auroraview.__file__}")
    except ImportError as e:
        print(f"[AuroraView] ✗ Failed to import auroraview: {e}")
        print(f"[AuroraView]   Check that LOCAL_AURORAVIEW_PATH is correct: {LOCAL_AURORAVIEW_PATH}")
        return

    # Verify maya_integration is available
    try:
        from maya_integration import maya_outliner
        print(f"[AuroraView] ✓ Maya integration loaded")
        print(f"[AuroraView]   Location: {maya_outliner.__file__}")
    except ImportError as e:
        print(f"[AuroraView] ✗ Failed to import maya_integration: {e}")
        print(f"[AuroraView]   Check that PROJECT_ROOT is correct: {PROJECT_ROOT}")
        return

    # Create a shelf button for easy access
    def create_shelf_button():
        """Create a shelf button to launch the outliner"""
        try:
            print("[AuroraView] Creating shelf button...")
            
            # Get or create AuroraView shelf
            shelf_name = "AuroraView"
            if not cmds.shelfLayout(shelf_name, exists=True):
                cmds.shelfLayout(shelf_name, parent="ShelfLayout")
                print(f"[AuroraView] Created shelf: {shelf_name}")
            else:
                print(f"[AuroraView] Shelf '{shelf_name}' already exists")

            # Check if button already exists
            existing_buttons = cmds.shelfLayout(shelf_name, query=True, childArray=True) or []
            for button in existing_buttons:
                try:
                    if cmds.shelfButton(button, query=True, label=True) == "Outliner":
                        print("[AuroraView] Shelf button already exists")
                        return
                except:
                    pass

            # Create shelf button with local dev paths
            cmds.shelfButton(
                parent=shelf_name,
                label="Outliner",
                annotation="Launch AuroraView Outliner (LOCAL DEV)",
                image="outliner.png",
                command=f"""
import sys

# Ensure local dev path is set FIRST
local_auroraview = r"{LOCAL_AURORAVIEW_PATH}"
if local_auroraview not in sys.path:
    sys.path.insert(0, local_auroraview)

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
            print("[AuroraView] ✓ Created shelf button: Outliner (LOCAL DEV)")
        except Exception as e:
            print(f"[AuroraView] ✗ Error creating shelf button: {e}")
            import traceback
            traceback.print_exc()

    # Create shelf button after Maya UI is ready
    print("[AuroraView] Scheduling shelf creation...")
    mutils.executeDeferred(create_shelf_button)

    print("[AuroraView] ✓ Setup complete! (LOCAL DEVELOPMENT MODE)")
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

