"""Build script for creating Maya Outliner installation package.

This script creates a distributable package containing:
- Built frontend files (dist/)
- Maya integration Python code (auroraview_maya_outliner/)
- Third-party Python dependencies (vendor/)
- Installation scripts (install.bat, install.ps1, install.sh)
- userSetup.py for auto-loading with shelf button creation
- Maya module (.mod) file
- README and documentation

Usage:
    python build_maya_package.py --version 0.1.0
    python build_maya_package.py --version 0.1.0 --skip-vendor  # Skip downloading dependencies
"""

import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


# Project configuration
PROJECT_ROOT = Path(__file__).parent
PACKAGE_NAME = "maya-outliner"
MAYA_INTEGRATION_DIR = PROJECT_ROOT / "auroraview_maya_outliner"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / ".build"

# Third-party dependencies to bundle
# Format: (package_name, include_deps)
# include_deps=True will also download package dependencies
VENDOR_PACKAGES = [
    ("auroraview", False),  # Core package, no deps (Maya has them)
    ("QtPy", False),  # Qt abstraction layer, needed for Maya Qt integration
]

# Shelf configuration
SHELF_NAME = "auroraview"

# Target platform configuration for pip download
# We target Windows + Python 3.7+ for Maya 2022 compatibility
PLATFORM_ARGS = [
    "--platform",
    "win_amd64",
    "--python-version",
    "3.7",  # Maya 2022 uses Python 3.7
    "--only-binary",
    ":all:",
]


def download_vendor_packages(vendor_dir: Path) -> None:
    """Download third-party packages to vendor directory.

    Downloads Windows-compatible wheels for Python 3.7+ to ensure
    compatibility with Maya 2022 and newer versions.

    Args:
        vendor_dir: Target directory for vendor packages
    """
    vendor_dir.mkdir(parents=True, exist_ok=True)

    print(f"📦 Downloading vendor packages to {vendor_dir}")
    print(f"   Target: Windows x64, Python 3.7+")

    for package_info in VENDOR_PACKAGES:
        if isinstance(package_info, tuple):
            package, include_deps = package_info
        else:
            package = package_info
            include_deps = False

        print(f"   Downloading {package}...")
        try:
            # Build pip download command
            cmd = [
                sys.executable,
                "-m",
                "pip",
                "download",
                "--dest",
                str(vendor_dir),
            ]

            # Add platform-specific arguments
            cmd.extend(PLATFORM_ARGS)

            # Add --no-deps if we don't want dependencies
            if not include_deps:
                cmd.append("--no-deps")

            cmd.append(package)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                # Fallback: try without platform args (use current platform)
                print(f"   ⚠️  Platform-specific download failed, trying current platform...")
                cmd = [
                    sys.executable,
                    "-m",
                    "pip",
                    "download",
                    "--dest",
                    str(vendor_dir),
                ]
                if not include_deps:
                    cmd.append("--no-deps")
                cmd.append(package)

                subprocess.run(cmd, capture_output=True, text=True, check=True)

            print(f"   ✅ Downloaded {package}")

            # Extract all wheel files for this package
            package_prefix = package.lower().replace("-", "_")
            for whl_file in vendor_dir.glob("*.whl"):
                whl_name_lower = whl_file.name.lower()
                if whl_name_lower.startswith(package_prefix):
                    print(f"   📂 Extracting {whl_file.name}...")
                    import zipfile as zf

                    with zf.ZipFile(whl_file, "r") as zip_ref:
                        zip_ref.extractall(vendor_dir)
                    # Remove the wheel file after extraction
                    whl_file.unlink()

            # Remove .dist-info directories (cleanup)
            for dist_info in vendor_dir.glob("*.dist-info"):
                shutil.rmtree(dist_info)

        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Warning: Failed to download {package}: {e.stderr}")
            print(f"   ⚠️  Users may need to install it manually: pip install {package}")


