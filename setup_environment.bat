@echo off
REM Setup script for Automated Cellpose Segmentation Environment
REM This script helps install the required dependencies

echo ============================================================
echo Cellpose Environment Setup
echo ============================================================
echo.

REM Check for Windows App Store Python 3.13 first
where python3.13.exe >nul 2>nul
if not errorlevel 1 (
    echo Found Windows App Store Python 3.13
    set PYTHON_CMD=python3.13.exe
    set PIP_CMD=python3.13.exe -m pip
    python3.13.exe --version
    python3.13.exe -c "import sys; print(f'Python version: {sys.version}')"
) else (
    REM Try generic python.exe as fallback
    where python.exe >nul 2>nul
    if not errorlevel 1 (
        echo Using python.exe as fallback
        set PYTHON_CMD=python.exe
        set PIP_CMD=pip
        python.exe --version
        python.exe -c "import sys; print(f'Python version: {sys.version}')"
    ) else (
        echo Error: Python not found
        echo Please install Python 3.13 from Windows Store or https://python.org
        pause
        exit /b 1
    )
)
echo.

REM Check if pip is available
%PIP_CMD% --version 2>nul
if errorlevel 1 (
    echo Error: pip not found
    echo Please ensure pip is available with Python
    pause
    exit /b 1
)

echo Installing/Upgrading required packages...
echo.

REM Install Cellpose
echo Installing Cellpose 4.0.6+...
%PIP_CMD% install cellpose

REM Install GUI dependencies
echo.
echo Installing GUI dependencies...
%PIP_CMD% install "cellpose[gui]"

REM Install PyTorch with CUDA support (for GPU acceleration)
echo.
echo Installing PyTorch with CUDA support...
%PIP_CMD% install torch torchvision --index-url https://download.pytorch.org/whl/cu118

echo.
echo ============================================================
echo Installation completed!
echo ============================================================
echo.

REM Test the installation
echo Testing Cellpose installation...
%PYTHON_CMD% -c "import cellpose; print('Cellpose installed successfully')"

echo.
echo Testing PyTorch CUDA...
%PYTHON_CMD% -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"

echo.
echo Setup complete! You can now run the automated segmentation.
echo Use: run_automated_cellpose.bat (GUI) or run_cellpose_cmdline.bat (command line)
echo.
pause