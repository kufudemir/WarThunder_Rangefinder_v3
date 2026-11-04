@echo off
setlocal
title War Thunder Tactical Rangefinder v3
cd /d "%~dp0"

:: ---------------------------------------------------------
:: 1. Detect Python
:: ---------------------------------------------------------
set "PYTHON_EXE="

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_EXE=python"
    goto :PYTHON_FOUND
)

where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_EXE=py -3"
    goto :PYTHON_FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :PYTHON_FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :PYTHON_FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    goto :PYTHON_FOUND
)

if exist "C:\Python311\python.exe" (
    set "PYTHON_EXE=C:\Python311\python.exe"
    goto :PYTHON_FOUND
)

if exist "C:\Python310\python.exe" (
    set "PYTHON_EXE=C:\Python310\python.exe"
    goto :PYTHON_FOUND
)

echo ========================================================================
echo   [ERROR] Python was not found on your system!
echo   [HATA]  Python sisteminizde bulunamadi!
echo ========================================================================
echo.
echo  1. Python 3.10 veya 3.11 kurabilirsiniz:
echo     https://www.python.org/downloads/
echo     (IMPORTANT: Check "Add Python to PATH" during installation)
echo.
echo  2. OR download the precompiled standalone executable:
echo     https://github.com/kufudemir/WarThunder_Rangefinder_v3/releases
echo     (Requires NO Python installation at all)
echo.
echo ========================================================================
pause
exit /b 1

:PYTHON_FOUND
:: ---------------------------------------------------------
:: 2. Check and auto-install dependencies
:: ---------------------------------------------------------
%PYTHON_EXE% -c "import onnxruntime, cv2, PIL, pynput, pyautogui, win32gui" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ========================================================================
    echo   War Thunder Tactical Rangefinder - Setup / Ilk Kurulum
    echo ========================================================================
    echo.
    echo  Installing required Python libraries from requirements.txt...
    echo  Gerekli kutuphaneler otomatik yukleniyor, lutfen bekleyin...
    echo  (One-time setup / Bu islem sadece ilk seferde yapilir)
    echo.
    echo ------------------------------------------------------------------------
    %PYTHON_EXE% -m pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ====================================================================
        echo  [ERROR] Failed to install dependencies. Please check internet connection
        echo  or run manually: pip install -r requirements.txt
        echo ====================================================================
        pause
        exit /b 1
    )
    echo.
    echo ------------------------------------------------------------------------
    echo  [OK] Dependencies installed successfully!
    echo  [OK] Launching application...
    echo ------------------------------------------------------------------------
    echo.
)

:: ---------------------------------------------------------
:: 3. Launch Application
:: ---------------------------------------------------------
%PYTHON_EXE% app.pyw
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Application exited with error code: %ERRORLEVEL%
    pause
)
