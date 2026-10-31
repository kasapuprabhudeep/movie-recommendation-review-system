@echo off
title CineGraph - Instant Live Public Sharing Link
cd /d "%~dp0"
echo ========================================================
echo   CineGraph - Instant Public Share Link Generator
echo ========================================================
echo.
echo 1. Ensure your backend is running on port 5000 (start_backend.bat or run_all.bat).
echo 2. Generating your temporary live public HTTPS link...
echo.
echo ========================================================
echo Look for the 'https://xxxxx.a.free.pinggy.link' URL below.
echo You can share that URL with anyone on any phone or laptop!
echo Press Ctrl+C anytime to stop sharing.
echo ========================================================
echo.
ssh -p 443 -R0:localhost:5000 -o StrictHostKeyChecking=no a.pinggy.io
pause

