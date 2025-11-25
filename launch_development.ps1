# Launch Maya Outliner in Development Mode
# This script sets AURORAVIEW_ENV to development and launches Maya

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Maya Outliner - Development Mode" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variable for development mode
$env:AURORAVIEW_ENV = "development"

Write-Host "Environment: DEVELOPMENT" -ForegroundColor Green
Write-Host "Using Vite dev server at http://localhost:5173" -ForegroundColor Green
Write-Host ""

# Check if dev server is running
Write-Host "Checking if Vite dev server is running..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
    Write-Host "Vite dev server is running - OK" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Vite dev server not detected!" -ForegroundColor Yellow
    Write-Host "Please run in another terminal: npm run dev" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press Enter to continue anyway..." -ForegroundColor Yellow
    Read-Host
}

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

