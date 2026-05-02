@echo off
echo ============================================
echo   AI Student Mental Health Companion - Sage
echo ============================================
echo.

REM Check if .env exists
if not exist .env (
    echo [WARNING] .env file not found. Copying from .env.example...
    copy .env.example .env
    echo Please edit .env and add your GEMINI_API_KEY, then re-run this script.
    pause
    exit /b
)

REM Install dependencies if needed
echo [1/2] Checking dependencies...
pip install -r requirements.txt --quiet

echo [2/2] Starting Flask server...
echo.
echo  Open your browser at: http://localhost:5000
echo  Press Ctrl+C to stop the server.
echo.
python app.py

pause
