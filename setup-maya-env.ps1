# Setup Maya environment for AuroraView Outliner
# Usage: .\setup-maya-env.ps1 -Version "2024" -ProjectRoot "C:\path\to\project" [-UseLocal]

param(
    [Parameter(Mandatory=$true)]
    [string]$Version,

    [Parameter(Mandatory=$true)]
    [string]$ProjectRoot,

    [switch]$UseLocal
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting up Maya $Version environment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Clean up previously installed .mod files that may conflict with local development
$mayaModulesDir = Join-Path $env:USERPROFILE "Documents\maya\modules"
$modFilesToClean = @("auroraview.mod", "maya-outliner.mod")

Write-Host "Checking for conflicting .mod files..." -ForegroundColor Yellow
foreach ($modFile in $modFilesToClean) {
    $modPath = Join-Path $mayaModulesDir $modFile
    if (Test-Path $modPath) {
        Remove-Item $modPath -Force
        Write-Host "  Removed: $modPath" -ForegroundColor Green
    }
}
Write-Host ""

# Paths
$mayaScriptsDir = Join-Path $env:USERPROFILE "Documents\maya\$Version\scripts"
$userSetupDest = Join-Path $mayaScriptsDir "userSetup.py"
$userSetupSrc = Join-Path $ProjectRoot "userSetup.py"

# Create scripts directory if it doesn't exist
if (-not (Test-Path $mayaScriptsDir)) {
    Write-Host "Creating Maya scripts directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $mayaScriptsDir -Force | Out-Null
}

# Read and process userSetup.py
if (-not (Test-Path $userSetupSrc)) {
    Write-Host "ERROR: userSetup.py not found at: $userSetupSrc" -ForegroundColor Red
    exit 1
}

Write-Host "Processing userSetup.py..." -ForegroundColor Green

# Read the template and replace placeholder
$content = Get-Content $userSetupSrc -Raw
$content = $content -replace '\{\{PROJECT_ROOT\}\}', $ProjectRoot

# Write to Maya scripts directory
$content | Out-File -FilePath $userSetupDest -Encoding utf8 -NoNewline

Write-Host "  Source: $userSetupSrc" -ForegroundColor White
Write-Host "  Destination: $userSetupDest" -ForegroundColor White

# Set environment variables based on mode
$envMode = "development"

if ($UseLocal) {
    $envMode = "production"
    Write-Host ""
    Write-Host "Setting AURORAVIEW_ENV=production for local mode..." -ForegroundColor Yellow
    [System.Environment]::SetEnvironmentVariable("AURORAVIEW_ENV", "production", "User")
    $env:AURORAVIEW_ENV = "production"
} else {
    Write-Host ""
    Write-Host "Setting AURORAVIEW_ENV=development for dev server mode..." -ForegroundColor Yellow
    [System.Environment]::SetEnvironmentVariable("AURORAVIEW_ENV", "development", "User")
    $env:AURORAVIEW_ENV = "development"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "userSetup.py installed to: $userSetupDest" -ForegroundColor White
Write-Host "Environment: $envMode" -ForegroundColor White
Write-Host ""

