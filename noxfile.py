"""Nox sessions for building and packaging Maya Outliner."""

import argparse
import os
import shutil
import zipfile
from pathlib import Path

import nox


# Project configuration
PROJECT_ROOT = Path(__file__).parent
PACKAGE_NAME = "maya-outliner"
MAYA_INTEGRATION_DIR = PROJECT_ROOT / "auroraview_maya_outliner"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / ".build"


@nox.session(name="make-maya-package")
def make_maya_package(session: nox.Session) -> None:
    """Create a Maya plugin installation package.

    This creates a zip file containing:
    - Built frontend files (dist/)
    - Maya integration Python code (auroraview_maya_outliner/)
    - Installation scripts (install.bat, install.sh)
    - userSetup.py for auto-loading
    - README and documentation

    Usage:
        nox -s make-maya-package -- --version 1.0.0
    """
    # Parse arguments
    parser = argparse.ArgumentParser(prog="nox -s make-maya-package")
    parser.add_argument("--version", default="0.1.0", help="Version for the package")
    args = parser.parse_args(session.posargs)
    version = str(args.version)
    
    print(f"📦 Creating Maya Outliner package v{version}")
    
    # Clean and create build directory
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True)
    
    package_dir = BUILD_DIR / "maya-outliner"
    package_dir.mkdir()
    
    # 1. Copy dist files (built frontend)
    print("📁 Copying frontend files...")
    if not DIST_DIR.exists():
        session.error("❌ dist/ directory not found. Run 'npm run build' first!")
    shutil.copytree(DIST_DIR, package_dir / "dist")
    
    # 2. Copy auroraview_maya_outliner
    print("📁 Copying Maya integration code...")
    shutil.copytree(MAYA_INTEGRATION_DIR, package_dir / "auroraview_maya_outliner")
    
    # 3. Create production userSetup.py (not copying dev version)
    print("📁 Creating production userSetup.py...")
    create_production_usersetup(package_dir)
    
    # 4. Create installation scripts
    print("📝 Creating installation scripts...")
    create_install_scripts(package_dir, version)
    
    # 5. Copy documentation
    print("📁 Copying documentation...")
    docs_to_copy = ["README.md", "README_zh.md", "DEPLOYMENT.md", "QUICKSTART.md"]
    for doc in docs_to_copy:
        doc_path = PROJECT_ROOT / doc
        if doc_path.exists():
            shutil.copy2(doc_path, package_dir / doc)
    
    # 6. Create .mod file
    print("📝 Creating Maya module file...")
    create_mod_file(package_dir, version)
    
    # 7. Create zip file
    print("🗜️  Creating zip archive...")
    zip_filename = f"{PACKAGE_NAME}-{version}.zip"
    zip_path = DIST_DIR / zip_filename
    
    # Ensure dist directory exists
    DIST_DIR.mkdir(exist_ok=True)
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(BUILD_DIR)
                zipf.write(file_path, arcname)
    
    print(f"✅ Package created: {zip_path}")
    print(f"📦 Size: {zip_path.stat().st_size / 1024 / 1024:.2f} MB")


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
    
    # PowerShell script
    install_ps1 = package_dir / "install.ps1"
    install_ps1.write_text(f"""# AuroraView Maya Outliner Installer v{version}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Maya Outliner Installer v{version}" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$mayaModulesDir = Join-Path $env:USERPROFILE "Documents\\maya\\modules"
$modFile = Join-Path $mayaModulesDir "maya-outliner.mod"

# Create modules directory if it doesn't exist
if (-not (Test-Path $mayaModulesDir)) {{
    Write-Host "Creating Maya modules directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $mayaModulesDir | Out-Null
}}

# Create .mod file
Write-Host "Creating module file..." -ForegroundColor Green
"+ maya-outliner {version} $scriptDir" | Out-File -FilePath $modFile -Encoding utf8

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Module file created at:" -ForegroundColor White
Write-Host $modFile -ForegroundColor Yellow
Write-Host ""
Write-Host "To use Maya Outliner:" -ForegroundColor White
Write-Host "1. Restart Maya" -ForegroundColor White
Write-Host "2. In Script Editor, run:" -ForegroundColor White
Write-Host "   from auroraview_maya_outliner import main" -ForegroundColor Cyan
Write-Host "   main()" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
""", encoding="utf-8")


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


if __name__ == "__main__":
    # Allow running directly for testing
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        class MockSession:
            posargs = ["--version", "0.1.0-test"]
        make_maya_package(MockSession())

