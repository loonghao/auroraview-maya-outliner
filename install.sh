#!/bin/bash
# AuroraView Maya Outliner Installer (Development Version)
# This script installs the Maya Outliner to your Maya modules directory

echo "========================================"
echo "Maya Outliner Installer (Dev)"
echo "========================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAYA_MODULES_DIR="$HOME/maya/modules"
MOD_FILE="$MAYA_MODULES_DIR/maya-outliner.mod"

# Check if dist directory exists
if [ ! -f "$SCRIPT_DIR/dist/index.html" ]; then
    echo "ERROR: dist/index.html not found!"
    echo "Please run: npm run build"
    echo ""
    read -p "Press Enter to exit"
    exit 1
fi

# Create modules directory if it doesn't exist
if [ ! -d "$MAYA_MODULES_DIR" ]; then
    echo "Creating Maya modules directory..."
    mkdir -p "$MAYA_MODULES_DIR"
fi

# Create .mod file pointing to current directory
# Note: PYTHONPATH should point to the module root (not auroraview_maya_outliner subdirectory)
# so that `from auroraview_maya_outliner import xxx` works correctly
echo "Creating module file..."
cat > "$MOD_FILE" << EOF
+ maya-outliner dev $SCRIPT_DIR
PYTHONPATH +:= .
EOF

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Module file created at:"
echo "$MOD_FILE"
echo ""
echo "Module points to:"
echo "$SCRIPT_DIR"
echo ""
echo "To use Maya Outliner:"
echo "1. Restart Maya"
echo "2. In Script Editor, run:"
echo "   from auroraview_maya_outliner import main"
echo "   main()"
echo ""
echo "For production mode, set environment variable:"
echo "   export AURORAVIEW_ENV=production"
echo ""
echo "For development mode (default):"
echo "   Make sure Vite dev server is running: npm run dev"
echo ""
read -p "Press Enter to exit"

