@echo off
title Push Project to GitHub
cd /d "%~dp0"
echo ========================================================
echo   Push MovieRecommendationSystem to GitHub
echo ========================================================
echo.

if not exist ".git" (
    echo [1/4] Initializing Git repository...
    git init
    git branch -M main
) else (
    echo [1/4] Git repository already initialized.
)

echo.
echo [2/4] Staging and committing files...
git add .
git commit -m "Complete Movie Recommendation & Review System (React, Flask, MongoDB, Neo4j, TMDB)"

echo.
echo [3/4] Checking remote origin...
git remote -v
echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/yourusername/MovieRecommendationSystem.git): "

if not "%REPO_URL%"=="" (
    git remote remove origin 2>nul
    git remote add origin %REPO_URL%
    echo.
    echo [4/4] Pushing to GitHub main branch...
    git push -u origin main
    echo.
    echo ========================================================
    echo   Code pushed to GitHub successfully!
    echo   Now you can deploy on Render.com with 1 click!
    echo ========================================================
) else (
    echo No repository URL provided. You can run 'git push origin main' manually.
)

pause