def create_mod_file(package_dir: Path, version: str) -> None:
    """Create Maya module (.mod) file with correct PYTHONPATH.

    The PYTHONPATH includes both the package root (for auroraview_maya_outliner)
    and the vendor directory (for third-party dependencies like auroraview).
    """
    mod_file = package_dir / "maya-outliner.mod"
    mod_file.write_text(
        f"""+ MAYAVERSION:2022 auroraview-maya-outliner {version} ./
scripts: scripts
PYTHONPATH +:= .
PYTHONPATH +:= vendor

+ MAYAVERSION:2024 auroraview-maya-outliner {version} ./
scripts: scripts
PYTHONPATH +:= .
PYTHONPATH +:= vendor

+ MAYAVERSION:2025 auroraview-maya-outliner {version} ./
scripts: scripts
PYTHONPATH +:= .
PYTHONPATH +:= vendor
""",
        encoding="utf-8",
    )
    print(f"✅ Created Maya module file: {mod_file}")


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
echo This will create the 'auroraview' shelf with an Outliner button.
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
echo   2. Look for the 'auroraview' shelf
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

    # PowerShell script
    install_ps1 = package_dir / "install.ps1"
    install_ps1.write_text(
        f"""# AuroraView Maya Outliner Installer v{version}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AuroraView Maya Outliner Installer v{version}" -ForegroundColor Cyan
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

# Update module path in mod file (replace ' ./' with actual path)
$content = Get-Content $modFile -Raw
$content = $content -replace ' \\./', " $scriptDir"
$content | Set-Content $modFile -NoNewline

Write-Host ""

# Ask user if they want to install userSetup.py
Write-Host "Do you want to install userSetup.py for auto-loading?" -ForegroundColor Yellow
Write-Host "This will create the 'auroraview' shelf with an Outliner button." -ForegroundColor White
Write-Host ""
$installUserSetup = Read-Host "Install userSetup.py? (Y/N)"

if ($installUserSetup -eq "Y" -or $installUserSetup -eq "y") {{
    Write-Host ""
    Write-Host "Available Maya versions:" -ForegroundColor Cyan
    Write-Host "  1. Maya 2022" -ForegroundColor White
    Write-Host "  2. Maya 2024" -ForegroundColor White
    Write-Host "  3. Maya 2025" -ForegroundColor White
    Write-Host ""
    $mayaVersion = Read-Host "Select Maya version (1-3)"

    $mayaScriptsDir = $null
    switch ($mayaVersion) {{
        "1" {{ $mayaScriptsDir = Join-Path $env:USERPROFILE "Documents\\maya\\2022\\scripts" }}
        "2" {{ $mayaScriptsDir = Join-Path $env:USERPROFILE "Documents\\maya\\2024\\scripts" }}
        "3" {{ $mayaScriptsDir = Join-Path $env:USERPROFILE "Documents\\maya\\2025\\scripts" }}
    }}

    if ($mayaScriptsDir) {{
        if (-not (Test-Path $mayaScriptsDir)) {{
            Write-Host "Creating Maya scripts directory..." -ForegroundColor Yellow
            New-Item -ItemType Directory -Path $mayaScriptsDir -Force | Out-Null
        }}
        $userSetupSrc = Join-Path $scriptDir "scripts\\userSetup.py"
        $userSetupDst = Join-Path $mayaScriptsDir "userSetup.py"
        Copy-Item -Path $userSetupSrc -Destination $userSetupDst -Force
        Write-Host "userSetup.py installed to: $mayaScriptsDir" -ForegroundColor Green
    }} else {{
        Write-Host "Invalid selection. Skipping userSetup.py installation." -ForegroundColor Yellow
    }}
}}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Module file installed at:" -ForegroundColor White
Write-Host "  $modFile" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Restart Maya" -ForegroundColor White
Write-Host "  2. Look for the 'auroraview' shelf" -ForegroundColor White
Write-Host "  3. Click the 'Outliner' button to launch" -ForegroundColor White
Write-Host ""
Write-Host "Or run manually in Script Editor:" -ForegroundColor Cyan
Write-Host "  from auroraview_maya_outliner import main" -ForegroundColor White
Write-Host "  main()" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
""",
        encoding="utf-8",
    )

    print("✅ Created installation scripts")


