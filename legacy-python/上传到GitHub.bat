@echo off
chcp 65001 >nul
echo ================================================
echo 王者荣耀自动点击器 - GitHub自动上传工具
echo ================================================
echo.

REM 检查git是否安装
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Git，请先安装Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/6] 检测到Git已安装
echo.

REM 询问GitHub信息
set /p username="请输入你的GitHub用户名: "
set /p email="请输入你的GitHub邮箱（可选，按回车跳过）: "

if "%email%"=="" set email=%username%@users.noreply.github.com

echo.
echo [2/6] 配置Git用户信息...
git config --global user.name "%username%"
git config --global user.email "%email%"

echo.
echo [3/6] 初始化Git仓库...
if exist .git (
    echo Git仓库已存在，跳过初始化
) else (
    git init
    echo Git仓库初始化完成
)

echo.
echo [4/6] 添加所有文件到Git...
git add .
echo 文件添加完成

echo.
echo [5/6] 创建提交...
git commit -m "初始提交：王者荣耀自动点击器Android版"
if %errorlevel% neq 0 (
    echo 提交失败，可能没有新文件需要提交
) else (
    echo 提交成功
)

echo.
echo [6/6] 设置远程仓库并推送...
echo.
echo 请按以下步骤操作：
echo 1. 打开浏览器，访问 https://github.com/new
echo 2. 创建新仓库，名称为: wangzhe-autoclicker
echo 3. 选择 Public（公开）
echo 4. 不要勾选任何初始化选项
echo 5. 点击 Create repository
echo 6. 复制仓库地址（例如：https://github.com/你的用户名/wangzhe-autoclicker.git）
echo.

set /p repo_url="请粘贴你的仓库地址: "

git branch -M main
git remote add origin %repo_url% 2>nul
if %errorlevel% neq 0 (
    git remote set-url origin %repo_url%
)

echo.
echo 正在上传到GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo ✅ 上传成功！
    echo ================================================
    echo.
    echo 下一步：
    echo 1. 访问你的仓库: %repo_url%
    echo 2. 点击 "Actions" 标签
    echo 3. 等待自动构建（约20-40分钟）
    echo 4. 构建完成后下载APK
    echo.
) else (
    echo.
    echo ================================================
    echo ❌ 上传失败
    echo ================================================
    echo.
    echo 可能的原因：
    echo 1. 仓库地址不正确
    echo 2. 需要GitHub认证（访问令牌）
    echo.
    echo 解决方法：
    echo 1. 访问 https://github.com/settings/tokens
    echo 2. 创建 Personal access token (classic)
    echo 3. 勾选 repo 权限
    echo 4. 使用令牌作为密码
    echo.
)

pause