@echo off
cd /d "%~dp0"

echo [INFO] Starting Novel AI Platform...
echo [INFO] Checking and installing dependencies first...

:: Backend Setup
if not exist .venv (
    echo [INFO] Creating Python virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate.bat
echo [INFO] Installing backend dependencies...
pip install -r backend/requirements.txt

:: Frontend Setup
cd frontend
if not exist node_modules (
    echo [INFO] Installing frontend dependencies...
    call npm install
)
cd ..

echo.
echo [INFO] All dependencies ready. Launching services...

:: Start Backend
start "Novel AI Backend" cmd /k "call .venv\Scripts\activate.bat && python -m backend.app"

:: Start Frontend
cd frontend
start "Novel AI Frontend" cmd /k "npm run dev"

echo.
echo [SUCCESS] Services are launching in separate windows.
echo - Backend API: http://127.0.0.1:5000
echo - Frontend UI: http://localhost:5173
echo.
pause
