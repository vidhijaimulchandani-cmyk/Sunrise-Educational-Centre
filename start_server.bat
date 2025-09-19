@echo off
title Sunrise Educational Centre Server
echo.
echo ========================================
echo   SUNRISE EDUCATIONAL CENTRE SERVER
echo ========================================
echo.
echo Starting server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Start the server
python app.py

REM If we get here, the server stopped
echo.
echo Server has stopped.
pause