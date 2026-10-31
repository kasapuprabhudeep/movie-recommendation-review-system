@echo off
title CineGraph - React Frontend Server
cd /d "%~dp0"
if exist frontend cd frontend
echo ===================================================
echo   Starting Movie Recommendation Frontend (Port 3000)
echo ===================================================
npm run dev
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Frontend failed to start.
)
pause
