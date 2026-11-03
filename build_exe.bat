@echo off
title Building War Thunder Rangefinder v3 Standalone Executable
cd /d "%~dp0"
echo ==============================================================
echo   Compiling War Thunder Rangefinder v3 into Standalone .exe
echo   (Lightweight Build - Excludes PyTorch, Matplotlib, SciPy)
echo ==============================================================
echo.

python -m PyInstaller --noconsole --onefile ^
  --name "WarThunderRangefinder_v3" ^
  --add-data "data;data" ^
  --add-data "distance/code;code" ^
  --add-data "distance/code;distance/code" ^
  --collect-all "onnxruntime" ^
  --collect-all "pystray" ^
  --hidden-import "PIL" ^
  --hidden-import "PIL.ImageGrab" ^
  --hidden-import "pynput" ^
  --hidden-import "cv2" ^
  --hidden-import "pyautogui" ^
  --hidden-import "pyscreeze" ^
  --hidden-import "win32gui" ^
  --hidden-import "win32api" ^
  --hidden-import "win32con" ^
  --hidden-import "pywintypes" ^
  --exclude-module "torch" ^
  --exclude-module "torchvision" ^
  --exclude-module "matplotlib" ^
  --exclude-module "scipy" ^
  --exclude-module "pandas" ^
  --exclude-module "tensorboard" ^
  --exclude-module "IPython" ^
  --exclude-module "jupyter" ^
  app.pyw

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==============================================================
    echo [OK] LIGHTWEIGHT BUILD SUCCESSFUL!
    echo Standalone executable created at: dist\WarThunderRangefinder_v3.exe
    echo ==============================================================
) else (
    echo.
    echo [!] Build failed! Please check the output above.
)
pause
