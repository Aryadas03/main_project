@echo off
echo ============================================
echo    Starting AQI Predictor
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Check if model files exist
if not exist "best_aqi_model.pkl" (
    echo ERROR: best_aqi_model.pkl not found
    echo Please ensure the model file is in this folder
    pause
    exit /b 1
)

if not exist "scaler.pkl" (
    echo ERROR: scaler.pkl not found
    echo Please ensure the scaler file is in this folder
    pause
    exit /b 1
)

REM Start the Flask application
echo Starting Flask server...
echo.
echo Open your browser and visit: http://localhost:5000
echo.
echo Press CTRL+C to stop the server
echo.
python app.py

pause