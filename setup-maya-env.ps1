# Setup Maya environment script
# Usage: .\setup-maya-env.ps1 -Version "2024" -ProjectRoot "C:\path\to\project" [-UseLocal]

param(
    [Parameter(Mandatory=$true)]
    [string]$Version,

    [Parameter(Mandatory=$true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory=$false)]
    [switch]$UseLocal = $false
)

$ErrorActionPreference = "Stop"

if ($UseLocal) {
    Write-Host "Setting up Maya $Version environment (LOCAL DEVELOPMENT MODE)..."
} else {
    Write-Host "Setting up Maya $Version environment..."
}

# Create scripts directory if it doesn't exist
$scriptsDir = "$env:USERPROFILE\Documents\maya\$Version\scripts"
if (-not (Test-Path $scriptsDir)) {
    New-Item -ItemType Directory -Path $scriptsDir -Force | Out-Null
    Write-Host "Created directory: $scriptsDir"
}

# Choose which userSetup.py to use
if ($UseLocal) {
    $userSetupFile = Join-Path $ProjectRoot "userSetup.local.py"
    if (-not (Test-Path $userSetupFile)) {
        Write-Error "userSetup.local.py not found at: $userSetupFile"
        Write-Host "Please create userSetup.local.py for local development"
        exit 1
    }
} else {
    $userSetupFile = Join-Path $ProjectRoot "userSetup.py"
    if (-not (Test-Path $userSetupFile)) {
        Write-Error "userSetup.py not found at: $userSetupFile"
        exit 1
    }
}

$content = Get-Content $userSetupFile -Raw

# Replace {{PROJECT_ROOT}} placeholder with actual path
$content = $content -replace '\{\{PROJECT_ROOT\}\}', $ProjectRoot

# Write to Maya scripts folder
$destFile = Join-Path $scriptsDir "userSetup.py"
$content | Set-Content $destFile -NoNewline

if ($UseLocal) {
    Write-Host "✓ Copied userSetup.local.py to Maya $Version scripts folder"
    Write-Host "✓ Set PROJECT_ROOT to: $ProjectRoot"
    Write-Host "✓ Using LOCAL development version of auroraview"
} else {
    Write-Host "✓ Copied userSetup.py to Maya $Version scripts folder"
    Write-Host "✓ Set PROJECT_ROOT to: $ProjectRoot"
}

