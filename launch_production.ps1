# Launch Maya Outliner in Production Mode
# This script sets AURORAVIEW_ENV to production and launches Maya

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Maya Outliner - Production Mode" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variable for production mode
$env:AURORAVIEW_ENV = "production"

Write-Host "Environment: PRODUCTION" -ForegroundColor Green
Write-Host "Using static files from dist/" -ForegroundColor Green
Write-Host ""

# Check if dist directory exists
if (-not (Test-Path "dist\index.html")) {
    Write-Host "ERROR: dist/index.html not found!" -ForegroundColor Red
    Write-Host "Please run: npm run build" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "dist/index.html found - OK" -ForegroundColor Green
Write-Host ""

# Launch Maya (adjust path for your Maya version)
$mayaPath = "C:\Program Files\Autodesk\Maya2024\bin\maya.exe"

if (Test-Path $mayaPath) {
    Write-Host "Launching Maya 2024..." -ForegroundColor Cyan
    Start-Process $mayaPath
} else {
    Write-Host "WARNING: Maya 2024 not found at: $mayaPath" -ForegroundColor Yellow
    Write-Host "Please update `$mayaPath in this script" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to continue"
}

Write-Host ""
Write-Host "To use the outliner in Maya, run:" -ForegroundColor Cyan
Write-Host "  from maya_integration import main" -ForegroundColor White
Write-Host "  main()" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"

