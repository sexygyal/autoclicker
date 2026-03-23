@echo off
cd /d "%~dp0"
echo Building dist\AutoClicker.exe (one-file, clean)...
python -m PyInstaller build.spec --noconfirm --clean
if errorlevel 1 exit /b 1

echo.
echo Verifying embedded icon matches assets\icon.ico, then refreshing shell icons...
python tools\check_exe_icon.py --compare --refresh-shell-icons
if errorlevel 1 exit /b 1

echo.
echo Done. Output: dist\AutoClicker.exe
pause
