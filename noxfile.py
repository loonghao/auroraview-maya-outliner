"""Nox sessions for building and packaging Maya Outliner."""

import argparse
import os
import shutil
import zipfile
from pathlib import Path

import nox

from build_utils import create_install_scripts, create_mod_file, create_production_usersetup


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


if __name__ == "__main__":
    # Allow running directly for testing
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        class MockSession:
            posargs = ["--version", "0.1.0-test"]
        make_maya_package(MockSession())

