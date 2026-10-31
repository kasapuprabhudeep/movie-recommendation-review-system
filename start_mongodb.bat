@echo off
title MongoDB Server 9.0
echo ========================================================
echo   Starting Local MongoDB Server on Port 27017
echo ========================================================
echo.
if exist "C:\Program Files\MongoDB\Server\9.0\bin\mongod.exe" (
    echo Using MongoDB 9.0 from Program Files...
    "C:\Program Files\MongoDB\Server\9.0\bin\mongod.exe" --config "C:\Program Files\MongoDB\Server\9.0\bin\mongod.cfg"
) else (
    echo [ERROR] MongoDB not found at C:\Program Files\MongoDB\Server\9.0\bin\mongod.exe
)
if %errorlevel% neq 0 (
    echo.
    echo [NOTE] If this requires administrative privileges, right-click this .bat file and select 'Run as administrator', or start the MongoDB Windows service.
)
pause

