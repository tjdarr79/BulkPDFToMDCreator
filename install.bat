@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  Bulk PDF to MD Creator - Setup
echo ============================================
echo.

REM --- 1. Check for Python -------------------------------------------------
set "PY_CMD="
py -3 --version >nul 2>nul
if %errorlevel%==0 (
    set "PY_CMD=py -3"
    goto :have_python
)
python --version >nul 2>nul
if %errorlevel%==0 (
    set "PY_CMD=python"
    goto :have_python
)

echo Python was not found on this system.
where winget >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo winget is not available on this machine, so Python can't be installed
    echo automatically. Please install Python 3.10+ from:
    echo     https://www.python.org/downloads/
    echo ^(check "Add python.exe to PATH" during install^), then re-run install.bat.
    pause
    exit /b 1
)

echo Installing Python 3.12 via winget - this may take a few minutes...
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
if %errorlevel% neq 0 (
    echo.
    echo Automatic Python installation failed. Please install Python 3.10+
    echo manually from https://www.python.org/downloads/ and re-run install.bat.
    pause
    exit /b 1
)

echo.
echo Python has been installed. Please close this window and double-click
echo install.bat again to finish setup.
pause
exit /b 0

:have_python
echo Found Python:
%PY_CMD% --version
echo.

REM --- 2. Create virtual environment ---------------------------------------
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PY_CMD% -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create the virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists, skipping creation.
)

REM --- 3. Install dependencies ----------------------------------------------
echo Installing dependencies...
"venv\Scripts\python.exe" -m pip install --upgrade pip >nul
"venv\Scripts\python.exe" -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

REM --- 4. Create Desktop shortcut with the app icon -------------------------
echo Creating Desktop shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0installer\create_shortcut.ps1"
if %errorlevel% neq 0 (
    echo Failed to create the Desktop shortcut. You can still run the app with:
    echo     venv\Scripts\pythonw.exe app.py
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Setup complete!
echo  "Bulk PDF to MD Creator" was added to your Desktop.
echo ============================================
pause
