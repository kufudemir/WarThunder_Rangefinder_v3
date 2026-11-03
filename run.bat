@echo off
title War Thunder Tactical Rangefinder v3
cd /d "%~dp0"

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python app.pyw
) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" app.pyw
) else (
    echo [ERROR] Python not found in PATH or standard installation directory!
    echo Please install Python 3.10+ or run the standalone executable in dist\
    pause
    exit /b 1
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Application exited with an error code: %ERRORLEVEL%
    pause
)
