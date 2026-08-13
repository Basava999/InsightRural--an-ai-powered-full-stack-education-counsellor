@echo off
:: ═══════════════════════════════════════════════════════════════════════════
:: InsightRural Platform v2.0 — Windows Startup Script
:: Starts the FastAPI backend + opens the frontend
:: ═══════════════════════════════════════════════════════════════════════════

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║       InsightRural AI Counselling Platform v2.0               ║
echo  ║       Karnataka KCET Engineering Admissions                   ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

:: ── Find Python ────────────────────────────────────────────────────────────
set PYTHON=python
python --version >nul 2>&1 || (
    set PYTHON=python3
    python3 --version >nul 2>&1 || (
        echo [ERROR] Python not found. Install Python 3.10+ from https://python.org
        pause
        exit /b 1
    )
)

:: ── Locate backend directory ────────────────────────────────────────────────
set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%backend
set LEGACY_DIR=%SCRIPT_DIR%..\backend

echo [1/4] Checking Python environment...
%PYTHON% --version

:: ── Install dependencies ────────────────────────────────────────────────────
echo.
echo [2/4] Installing/updating dependencies...
%PYTHON% -m pip install -r "%BACKEND_DIR%\requirements.txt" --quiet --disable-pip-version-check
if errorlevel 1 (
    echo [WARNING] Some packages failed to install. Continuing...
)

:: ── Start FastAPI backend ───────────────────────────────────────────────────
echo.
echo [3/4] Starting FastAPI backend on http://localhost:8000 ...
echo       API Docs: http://localhost:8000/api/v2/docs

:: Add legacy backend to PYTHONPATH for engine imports
set PYTHONPATH=%BACKEND_DIR%;%LEGACY_DIR%;%PYTHONPATH%

start "InsightRural Backend" cmd /k "cd /d "%BACKEND_DIR%" && set PYTHONPATH=%BACKEND_DIR%;%LEGACY_DIR% && %PYTHON% -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

:: ── Wait for backend to start ───────────────────────────────────────────────
echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

:: ── Open frontend ───────────────────────────────────────────────────────────
echo.
echo [4/4] Opening frontend...
set FRONTEND=%SCRIPT_DIR%frontend\index.html
if exist "%FRONTEND%" (
    start "" "%FRONTEND%"
    echo [OK] Frontend opened in browser
) else (
    echo [ERROR] Frontend not found at: %FRONTEND%
)

echo.
echo ══════════════════════════════════════════════════════════════════
echo  Platform is running!
echo  
echo  Backend API:  http://localhost:8000
echo  API Docs:     http://localhost:8000/api/v2/docs
echo  Frontend:     file://%FRONTEND%
echo.
echo  Press Ctrl+C in the backend window to stop the server.
echo ══════════════════════════════════════════════════════════════════
echo.
pause
