@echo off
title CineGraph - Full Stack Launcher
cd /d "%~dp0"
echo ========================================================
echo   Launching CineGraph: Movie Recommendation System
echo ========================================================
echo.
echo 1. Launching Flask Backend on http://localhost:5000...
start "CineGraph Backend" cmd /k "call start_backend.bat"

echo 2. Launching React Frontend on http://localhost:3000...
start "CineGraph Frontend" cmd /k "call start_frontend.bat"

echo.
echo ========================================================
echo   Application started!
echo   - Frontend: http://localhost:3000
echo   - Backend:  http://localhost:5000/api/status
echo ========================================================
pause
