"""Build script for creating Maya Outliner installation package.

This script creates a distributable package containing:
- Built frontend files (dist/)
- Maya integration Python code (auroraview_maya_outliner/)
- Installation scripts (install.bat, install.ps1, install.sh)
- userSetup.py for auto-loading
- Maya module (.mod) file
- README and documentation

Usage:
    python build_maya_package.py --version 0.1.0
"""

import argparse
import os
import shutil
import zipfile
from pathlib import Path


# Project configuration
PROJECT_ROOT = Path(__file__).parent
PACKAGE_NAME = "maya-outliner"
MAYA_INTEGRATION_DIR = PROJECT_ROOT / "auroraview_maya_outliner"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / ".build"


def create_mod_file(package_dir: Path, version: str) -> None:
    """Create Maya module (.mod) file with correct PYTHONPATH."""
    mod_file = package_dir / "maya-outliner.mod"
    mod_file.write_text(f"""+ MAYAVERSION:2022 auroraview-maya-outliner {version} ./
PYTHONPATH +:= auroraview_maya_outliner

+ MAYAVERSION:2024 auroraview-maya-outliner {version} ./
PYTHONPATH +:= auroraview_maya_outliner

+ MAYAVERSION:2025 auroraview-maya-outliner {version} ./
PYTHONPATH +:= auroraview_maya_outliner
""", encoding="utf-8")
    print(f"✅ Created Maya module file: {mod_file}")


def create_install_scripts(package_dir: Path, version: str) -> None:
    """Create installation scripts for different platforms."""
    
    # Windows batch script
    install_bat = package_dir / "install.bat"
    install_bat.write_text(f"""@echo off
REM AuroraView Maya Outliner Installer v{version}

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

REM Copy .mod file to modules directory
echo Installing module file...
copy /Y "%SCRIPT_DIR%maya-outliner.mod" "%MOD_FILE%"

REM Update paths in mod file
powershell -Command "(Get-Content '%MOD_FILE%') -replace '\\./', '%SCRIPT_DIR%' | Set-Content '%MOD_FILE%'"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Module file installed at:
echo %MOD_FILE%
echo.
echo To use Maya Outliner:
echo 1. Restart Maya
echo 2. In Script Editor, run:
echo    from auroraview_maya_outliner import main
echo    main()
echo.
echo Or copy userSetup.py to Maya scripts folder for auto-load
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
$sourceModFile = Join-Path $scriptDir "maya-outliner.mod"

# Create modules directory if it doesn't exist
if (-not (Test-Path $mayaModulesDir)) {{
    Write-Host "Creating Maya modules directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $mayaModulesDir | Out-Null
}}

# Copy .mod file and update paths
Write-Host "Installing module file..." -ForegroundColor Green
Copy-Item -Path $sourceModFile -Destination $modFile -Force

# Update paths in mod file (replace ./ with actual script directory)
(Get-Content $modFile) -replace '\\./', $scriptDir | Set-Content $modFile

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Module file installed at:" -ForegroundColor White
Write-Host $modFile -ForegroundColor Yellow
Write-Host ""
Write-Host "To use Maya Outliner:" -ForegroundColor White
Write-Host "1. Restart Maya" -ForegroundColor White
Write-Host "2. In Script Editor, run:" -ForegroundColor White
Write-Host "   from auroraview_maya_outliner import main" -ForegroundColor Cyan
Write-Host "   main()" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or copy userSetup.py to Maya scripts folder for auto-load" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
""", encoding="utf-8")
    
    print(f"✅ Created installation scripts")


def create_usersetup(package_dir: Path) -> None:
    """Create userSetup.py with relative path support."""
    usersetup_file = package_dir / "userSetup.py"
    usersetup_content = '''"""
Maya userSetup.py for AuroraView Outliner

Copy this file to your Maya scripts directory:
- Windows: C:/Users/<username>/Documents/maya/<version>/scripts/userSetup.py
- macOS: ~/Library/Preferences/Autodesk/maya/<version>/scripts/userSetup.py
- Linux: ~/maya/<version>/scripts/userSetup.py

This will automatically create a shelf button when Maya starts.
"""

import os
import sys

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
        print(f"[AuroraView] ✓ Maya integration loaded")
    except ImportError as e:
        print(f"[AuroraView] ✗ Failed to import auroraview_maya_outliner: {e}")
        print(f"[AuroraView]   Make sure Maya module is installed correctly")
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
'''
    usersetup_file.write_text(usersetup_content, encoding="utf-8")
    print(f"✅ Created userSetup.py")


def build_package(version: str) -> Path:
    """Build the Maya Outliner package.

    Args:
        version: Version string for the package

    Returns:
        Path to the created zip file
    """
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
        raise FileNotFoundError("dist/ directory not found. Run 'npm run build' first!")
    shutil.copytree(DIST_DIR, package_dir / "dist")

    # 2. Copy auroraview_maya_outliner
    print("📁 Copying Maya integration code...")
    if not MAYA_INTEGRATION_DIR.exists():
        raise FileNotFoundError(f"Maya integration directory not found: {MAYA_INTEGRATION_DIR}")
    shutil.copytree(MAYA_INTEGRATION_DIR, package_dir / "auroraview_maya_outliner")

    # 3. Create userSetup.py
    print("📝 Creating userSetup.py...")
    create_usersetup(package_dir)

    # 4. Create installation scripts
    print("📝 Creating installation scripts...")
    create_install_scripts(package_dir, version)

    # 5. Create .mod file
    print("📝 Creating Maya module file...")
    create_mod_file(package_dir, version)

    # 6. Create zip file
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

    return zip_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build Maya Outliner package")
    parser.add_argument("--version", default="0.1.0", help="Version for the package")
    args = parser.parse_args()

    try:
        zip_path = build_package(args.version)
        print()
        print("=" * 60)
        print("✅ Build Complete!")
        print("=" * 60)
        print(f"Package: {zip_path}")
        print()
        print("To install:")
        print("1. Extract the zip file")
        print("2. Run install.bat (Windows) or install.ps1 (PowerShell)")
        print("3. Restart Maya")
        print("4. Click the 'Outliner' button on the AuroraView shelf")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())