def create_usersetup(scripts_dir: Path) -> None:
    """Create userSetup.py for auto-loading with shelf button.

    The shelf name is 'auroraview' (lowercase) for consistency.
    """
    scripts_dir.mkdir(parents=True, exist_ok=True)
    usersetup_file = scripts_dir / "userSetup.py"
    usersetup_content = f'''"""
Maya userSetup.py for AuroraView Outliner

This file is automatically installed by the installer.
It creates the '{SHELF_NAME}' shelf with an Outliner button when Maya starts.

Manual installation:
- Windows: C:/Users/<username>/Documents/maya/<version>/scripts/userSetup.py
- macOS: ~/Library/Preferences/Autodesk/maya/<version>/scripts/userSetup.py
- Linux: ~/maya/<version>/scripts/userSetup.py
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
'''
    usersetup_file.write_text(usersetup_content, encoding="utf-8")
    print("✅ Created userSetup.py")


def build_package(version: str, skip_vendor: bool = False) -> Path:
    """Build the Maya Outliner package.

    Args:
        version: Version string for the package
        skip_vendor: Skip downloading vendor packages (for faster testing)

    Returns:
        Path to the created zip file
    """
    print(f"📦 Creating Maya Outliner package v{version}")
    print(f"   Shelf name: {SHELF_NAME}")

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

    # 3. Download vendor packages (third-party dependencies)
    if not skip_vendor:
        print("📦 Downloading vendor packages...")
        vendor_dir = package_dir / "vendor"
        download_vendor_packages(vendor_dir)
    else:
        print("⏭️  Skipping vendor packages (--skip-vendor)")

    # 4. Create scripts directory with userSetup.py
    print("📝 Creating userSetup.py...")
    scripts_dir = package_dir / "scripts"
    create_usersetup(scripts_dir)

    # 5. Create installation scripts
    print("📝 Creating installation scripts...")
    create_install_scripts(package_dir, version)

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
        for root, _dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(BUILD_DIR)
                zipf.write(file_path, arcname)

    print(f"✅ Package created: {zip_path}")
    print(f"📦 Size: {zip_path.stat().st_size / 1024 / 1024:.2f} MB")

    return zip_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build Maya Outliner package with bundled dependencies"
    )
    parser.add_argument("--version", default="0.1.0", help="Version for the package")
    parser.add_argument(
        "--skip-vendor",
        action="store_true",
        help="Skip downloading vendor packages (for faster testing)",
    )
    args = parser.parse_args()

    try:
        zip_path = build_package(args.version, skip_vendor=args.skip_vendor)
        print()
        print("=" * 60)
        print("✅ Build Complete!")
        print("=" * 60)
        print(f"Package: {zip_path}")
        print()
        print("Package contents:")
        print("  📁 dist/           - Built frontend files")
        print("  📁 auroraview_maya_outliner/ - Maya integration code")
        print("  📁 vendor/         - Third-party dependencies (auroraview)")
        print("  📁 scripts/        - userSetup.py for auto-loading")
        print("  📄 maya-outliner.mod - Maya module file")
        print("  📄 install.bat/ps1 - Installation scripts")
        print()
        print("To install:")
        print("  1. Extract the zip file")
        print("  2. Run install.bat (Windows) or install.ps1 (PowerShell)")
        print("  3. Follow the prompts to install userSetup.py")
        print("  4. Restart Maya")
        print(f"  5. Look for the '{SHELF_NAME}' shelf and click 'Outliner'")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())


