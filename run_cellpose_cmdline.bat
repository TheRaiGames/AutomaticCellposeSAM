@echo off
REM Command Line Version of Automated Cellpose Segmentation
REM Usage: run_cellpose_cmdline.bat [input_folder] [output_folder]

echo ============================================================
echo Automated Cellpose Segmentation (Command Line)
echo ============================================================
echo.

REM Check arguments
if "%~1"=="" (
    echo Usage: %0 [input_folder] [output_folder]
    echo.
    echo Example: %0 "C:\Images\Input" "C:\Images\Output"
    echo.
    echo For GUI version, use: run_automated_cellpose.bat
    pause
    exit /b 1
)

if "%~2"=="" (
    echo Usage: %0 [input_folder] [output_folder]
    echo.
    echo Example: %0 "C:\Images\Input" "C:\Images\Output"
    echo.
    echo For GUI version, use: run_automated_cellpose.bat
    pause
    exit /b 1
)

set INPUT_FOLDER=%~1
set OUTPUT_FOLDER=%~2

echo Input folder: %INPUT_FOLDER%
echo Output folder: %OUTPUT_FOLDER%
echo.

REM Check if input folder exists
if not exist "%INPUT_FOLDER%" (
    echo Error: Input folder does not exist: %INPUT_FOLDER%
    pause
    exit /b 1
)

REM Check for Windows App Store Python 3.13 first
where python3.13.exe >nul 2>nul
if not errorlevel 1 (
    echo Using Windows App Store Python 3.13
    set PYTHON_CMD=python3.13.exe
) else (
    REM Try generic python.exe as fallback
    where python.exe >nul 2>nul
    if not errorlevel 1 (
        echo Using python.exe as fallback
        set PYTHON_CMD=python.exe
    ) else (
        echo Error: Python executable not found
        pause
        exit /b 1
    )
)

REM Check if the Python script exists
if not exist "automated_cellpose_segmentation.py" (
    echo Error: automated_cellpose_segmentation.py not found
    pause
    exit /b 1
)

echo Starting batch processing...
echo.

REM Run the Python script with specified folders
%PYTHON_CMD% automated_cellpose_segmentation.py --input "%INPUT_FOLDER%" --output "%OUTPUT_FOLDER%" --model cpsam

REM Check if the script ran successfully
if errorlevel 1 (
    echo.
    echo Error: Segmentation process failed
) else (
    echo.
    echo Segmentation process completed successfully!
)

echo.
pause