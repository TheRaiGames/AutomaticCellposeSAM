@echo off
REM Quick Start Guide for Automated Cellpose Segmentation

echo ============================================================
echo Quick Start Guide - Automated Cellpose Segmentation
echo ============================================================
echo.

echo Step 1: Test your installation
echo ------------------------------
echo Testing system compatibility...

REM Check for Windows App Store Python 3.13 first
where python3.13.exe >nul 2>nul
if not errorlevel 1 (
    echo Using Windows App Store Python 3.13
    python3.13.exe test_installation.py
) else (
    REM Try generic python.exe as fallback
    where python.exe >nul 2>nul
    if not errorlevel 1 (
        echo Using python.exe as fallback
        python.exe test_installation.py
    ) else (
        echo Error: Python executable not found
        pause
        exit /b 1
    )
)
if errorlevel 1 (
    echo.
    echo Installation test FAILED. Please fix the issues above.
    echo Run setup_environment.bat to install missing dependencies.
    pause
    exit /b 1
)

echo.
echo Step 2: Check for example images
echo --------------------------------
if not exist "example_images\*.tif" (
    echo No .tif files found in example_images folder.
    echo.
    echo Please:
    echo 1. Copy your .tif images to the example_images folder
    echo 2. Or use run_automated_cellpose.bat to select a different folder
    echo.
) else (
    echo ✓ Found .tif files in example_images folder
)

echo.
echo Step 3: Choose how to run
echo -------------------------
echo Select an option:
echo.
echo 1. GUI Mode (Recommended) - Select folders with file browser
echo 2. Command Line - Process example_images folder
echo 3. Setup Environment - Install/update dependencies
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting GUI mode...
    call run_automated_cellpose.bat
) else if "%choice%"=="2" (
    echo.
    echo Starting command line processing...
    call run_cellpose_cmdline.bat "example_images" "output_flows"
) else if "%choice%"=="3" (
    echo.
    echo Starting environment setup...
    call setup_environment.bat
) else if "%choice%"=="4" (
    echo.
    echo Goodbye!
    exit /b 0
) else (
    echo.
    echo Invalid choice. Please run the script again.
    pause
    exit /b 1
)

echo.
pause