@echo off
REM Automated Cellpose Segmentation Batch File
REM Compatible with Python 3.13.5 and Cellpose 4.0.4

echo ============================================================
echo Automated Cellpose Segmentation System
echo ============================================================
echo.

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

REM Check if the Python script exists
if not exist "automated_cellpose_segmentation.py" (
    echo Error: automated_cellpose_segmentation.py not found
    echo Please ensure the script is in the same directory as this batch file
    pause
    exit /b 1
)

echo.
echo Starting Automated Cellpose Segmentation...
echo You will be prompted to select input and output folders.
echo.

REM Run the Python script with GUI mode
%PYTHON_CMD% automated_cellpose_segmentation.py --gui

REM Check if the script ran successfully
if errorlevel 1 (
    echo.
    echo Error: Segmentation process failed
    echo Please check the error messages above
) else (
    echo.
    echo Segmentation process completed successfully!
)

echo.
pause