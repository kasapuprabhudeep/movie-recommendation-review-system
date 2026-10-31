@echo off
title CineGraph - Flask Backend Server
cd /d "%~dp0"
if exist backend cd backend
echo ===================================================
echo   Starting Movie Recommendation Backend (Port 5000)
echo ===================================================
python app.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Backend failed to start.
)
pause
