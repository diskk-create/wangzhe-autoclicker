@echo off
chcp 65001 >nul
echo ====================================
echo WangZhe Auto Clicker - Install Script
echo ====================================
echo.

set APK_PATH=app\build\outputs\apk\debug\app-debug.apk

if not exist "%APK_PATH%" (
    echo APK not found! Please run build.bat first.
    pause
    exit /b 1
)

echo Checking device connection...
adb devices

echo.
echo Installing APK...
adb install -r "%APK_PATH%"

if %errorlevel% neq 0 (
    echo.
    echo Installation FAILED!
    pause
    exit /b 1
)

echo.
echo ====================================
echo Installation SUCCESS!
echo ====================================
echo.
echo Launching app...
adb shell am start -n com.wangzhe.autoclicker/.MainActivity

echo.
pause
