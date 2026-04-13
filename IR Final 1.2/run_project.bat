@echo off
echo ==================================================
echo 🚀 Starting InsightRural - Full Project
echo ==================================================

:: 1. Start Backend Server
echo [*] Starting Backend Server...
cd "college/backend"
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate
)
start "InsightRural Backend" cmd /k "python app.py"

:: Wait for backend to initialize
timeout /t 5 >nul

:: 2. Start Frontend Server
echo [*] Starting Frontend Server...
cd "../../insightrural-frontend"
:: Start Python HTTP server for frontend (port 8000)
start "InsightRural Frontend" cmd /k "python -m http.server 8000"

:: 3. Open in Browser
echo [*] Opening Application...
timeout /t 2 >nul
start http://localhost:8000

echo ==================================================
echo ✅ Project is running!
echo 📝 Backend: http://127.0.0.1:5000
echo 💻 Frontend: http://localhost:8000
echo ==================================================
pause
