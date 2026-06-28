@echo off
setlocal EnableDelayedExpansion

:: ─── Read version from version.txt ───────────────────────────────────────────
set "VER=unknown"
if exist version.txt (
    set /p VER=<version.txt
    set "VER=!VER: =!"
)

echo.
echo ╔══════════════════════════════════════════════╗
echo ║        Byte Recovery Pro — Build Tool        ║
echo ╠══════════════════════════════════════════════╣
echo ║  Version : !VER!
echo ║  Output  : dist\ByteRecoveryPro.exe
echo ╚══════════════════════════════════════════════╝
echo.

:: ─── Install dependencies ─────────────────────────────────────────────────────
echo [1/3] Installing build dependencies...
pip install --quiet --upgrade eel pyinstaller
if %ERRORLEVEL% neq 0 (
    echo ERROR: pip install failed. Make sure Python is on PATH.
    exit /b 1
)

:: ─── Build executable ─────────────────────────────────────────────────────────
echo [2/3] Building executable (this may take a minute)...
pyinstaller app.py ^
    --noconsole ^
    --onefile ^
    --name "ByteRecoveryPro" ^
    --add-data "web;web" ^
    --add-data "version.txt;." ^
    --clean ^
    --noconfirm

if %ERRORLEVEL% neq 0 (
    echo ERROR: PyInstaller build failed.
    exit /b 1
)

:: ─── Done ─────────────────────────────────────────────────────────────────────
echo [3/3] Done!
echo.
echo   Executable : dist\ByteRecoveryPro.exe
echo   Version    : !VER!
echo.
echo   Right-click the .exe and select "Run as administrator"
echo   to enable raw disk access.
echo.
