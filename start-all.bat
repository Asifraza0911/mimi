@echo off
echo ========================================
echo   AI Waifu Cross-Platform System
echo   Starting All Services...
echo ========================================
echo.

REM Get the current directory
set ROOT_DIR=%~dp0

REM Start Backend API
echo [1/3] Starting Backend API...
start "AI Waifu Backend" cmd /k "cd /d "%ROOT_DIR%backend" && python main.py"
timeout /t 3 /nobreak >nul

REM Start Web Client
echo [2/3] Starting Web Client...
start "AI Waifu Web Client" cmd /k "cd /d "%ROOT_DIR%web-client" && ng serve"
timeout /t 3 /nobreak >nul

REM Start Discord Bot
echo [3/3] Starting Discord Bot...
start "AI Waifu Discord Bot" cmd /k "cd /d "%ROOT_DIR%discord-bot" && python discord_bot.py"

echo.
echo ========================================
echo   All Services Started!
echo ========================================
echo.
echo Backend API:     http://localhost:8000
echo Web Client:      http://localhost:4200
echo Discord Bot:     Connected to Discord
echo.
echo Three command windows have been opened:
echo - AI Waifu Backend
echo - AI Waifu Web Client
echo - AI Waifu Discord Bot
echo.
echo You can close this window now.
echo Services will continue running in their own windows.
echo.
pause
