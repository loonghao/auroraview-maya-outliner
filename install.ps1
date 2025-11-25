# AuroraView Maya Outliner Installer (Development Version)
# This script installs the Maya Outliner to your Maya modules directory

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Maya Outliner Installer (Dev)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$mayaModulesDir = Join-Path $env:USERPROFILE "Documents\maya\modules"
$modFile = Join-Path $mayaModulesDir "maya-outliner.mod"

# Check if dist directory exists
$distIndex = Join-Path $scriptDir "dist\index.html"
if (-not (Test-Path $distIndex)) {
    Write-Host "ERROR: dist/index.html not found!" -ForegroundColor Red
    Write-Host "Please run: npm run build" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Create modules directory if it doesn't exist
if (-not (Test-Path $mayaModulesDir)) {
    Write-Host "Creating Maya modules directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $mayaModulesDir | Out-Null
}

# Create .mod file pointing to current directory
Write-Host "Creating module file..." -ForegroundColor Green
@"
+ maya-outliner dev $scriptDir
PYTHONPATH +:= auroraview_maya_outliner
"@ | Out-File -FilePath $modFile -Encoding utf8

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Module file created at:" -ForegroundColor White
Write-Host $modFile -ForegroundColor Yellow
Write-Host ""
Write-Host "Module points to:" -ForegroundColor White
Write-Host $scriptDir -ForegroundColor Yellow
Write-Host ""
Write-Host "To use Maya Outliner:" -ForegroundColor White
Write-Host "1. Restart Maya" -ForegroundColor White
Write-Host "2. In Script Editor, run:" -ForegroundColor White
Write-Host "   from auroraview_maya_outliner import main" -ForegroundColor Cyan
Write-Host "   main()" -ForegroundColor Cyan
Write-Host ""
Write-Host "For production mode, set environment variable:" -ForegroundColor White
Write-Host "   `$env:AURORAVIEW_ENV='production'" -ForegroundColor Yellow
Write-Host ""
Write-Host "For development mode (default):" -ForegroundColor White
Write-Host "   Make sure Vite dev server is running: npm run dev" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"

