# Setup Maya environment script
# Usage: .\setup-maya-env.ps1 -Version "2024" -ProjectRoot "C:\path\to\project"

param(
    [Parameter(Mandatory=$true)]
    [string]$Version,
    
    [Parameter(Mandatory=$true)]
    [string]$ProjectRoot
)

$ErrorActionPreference = "Stop"

Write-Host "Setting up Maya $Version environment..."

# Create scripts directory if it doesn't exist
$scriptsDir = "$env:USERPROFILE\Documents\maya\$Version\scripts"
if (-not (Test-Path $scriptsDir)) {
    New-Item -ItemType Directory -Path $scriptsDir -Force | Out-Null
    Write-Host "Created directory: $scriptsDir"
}

# Read userSetup.py template
$userSetupFile = Join-Path $ProjectRoot "userSetup.py"
if (-not (Test-Path $userSetupFile)) {
    Write-Error "userSetup.py not found at: $userSetupFile"
    exit 1
}

$content = Get-Content $userSetupFile -Raw

# Replace {{PROJECT_ROOT}} placeholder with actual path
$content = $content -replace '\{\{PROJECT_ROOT\}\}', $ProjectRoot

# Write to Maya scripts folder
$destFile = Join-Path $scriptsDir "userSetup.py"
$content | Set-Content $destFile -NoNewline

Write-Host "✓ Copied userSetup.py to Maya $Version scripts folder"
Write-Host "✓ Set PROJECT_ROOT to: $ProjectRoot"

