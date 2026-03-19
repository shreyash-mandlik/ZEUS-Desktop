@echo off
echo.
echo  ==========================================
echo   ZEUS Desktop Builder
echo  ==========================================
echo.

:: Step 1 — Check Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Install Python 3.10+ from python.org
    pause
    exit /b 1
)
echo [OK] Python found.

:: Step 2 — Install dependencies
echo.
echo [1/3] Installing dependencies...
pip install -r requirements_desktop.txt --quiet
IF %ERRORLEVEL% NEQ 0 (
    echo [WARN] Some packages may have failed. Continuing...
)

:: Step 3 — Install PyInstaller
pip install pyinstaller --quiet
echo [OK] PyInstaller ready.

:: Step 4 — Build
echo.
echo [2/3] Building ZEUS_Desktop.exe ...
echo       (This takes 2-5 minutes, please wait)
echo.
pyinstaller zeus_desktop.spec --clean --noconfirm

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Build failed. Check the error above.
    echo Common fixes:
    echo   - Run: pip install pyaudio pipwin ^&^& pipwin install pyaudio
    echo   - Make sure .env file exists in this folder
    pause
    exit /b 1
)

:: Step 5 — Done
echo.
echo [3/3] Build complete!
echo.
echo  Your exe is at:  dist\ZEUS_Desktop.exe
echo  File size will be approx 80-120 MB (normal for bundled Python)
echo.
echo  To distribute: copy the entire dist\ZEUS_Desktop.exe to any Windows PC.
echo  No Python installation required on the target machine!
echo.
pause
