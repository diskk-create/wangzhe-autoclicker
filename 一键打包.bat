@echo off
chcp 65001 >nul
echo ================================================
echo 王者荣耀自动点击器 - 一键打包APK
echo ================================================
echo.

REM 检查WSL
wsl --list >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到WSL，正在安装...
    echo.
    wsl --install -d Ubuntu-20.04
    if %errorlevel% neq 0 (
        echo [错误] WSL安装失败
        echo 请手动安装: https://docs.microsoft.com/zh-cn/windows/wsl/install
        pause
        exit /b 1
    )
    echo [成功] WSL安装完成，请重启电脑后再次运行此脚本
    pause
    exit /b 0
)

echo [✓] WSL已安装
echo.

REM 获取项目路径
set "PROJECT_PATH=%~dp0"
set "PROJECT_PATH=%PROJECT_PATH:\=/%"
set "PROJECT_PATH=%PROJECT_PATH::=%"
set "PROJECT_PATH=/mnt/c%PROJECT_PATH%"

echo 项目路径: %PROJECT_PATH%
echo.

REM 在WSL中执行打包
echo [1/5] 进入WSL环境...
wsl bash -c "cd '%PROJECT_PATH%' && pwd"

echo.
echo [2/5] 检查并安装buildozer...
wsl bash -c "if ! command -v buildozer &> /dev/null; then \
    echo '安装buildozer...'; \
    sudo apt update; \
    sudo apt install -y git zip unzip openjdk-11-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev automake python3 python3-pip; \
    pip3 install buildozer cython==0.29.33; \
fi && buildozer --version"

echo.
echo [3/5] 检查项目文件...
wsl bash -c "cd '%PROJECT_PATH%' && ls -la"

echo.
echo [4/5] 开始打包APK（首次需要30-60分钟）...
echo 请耐心等待，不要关闭窗口...
echo.
wsl bash -c "cd '%PROJECT_PATH%' && buildozer android debug"

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo [✓] 打包成功！
    echo ================================================
    echo.
    echo APK文件位置:
    wsl bash -c "cd '%PROJECT_PATH%' && ls -lh bin/*.apk"
    echo.
    echo 正在复制APK到桌面...
    wsl bash -c "cd '%PROJECT_PATH%' && cp bin/*.apk /mnt/c/Users/Administrator/Desktop/"
    echo.
    echo APK已复制到桌面！
    echo.
) else (
    echo.
    echo ================================================
    echo [✗] 打包失败
    echo ================================================
    echo.
    echo 请查看错误信息，常见问题：
    echo 1. 内存不足 - 增加WSL内存配置
    echo 2. 网络问题 - 检查网络连接
    echo 3. 依赖问题 - 重新运行此脚本
    echo.
)

pause