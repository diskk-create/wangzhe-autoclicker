@echo off
chcp 65001 >nul
echo ====================================
echo WangZhe Auto Clicker - Build Script
echo ====================================
echo.

echo Checking Gradle wrapper...
if not exist "gradlew.bat" (
    echo Generating Gradle wrapper...
    gradle wrapper
)

echo.
echo Building debug APK...
call gradlew.bat assembleDebug

if %errorlevel% neq 0 (
    echo.
    echo ====================================
    echo Build FAILED!
    echo ====================================
    pause
    exit /b 1
)

echo.
echo ====================================
echo Build SUCCESS!
echo ====================================
echo.
echo APK location: app\build\outputs\apk\debug\app-debug.apk
echo.

pause
