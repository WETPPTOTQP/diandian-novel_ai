@echo off
cd /d "%~dp0"

echo [INFO] Starting Novel AI Platform...

:: Start Backend
echo [INFO] Launching Backend...
start "Novel AI Backend" cmd /k "if exist .venv\Scripts\activate.bat (call .venv\Scripts\activate.bat && echo Activated venv) else (echo No venv found, using system python) && python -m backend.app"

:: Start Frontend
echo [INFO] Launching Frontend...
cd frontend
start "Novel AI Frontend" cmd /k "npm run dev"

echo.
echo [SUCCESS] Services are launching in separate windows.
echo - Backend API: http://127.0.0.1:5000
echo - Frontend UI: http://localhost:5173
echo.
pause