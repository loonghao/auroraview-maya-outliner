@echo off
REM AuroraView Maya Outliner Installer (Development Version)
REM This script installs the Maya Outliner to your Maya modules directory

echo ========================================
echo Maya Outliner Installer (Dev)
echo ========================================
echo.

SET "SCRIPT_DIR=%~dp0"
SET "MAYA_MODULES_DIR=%USERPROFILE%\Documents\maya\modules"
SET "MOD_FILE=%MAYA_MODULES_DIR%\maya-outliner.mod"

REM Check if dist directory exists
if not exist "%SCRIPT_DIR%dist\index.html" (
    echo ERROR: dist/index.html not found!
    echo Please run: npm run build
    echo.
    pause
    exit /b 1
)

REM Create modules directory if it doesn't exist
if not exist "%MAYA_MODULES_DIR%" (
    echo Creating Maya modules directory...
    mkdir "%MAYA_MODULES_DIR%"
)

REM Create .mod file pointing to current directory
echo Creating module file...
echo + maya-outliner dev %SCRIPT_DIR% > "%MOD_FILE%"
echo PYTHONPATH +:= auroraview_maya_outliner >> "%MOD_FILE%"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Module file created at:
echo %MOD_FILE%
echo.
echo Module points to:
echo %SCRIPT_DIR%
echo.
echo To use Maya Outliner:
echo 1. Restart Maya
echo 2. In Script Editor, run:
echo    from auroraview_maya_outliner import main
echo    main()
echo.
echo For production mode, set environment variable:
echo    set AURORAVIEW_ENV=production
echo.
echo For development mode (default):
echo    Make sure Vite dev server is running: npm run dev
echo.
pause

