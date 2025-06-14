@echo off
REM Windows Build Script for Aleksameter
REM This batch file runs the PowerShell build script

echo.
echo ================================================
echo    Aleksameter Windows Build Tool
echo ================================================
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Error: PowerShell not found
    echo    Please ensure PowerShell is installed on your system
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "..\..\app.py" (
    echo ❌ Error: Please run this script from deployment/windows directory
    echo    Current directory should contain ../../app.py
    pause
    exit /b 1
)

echo 🔄 Starting PowerShell build script...
echo.

REM Run the PowerShell script
powershell -ExecutionPolicy Bypass -File "build_and_package_windows.ps1"

if %errorlevel% neq 0 (
    echo.
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo.
echo ✅ Build completed!
echo 📁 Check the dist folder for built files
echo 📦 Check for ZIP installer package

pause 