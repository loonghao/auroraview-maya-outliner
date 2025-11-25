@echo off
REM Launch Maya Outliner in Development Mode
REM This script sets AURORAVIEW_ENV to development and launches Maya

echo ========================================
echo Maya Outliner - Development Mode
echo ========================================
echo.

REM Set environment variable for development mode
set AURORAVIEW_ENV=development

echo Environment: DEVELOPMENT
echo Using Vite dev server at http://localhost:5173
echo.

REM Check if dev server is running
echo Checking if Vite dev server is running...
curl -s http://localhost:5173 >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Vite dev server not detected!
    echo Please run in another terminal: npm run dev
    echo.
    echo Press any key to continue anyway...
    pause >nul
) else (
    echo Vite dev server is running - OK
)

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

