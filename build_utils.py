"""Build utilities for Maya Outliner package.

This module contains helper functions for building the Maya plugin package.
These are extracted from noxfile.py to enable testing without nox dependency.
"""

from pathlib import Path


# Shelf configuration - must match build_maya_package.py
SHELF_NAME = "auroraview"


def create_mod_file(package_dir: Path, version: str) -> None:
    """Create Maya module (.mod) file.

    The PYTHONPATH includes both the package root (for auroraview_maya_outliner)
    and the vendor directory (for third-party dependencies like auroraview).
    """
    mod_file = package_dir / "maya-outliner.mod"
    mod_file.write_text(
        f"""+ MAYAVERSION:2022 maya-outliner {version} ./
scripts: scripts
PYTHONPATH +:= .
PYTHONPATH +:= vendor

+ MAYAVERSION:2024 maya-outliner {version} ./
scripts: scripts
PYTHONPATH +:= .
PYTHONPATH +:= vendor

+ MAYAVERSION:2025 maya-outliner {version} ./
scripts: scripts
PYTHONPATH +:= .
PYTHONPATH +:= vendor
""",
        encoding="utf-8",
    )


def create_production_usersetup(package_dir: Path) -> None:
    """Create production userSetup.py for the release package.

    This version auto-detects the installation path and sets up the shelf button.
    Unlike the development version, it doesn't require PROJECT_ROOT to be injected.
    The shelf name is 'auroraview' (lowercase) for consistency.
    """
    # Create scripts directory if it doesn't exist
    scripts_dir = package_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    usersetup_file = scripts_dir / "userSetup.py"
    usersetup_file.write_text(
        f'''"""
Maya userSetup.py for AuroraView Outliner (Production Version)

This file is automatically installed by the installer.
It creates the '{SHELF_NAME}' shelf with an Outliner button when Maya starts.

Manual installation:
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

    # Verify auroraview is available (bundled in vendor/)
    try:
        import auroraview
        print(f"[AuroraView] ✓ AuroraView {{getattr(auroraview, '__version__', 'dev')}} loaded")
    except ImportError as e:
        print(f"[AuroraView] ✗ Failed to import auroraview: {{e}}")
        print("[AuroraView]   Make sure Maya module (.mod) is installed correctly")
        return

    # Verify auroraview_maya_outliner is available
    try:
        from auroraview_maya_outliner import maya_outliner
        print("[AuroraView] ✓ Maya integration loaded")
    except ImportError as e:
        print(f"[AuroraView] ✗ Failed to import auroraview_maya_outliner: {{e}}")
        print("[AuroraView]   Make sure Maya module (.mod) is installed correctly")
        return

    # Create a shelf button for easy access
    def create_shelf_button():
        """Create a shelf button to launch the outliner"""
        try:
            print("[AuroraView] Creating shelf button...")

            # Get or create auroraview shelf (lowercase)
            shelf_name = "{SHELF_NAME}"
            if not cmds.shelfLayout(shelf_name, exists=True):
                cmds.shelfLayout(shelf_name, parent="ShelfLayout")
                print(f"[AuroraView] Created shelf: {{shelf_name}}")
            else:
                print(f"[AuroraView] Shelf '{{shelf_name}}' already exists")

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
                annotation="Launch AuroraView Outliner - Modern web-based scene outliner",
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
            print(f"[AuroraView] ✗ Error creating shelf button: {{e}}")
            import traceback
            traceback.print_exc()

    # Create shelf button after Maya UI is ready
    print("[AuroraView] Scheduling shelf creation...")
    mutils.executeDeferred(create_shelf_button)

    print("[AuroraView] ✓ Setup complete!")
    print(f"[AuroraView] Click the 'Outliner' button on the '{SHELF_NAME}' shelf to launch")
    print("=" * 60)


# Run setup when Maya starts
try:
    setup_auroraview_outliner()
except Exception as e:
    print("=" * 60)
    print(f"[AuroraView] ✗ Error during setup: {{e}}")
    import traceback
    traceback.print_exc()
    print("=" * 60)
''',
        encoding="utf-8",
    )


def create_install_scripts(package_dir: Path, version: str) -> None:
    """Create installation scripts for different platforms."""

    # Windows batch script
    install_bat = package_dir / "install.bat"
    install_bat.write_text(
        f"""@echo off
REM AuroraView Maya Outliner Installer v{version}

echo ========================================
echo AuroraView Maya Outliner Installer v{version}
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

REM Copy .mod file to modules directory
echo Installing module file...
copy /Y "%SCRIPT_DIR%maya-outliner.mod" "%MOD_FILE%"

REM Update module path in mod file (replace ' ./' with actual path)
powershell -Command "$content = Get-Content '%MOD_FILE%' -Raw; $content = $content -replace ' \\./', ' %SCRIPT_DIR%'; $content | Set-Content '%MOD_FILE%' -NoNewline"

echo.

REM Ask user if they want to install userSetup.py for auto-loading
echo Do you want to install userSetup.py for auto-loading?
echo This will create the '{SHELF_NAME}' shelf with an Outliner button.
echo.
set /p INSTALL_USERSETUP="Install userSetup.py? (Y/N): "

if /i "%INSTALL_USERSETUP%"=="Y" (
    echo.
    echo Available Maya versions:
    echo   1. Maya 2022
    echo   2. Maya 2024
    echo   3. Maya 2025
    echo.
    set /p MAYA_VERSION="Select Maya version (1-3): "

    if "%MAYA_VERSION%"=="1" SET "MAYA_SCRIPTS_DIR=%USERPROFILE%\\Documents\\maya\\2022\\scripts"
    if "%MAYA_VERSION%"=="2" SET "MAYA_SCRIPTS_DIR=%USERPROFILE%\\Documents\\maya\\2024\\scripts"
    if "%MAYA_VERSION%"=="3" SET "MAYA_SCRIPTS_DIR=%USERPROFILE%\\Documents\\maya\\2025\\scripts"

    if defined MAYA_SCRIPTS_DIR (
        if not exist "%MAYA_SCRIPTS_DIR%" (
            echo Creating Maya scripts directory...
            mkdir "%MAYA_SCRIPTS_DIR%"
        )
        echo Copying userSetup.py...
        copy /Y "%SCRIPT_DIR%scripts\\userSetup.py" "%MAYA_SCRIPTS_DIR%\\userSetup.py"
        echo.
        echo userSetup.py installed to: %MAYA_SCRIPTS_DIR%
    ) else (
        echo Invalid selection. Skipping userSetup.py installation.
    )
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Module file installed at:
echo   %MOD_FILE%
echo.
echo Next steps:
echo   1. Restart Maya
echo   2. Look for the '{SHELF_NAME}' shelf
echo   3. Click the 'Outliner' button to launch
echo.
echo Or run manually in Script Editor:
echo   from auroraview_maya_outliner import main
echo   main()
echo.
pause
""",
        encoding="utf-8",
    )

