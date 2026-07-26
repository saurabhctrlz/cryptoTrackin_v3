@echo off
setlocal

echo ============================================
echo   CryptoTrackin - Windows Launcher
echo   Built by ambatron_ctrlz
echo ============================================
echo.

cd /d "%~dp0"

REM --- Check Python is installed ---
where python >nul 2>nul
if errorlevel 1 (
    echo [!] Python was not found on this system.
    echo     Download and install it from https://www.python.org/downloads/
    echo     During install, make sure to check "Add Python to PATH".
    pause
    exit /b 1
)

REM --- Create a virtual environment on first run ---
if not exist "venv\" (
    echo [*] First-time setup: creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [!] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat

REM --- Install/update dependencies ---
echo [*] Checking dependencies...
pip install -r requirements.txt -q

REM --- Check Node.js is installed ---
where npm >nul 2>nul
if errorlevel 1 (
    echo [!] npm was not found on this system.
    echo     Download and install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM --- Setup Frontend ---
if not exist "frontend\node_modules\" (
    echo [*] First-time frontend setup: installing npm dependencies...
    pushd frontend
    call npm install
    popd
)

if not exist "frontend\dist\" (
    echo [*] Building React frontend...
    pushd frontend
    call npm run build
    popd
)

REM --- Launch the dashboard ---
echo.
echo [+] Starting CryptoTrackin dashboard...
echo [+] Your browser will open automatically at http://127.0.0.1:5000
echo [+] Close this window (or press CTRL+C) to stop the server.
echo.

set CRYPTO_TRACKER_MOCK=false
python app.py

pause
