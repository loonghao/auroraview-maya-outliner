# AuroraView Maya Outliner - Just Commands
# https://github.com/casey/just

# Default Maya installation paths
MAYA_2022_PATH := "C:/Program Files/Autodesk/Maya2022/bin/maya.exe"
MAYA_2024_PATH := "C:/Program Files/Autodesk/Maya2024/bin/maya.exe"
MAYA_2025_PATH := "C:/Program Files/Autodesk/Maya2025/bin/maya.exe"

# Project paths
PROJECT_ROOT := justfile_directory()
USERSETUP_FILE := PROJECT_ROOT / "userSetup.py"

# Default recipe - show available commands
default:
    @just --list

# Install frontend dependencies
install:
    npm install

# Start Vite dev server
dev:
    npm run dev

# Build frontend for production
build:
    npm run build

# Setup Maya environment and copy userSetup.py with PROJECT_ROOT replacement
[private]
setup-maya-env version:
    @echo "Setting up Maya {{version}} environment..."
    @if not exist "%USERPROFILE%\Documents\maya\{{version}}\scripts" mkdir "%USERPROFILE%\Documents\maya\{{version}}\scripts"
    @powershell -Command "(Get-Content '{{USERSETUP_FILE}}') -replace '{{{{PROJECT_ROOT}}}}', '{{PROJECT_ROOT}}' | Set-Content '%USERPROFILE%\Documents\maya\{{version}}\scripts\userSetup.py'"
    @echo "✓ Copied userSetup.py to Maya {{version}} scripts folder"
    @echo "✓ Set PROJECT_ROOT to: {{PROJECT_ROOT}}"

# Launch Maya 2022 with AuroraView Outliner
maya-2022: (setup-maya-env "2022")
    @echo "Launching Maya 2022..."
    @if exist "{{MAYA_2022_PATH}}" ( \
        start "" "{{MAYA_2022_PATH}}" \
    ) else ( \
        echo "ERROR: Maya 2022 not found at {{MAYA_2022_PATH}}" && \
        echo "Please update MAYA_2022_PATH in justfile" && \
        exit 1 \
    )

# Launch Maya 2024 with AuroraView Outliner
maya-2024: (setup-maya-env "2024")
    @echo "Launching Maya 2024..."
    @if exist "{{MAYA_2024_PATH}}" ( \
        start "" "{{MAYA_2024_PATH}}" \
    ) else ( \
        echo "ERROR: Maya 2024 not found at {{MAYA_2024_PATH}}" && \
        echo "Please update MAYA_2024_PATH in justfile" && \
        exit 1 \
    )

# Launch Maya 2025 with AuroraView Outliner
maya-2025: (setup-maya-env "2025")
    @echo "Launching Maya 2025..."
    @if exist "{{MAYA_2025_PATH}}" ( \
        start "" "{{MAYA_2025_PATH}}" \
    ) else ( \
        echo "ERROR: Maya 2025 not found at {{MAYA_2025_PATH}}" && \
        echo "Please update MAYA_2025_PATH in justfile" && \
        exit 1 \
    )

# Clean Maya environment (remove userSetup.py)
clean-maya version:
    @echo "Cleaning Maya {{version}} environment..."
    @if exist "%USERPROFILE%\Documents\maya\{{version}}\scripts\userSetup.py" ( \
        del "%USERPROFILE%\Documents\maya\{{version}}\scripts\userSetup.py" && \
        echo "✓ Removed userSetup.py from Maya {{version}}" \
    ) else ( \
        echo "No userSetup.py found in Maya {{version}}" \
    )

# Clean all Maya versions
clean-all-maya:
    @just clean-maya 2022
    @just clean-maya 2024
    @just clean-maya 2025

# Show Maya environment info
info:
    @echo "=== AuroraView Maya Outliner ==="
    @echo "Project Root: {{PROJECT_ROOT}}"
    @echo "UserSetup File: {{USERSETUP_FILE}}"
    @echo ""
    @echo "=== Maya Installations ==="
    @if exist "{{MAYA_2022_PATH}}" (echo "✓ Maya 2022: {{MAYA_2022_PATH}}") else (echo "✗ Maya 2022: Not found")
    @if exist "{{MAYA_2024_PATH}}" (echo "✓ Maya 2024: {{MAYA_2024_PATH}}") else (echo "✗ Maya 2024: Not found")
    @if exist "{{MAYA_2025_PATH}}" (echo "✓ Maya 2025: {{MAYA_2025_PATH}}") else (echo "✗ Maya 2025: Not found")
    @echo ""
    @echo "=== UserSetup Status ==="
    @if exist "%USERPROFILE%\Documents\maya\2022\scripts\userSetup.py" (echo "✓ Maya 2022: Installed") else (echo "✗ Maya 2022: Not installed")
    @if exist "%USERPROFILE%\Documents\maya\2024\scripts\userSetup.py" (echo "✓ Maya 2024: Installed") else (echo "✗ Maya 2024: Not installed")
    @if exist "%USERPROFILE%\Documents\maya\2025\scripts\userSetup.py" (echo "✓ Maya 2025: Installed") else (echo "✗ Maya 2025: Not installed")

