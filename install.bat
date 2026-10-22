@echo off
rem Sets up usfscript-py: virtual environment, Python dependencies and Chromium.
setlocal
cd /d "%~dp0"

set "PY=python"
where py >nul 2>nul
if not errorlevel 1 set "PY=py -3"

%PY% -c "import sys; sys.exit(sys.version_info < (3, 9))"
if errorlevel 1 (
    echo Python 3.9 or newer is required.
    exit /b 1
)

if not exist .venv\Scripts\python.exe (
    %PY% -m venv .venv
    if errorlevel 1 exit /b 1
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 exit /b 1
python -m pip install -e .
if errorlevel 1 exit /b 1
python -m playwright install chromium
if errorlevel 1 exit /b 1

echo.
echo Done. To use it:
echo   .venv\Scripts\activate
echo   python examples\demo.py
