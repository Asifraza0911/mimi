@echo off
echo ========================================
echo   AI Waifu Cross-Platform System
echo   Stopping All Services...
echo ========================================
echo.

REM Kill all Python processes (Backend + Discord Bot)
echo [1/2] Stopping Python services (Backend API + Discord Bot)...
taskkill /F /IM python.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo Python services stopped successfully.
) else (
    echo No Python services were running.
)

REM Kill all Node processes (Web Client)
echo [2/2] Stopping Node services (Web Client)...
taskkill /F /IM node.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo Node services stopped successfully.
) else (
    echo No Node services were running.
)

echo.
echo ========================================
echo   All Services Stopped!
echo ========================================
echo.
echo WARNING: This stops ALL Python and Node processes.
echo If you have other Python/Node apps running, they were also stopped.
echo.
pause
