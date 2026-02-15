@echo off
echo ============================================
echo    AQI Predictor - Windows Setup
echo ============================================
echo.

REM Check if Python is installed
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
python --version
echo.

REM Check if pip is installed
echo [2/4] Checking pip installation...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed
    echo Please install pip or reinstall Python
    pause
    exit /b 1
)
pip --version
echo.

REM Install required packages
echo [3/4] Installing required packages...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install packages
    echo Please check your internet connection and try again
    pause
    exit /b 1
)
echo.

REM Check if model files exist
echo [4/4] Checking model files...
if not exist "best_aqi_model.pkl" (
    echo WARNING: best_aqi_model.pkl not found
    echo The model file should be in the same folder as this script
    echo.
)

if not exist "scaler.pkl" (
    echo WARNING: scaler.pkl not found
    echo The scaler file should be in the same folder as this script
    echo.
)

if exist "best_aqi_model.pkl" (
    echo ✓ Model file found
)

if exist "scaler.pkl" (
    echo ✓ Scaler file found
)

echo.
echo ============================================
echo    Setup Complete!
echo ============================================
echo.
echo To start the application, run:
echo     run.bat
echo.
echo Or manually with:
echo     python app.py
echo.
echo Then open your browser and visit:
echo     http://localhost:5000
echo.
echo IMPORTANT: Make sure to update your WAQI API token in app.py
echo Get your free token from: https://aqicn.org/data-platform/token/
echo.
pause