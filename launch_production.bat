@echo off
REM Launch Maya Outliner in Production Mode
REM This script sets AURORAVIEW_ENV to production and launches Maya

echo ========================================
echo Maya Outliner - Production Mode
echo ========================================
echo.

REM Set environment variable for production mode
set AURORAVIEW_ENV=production

echo Environment: PRODUCTION
echo Using static files from dist/
echo.

REM Check if dist directory exists
if not exist "dist\index.html" (
    echo ERROR: dist/index.html not found!
    echo Please run: npm run build
    echo.
    pause
    exit /b 1
)

echo dist/index.html found - OK
echo.

REM Launch Maya (adjust path for your Maya version)
set MAYA_PATH=C:\Program Files\Autodesk\Maya2024\bin\maya.exe

if exist "%MAYA_PATH%" (
    echo Launching Maya 2024...
    start "" "%MAYA_PATH%"
) else (
    echo WARNING: Maya 2024 not found at: %MAYA_PATH%
    echo Please update MAYA_PATH in this script
    echo.
    pause
)

echo.
echo To use the outliner in Maya, run:
echo   from maya_integration import main
echo   main()
echo.
pause

