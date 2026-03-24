@echo off
cd /d "%~dp0"

where dotnet >nul 2>&1
if errorlevel 1 (
    echo ERROR: dotnet SDK not found.
    pause
    exit /b 1
)

set "PROJ=%~dp0AutoClickerLiteDotnet\AutoClickerLiteDotnet.csproj"
set "OUT_SAFE=%~dp0out-safe"
set "OUT_SLIM=%~dp0out-slim"

if exist "%OUT_SAFE%" rmdir /s /q "%OUT_SAFE%"
if exist "%OUT_SLIM%" rmdir /s /q "%OUT_SLIM%"

echo Building SAFE release...
dotnet publish "%PROJ%" -c Release -r win-x64 --self-contained false /p:PublishSingleFile=true -o "%OUT_SAFE%"
if errorlevel 1 (
    echo SAFE build failed.
    pause
    exit /b 1
)

echo Building SLIM release...
dotnet publish "%PROJ%" -c Release -r win-x64 --self-contained false /p:PublishSingleFile=true /p:DebugType=None /p:DebugSymbols=false /p:InvariantGlobalization=true -o "%OUT_SLIM%"
if errorlevel 1 (
    echo SLIM build failed.
    pause
    exit /b 1
)

echo.
for %%I in ("%OUT_SAFE%\AutoClickerLite.exe") do echo SAFE: %%~zI bytes
for %%I in ("%OUT_SLIM%\AutoClickerLite.exe") do echo SLIM: %%~zI bytes

echo.
echo Done.
pause
