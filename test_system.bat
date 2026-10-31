@echo off
title CineGraph - System & API Diagnostic Tests
echo ========================================================
echo   Running Movie Recommendation System Diagnostics
echo ========================================================
echo.
echo [1] Testing Database Connections and Graph Engine...
cd backend
python test_connections.py
if %errorlevel% neq 0 (
    echo [ERROR] test_connections.py failed.
    pause
    exit /b %errorlevel%
)

echo.
echo [2] Running Backend API Endpoint Test Suite (11 Tests)...
python -m unittest test_api.py
if %errorlevel% neq 0 (
    echo [ERROR] test_api.py failed.
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================================
echo   ALL TESTS PASSED WITH 100%% SUCCESS!
echo ========================================================
pause

