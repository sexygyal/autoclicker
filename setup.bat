@echo off
cd /d "%~dp0"
echo.
echo  AutoClicker - installing Python packages (one-time or after updates)
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python was not found. Install Python 3.10+ from python.org
    echo  and check "Add python.exe to PATH" during setup, then run this again.
    echo.
    pause
    exit /b 1
)

echo  Using:
python --version
python -m pip --version
echo.

python -m pip install customtkinter==5.2.2 pynput==1.7.7 pywin32==308 pyinstaller==6.11.1

if errorlevel 1 (
    echo.
    echo  Install failed. Try running this file as Administrator, or:
    echo    python -m pip install --user customtkinter pynput pywin32 pyinstaller
    echo.
    pause
    exit /b 1
)

echo.
echo  All set. You can run the app with:  python src\main.py
echo  Build an .exe with:  python -m PyInstaller build.spec --noconfirm
echo.
pause
