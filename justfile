# AuroraView Maya Outliner - Just Commands
# https://github.com/casey/just

# Use PowerShell on Windows
set shell := ["powershell.exe", "-NoLogo", "-Command"]

# Default Maya installation paths
MAYA_2022_PATH := "C:/Program Files/Autodesk/Maya2022/bin/maya.exe"
MAYA_2024_PATH := "C:/Program Files/Autodesk/Maya2024/bin/maya.exe"
MAYA_2025_PATH := "C:/Program Files/Autodesk/Maya2025/bin/maya.exe"

# Project paths
PROJECT_ROOT := justfile_directory()
USERSETUP_FILE := PROJECT_ROOT + "\\userSetup.py"

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
    @powershell -NoLogo -ExecutionPolicy Bypass -File "{{PROJECT_ROOT}}\setup-maya-env.ps1" -Version "{{version}}" -ProjectRoot "{{PROJECT_ROOT}}"

# Setup Maya environment with local development version
[private]
setup-maya-env-local version:
    @powershell -NoLogo -ExecutionPolicy Bypass -File "{{PROJECT_ROOT}}\setup-maya-env.ps1" -Version "{{version}}" -ProjectRoot "{{PROJECT_ROOT}}" -UseLocal

# Launch Maya 2022 with AuroraView Outliner
maya-2022: (setup-maya-env "2022")
    @Write-Host "Launching Maya 2022..."
    @if (Test-Path "{{MAYA_2022_PATH}}") { Start-Process "{{MAYA_2022_PATH}}" } else { Write-Host "ERROR: Maya 2022 not found at {{MAYA_2022_PATH}}"; Write-Host "Please update MAYA_2022_PATH in justfile"; exit 1 }

# Launch Maya 2024 with AuroraView Outliner
maya-2024: (setup-maya-env "2024")
    @Write-Host "Launching Maya 2024..."
    @if (Test-Path "{{MAYA_2024_PATH}}") { Start-Process "{{MAYA_2024_PATH}}" } else { Write-Host "ERROR: Maya 2024 not found at {{MAYA_2024_PATH}}"; Write-Host "Please update MAYA_2024_PATH in justfile"; exit 1 }

# Launch Maya 2025 with AuroraView Outliner
maya-2025: (setup-maya-env "2025")
    @Write-Host "Launching Maya 2025..."
    @if (Test-Path "{{MAYA_2025_PATH}}") { Start-Process "{{MAYA_2025_PATH}}" } else { Write-Host "ERROR: Maya 2025 not found at {{MAYA_2025_PATH}}"; Write-Host "Please update MAYA_2025_PATH in justfile"; exit 1 }

# Launch Maya 2022 with LOCAL development version
maya-2022-local: (setup-maya-env-local "2022")
    @Write-Host "Launching Maya 2022 (LOCAL DEV)..."
    @if (Test-Path "{{MAYA_2022_PATH}}") { Start-Process "{{MAYA_2022_PATH}}" } else { Write-Host "ERROR: Maya 2022 not found at {{MAYA_2022_PATH}}"; Write-Host "Please update MAYA_2022_PATH in justfile"; exit 1 }

# Launch Maya 2024 with LOCAL development version
maya-2024-local: (setup-maya-env-local "2024")
    @Write-Host "Launching Maya 2024 (LOCAL DEV)..."
    @if (Test-Path "{{MAYA_2024_PATH}}") { Start-Process "{{MAYA_2024_PATH}}" } else { Write-Host "ERROR: Maya 2024 not found at {{MAYA_2024_PATH}}"; Write-Host "Please update MAYA_2024_PATH in justfile"; exit 1 }

# Launch Maya 2025 with LOCAL development version
maya-2025-local: (setup-maya-env-local "2025")
    @Write-Host "Launching Maya 2025 (LOCAL DEV)..."
    @if (Test-Path "{{MAYA_2025_PATH}}") { Start-Process "{{MAYA_2025_PATH}}" } else { Write-Host "ERROR: Maya 2025 not found at {{MAYA_2025_PATH}}"; Write-Host "Please update MAYA_2025_PATH in justfile"; exit 1 }

# Clean Maya environment (remove userSetup.py)
clean-maya version:
    @Write-Host "Cleaning Maya {{version}} environment..."
    @$userSetupPath = "$env:USERPROFILE\Documents\maya\{{version}}\scripts\userSetup.py"; if (Test-Path $userSetupPath) { Remove-Item $userSetupPath; Write-Host "✓ Removed userSetup.py from Maya {{version}}" } else { Write-Host "No userSetup.py found in Maya {{version}}" }

# Clean all Maya versions
clean-all-maya:
    @just clean-maya 2022
    @just clean-maya 2024
    @just clean-maya 2025

# Show Maya environment info
info:
    @Write-Host "=== AuroraView Maya Outliner ==="
    @Write-Host "Project Root: {{PROJECT_ROOT}}"
    @Write-Host "UserSetup File: {{USERSETUP_FILE}}"
    @Write-Host ""
    @Write-Host "=== Maya Installations ==="
    @if (Test-Path "{{MAYA_2022_PATH}}") { Write-Host "✓ Maya 2022: {{MAYA_2022_PATH}}" } else { Write-Host "✗ Maya 2022: Not found" }
    @if (Test-Path "{{MAYA_2024_PATH}}") { Write-Host "✓ Maya 2024: {{MAYA_2024_PATH}}" } else { Write-Host "✗ Maya 2024: Not found" }
    @if (Test-Path "{{MAYA_2025_PATH}}") { Write-Host "✓ Maya 2025: {{MAYA_2025_PATH}}" } else { Write-Host "✗ Maya 2025: Not found" }
    @Write-Host ""
    @Write-Host "=== UserSetup Status ==="
    @if (Test-Path "$env:USERPROFILE\Documents\maya\2022\scripts\userSetup.py") { Write-Host "✓ Maya 2022: Installed" } else { Write-Host "✗ Maya 2022: Not installed" }
    @if (Test-Path "$env:USERPROFILE\Documents\maya\2024\scripts\userSetup.py") { Write-Host "✓ Maya 2024: Installed" } else { Write-Host "✗ Maya 2024: Not installed" }
    @if (Test-Path "$env:USERPROFILE\Documents\maya\2025\scripts\userSetup.py") { Write-Host "✓ Maya 2025: Installed" } else { Write-Host "✗ Maya 2025: Not installed" }

