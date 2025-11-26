"""Build utilities for Maya Outliner package.

This module contains helper functions for building the Maya plugin package.
These are extracted from noxfile.py to enable testing without nox dependency.
"""

from pathlib import Path


def create_mod_file(package_dir: Path, version: str) -> None:
    """Create Maya module (.mod) file.

    The PYTHONPATH is set to the package root directory (.) so that
    'from auroraview_maya_outliner import ...' works correctly.
    """
    mod_file = package_dir / "maya-outliner.mod"
    mod_file.write_text(f"""+ MAYAVERSION:2022 maya-outliner {version} ./
scripts: ./
PYTHONPATH +:= ./

+ MAYAVERSION:2024 maya-outliner {version} ./
scripts: ./
PYTHONPATH +:= ./

+ MAYAVERSION:2025 maya-outliner {version} ./
scripts: ./
PYTHONPATH +:= ./
""", encoding="utf-8")


def create_production_usersetup(package_dir: Path) -> None:
    """Create production userSetup.py for the release package.

    This version auto-detects the installation path and sets up the shelf button.
    Unlike the development version, it doesn't require PROJECT_ROOT to be injected.
    """
    usersetup_file = package_dir / "userSetup.py"
    usersetup_file.write_text('''"""
Maya userSetup.py for AuroraView Outliner (Production Version)

This file should be copied to your Maya scripts folder:
- Windows: C:/Users/<username>/Documents/maya/<version>/scripts/userSetup.py
- macOS: ~/Library/Preferences/Autodesk/maya/<version>/scripts/userSetup.py
- Linux: ~/maya/<version>/scripts/userSetup.py

The module path is automatically configured via Maya's .mod file.
"""

import maya.utils as mutils
from maya import cmds


def setup_auroraview_outliner():
    """Setup AuroraView Outliner on Maya startup"""

    print("=" * 60)
    print("AuroraView Outliner - Setup")
    print("=" * 60)

    # Verify auroraview is available
    try:
        import auroraview
        print(f"[AuroraView] ✓ AuroraView {getattr(auroraview, '__version__', 'dev')} loaded")
    except ImportError as e:
        print(f"[AuroraView] ✗ Failed to import auroraview: {e}")
        print("[AuroraView]   Please install: mayapy -m pip install auroraview")
        return

    # Verify auroraview_maya_outliner is available
    try:
        from auroraview_maya_outliner import maya_outliner
        print("[AuroraView] ✓ Maya integration loaded")
    except ImportError as e:
        print(f"[AuroraView] ✗ Failed to import auroraview_maya_outliner: {e}")
        print("[AuroraView]   Please check the Maya module (.mod) file is installed correctly")
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
                except Exception:
                    pass

            # Create shelf button
            cmds.shelfButton(
                parent=shelf_name,
                label="Outliner",
                annotation="Launch AuroraView Outliner",
                image="outliner.png",
                command="""
# Launch AuroraView Outliner
from auroraview_maya_outliner import maya_outliner
maya_outliner.main()
""",
                sourceType="python",
            )
            print("[AuroraView] ✓ Created shelf button: Outliner")
        except Exception as e:
            print(f"[AuroraView] ✗ Error creating shelf button: {e}")
            import traceback
            traceback.print_exc()

    # Create shelf button after Maya UI is ready
    print("[AuroraView] Scheduling shelf creation...")
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
''', encoding="utf-8")


def create_install_scripts(package_dir: Path, version: str) -> None:
    """Create installation scripts for different platforms."""

    # Windows batch script
    install_bat = package_dir / "install.bat"
    install_bat.write_text(f"""@echo off
REM AuroraView Maya Outliner Installer v{version}
REM This script installs the Maya Outliner to your Maya modules directory

echo ========================================
echo Maya Outliner Installer v{version}
echo ========================================
echo.

SET "SCRIPT_DIR=%~dp0"
SET "MAYA_MODULES_DIR=%USERPROFILE%\\Documents\\maya\\modules"
SET "MOD_FILE=%MAYA_MODULES_DIR%\\maya-outliner.mod"

REM Create modules directory if it doesn't exist
if not exist "%MAYA_MODULES_DIR%" (
    echo Creating Maya modules directory...
    mkdir "%MAYA_MODULES_DIR%"
)

REM Create .mod file
echo Creating module file...
echo + maya-outliner {version} %SCRIPT_DIR% > "%MOD_FILE%"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Module file created at:
echo %MOD_FILE%
echo.
echo To use Maya Outliner:
echo 1. Restart Maya
echo 2. In Script Editor, run:
echo    from auroraview_maya_outliner import main
echo    main()
echo.
pause
""", encoding="utf-8")

