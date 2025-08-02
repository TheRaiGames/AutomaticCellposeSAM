@echo off
REM Enhanced Automated Cellpose Segmentation Launcher
REM This batch file starts the enhanced GUI with progress bar and output selection
REM 
REM Author: Developed using Python with Cursor and Claude-4-Sonnet AI assistant
REM Based on: Cellpose by Stringer et al. (https://github.com/MouseLand/cellpose)

echo ============================================================
echo Enhanced Automated Cellpose Segmentation
echo ============================================================

REM Check for Windows App Store Python 3.13 first
echo Checking for Python 3.13...
where python3.13.exe >nul 2>nul
if not errorlevel 1 (
    echo Found Windows App Store Python 3.13
    set PYTHON_CMD=python3.13.exe
    python3.13.exe --version
) else (
    REM Try generic python.exe as fallback
    where python.exe >nul 2>nul
    if not errorlevel 1 (
        echo Using python.exe as fallback
        set PYTHON_CMD=python.exe
        python.exe --version
    ) else (
        echo Error: Python executable not found
        echo Please ensure Python 3.13 is installed from Windows Store or python.org
        pause
        exit /b 1
    )
)

echo.
echo Starting Enhanced Cellpose Segmentation GUI...
echo Features:
echo - Interactive folder selection
echo - Selectable output file types
echo - Real-time progress tracking
echo - Detailed processing logs
echo.

REM Launch the enhanced GUI
%PYTHON_CMD% automated_cellpose_enhanced_gui.py

REM Check if the script executed successfully
if errorlevel 1 (
    echo.
    echo Error: Failed to start the enhanced GUI
    echo Please check the error messages above.
    echo.
    echo Common solutions:
    echo 1. Install required packages: pip install cellpose[gui] tifffile pillow
    echo 2. Ensure all dependencies are properly installed
    echo 3. Check that your GPU drivers are up to date (for CUDA support)
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo Enhanced GUI closed successfully.
)

pause