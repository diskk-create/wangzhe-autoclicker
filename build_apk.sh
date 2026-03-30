#!/bin/bash
# 王者荣耀自动点击器 - APK打包脚本
# 用于Linux/WSL环境

echo "========================================"
echo "王者荣耀自动点击器 - APK打包工具"
echo "========================================"
echo ""

# 检查是否在项目目录
if [ ! -f "buildozer.spec" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    echo "当前目录: $(pwd)"
    exit 1
fi

# 检查buildozer是否安装
if ! command -v buildozer &> /dev/null; then
    echo "错误: buildozer未安装"
    echo "请运行: pip3 install buildozer"
    exit 1
fi

# 检查Python版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $PYTHON_VERSION"

# 显示菜单
echo ""
echo "请选择操作:"
echo "1. 首次打包（下载SDK/NDK）"
echo "2. 快速打包（已有SDK/NDK）"
echo "3. 清理构建文件"
echo "4. 查看构建日志"
echo "5. 安装到设备"
echo "6. 退出"
echo ""

read -p "请输入选项 (1-6): " choice

case $choice in
    1)
        echo ""
        echo "开始首次打包..."
        echo "注意: 首次打包需要下载Android SDK/NDK，时间较长（约30-60分钟）"
        echo ""
        read -p "确认继续? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            buildozer android debug
        else
            echo "已取消"
        fi
        ;;
    2)
        echo ""
        echo "开始快速打包..."
        buildozer android debug
        echo ""
        echo "打包完成！"
        echo "APK位置: bin/王者荣耀自动点击器-1.0.0-arm64-v8a-debug.apk"
        ;;
    3)
        echo ""
        echo "清理构建文件..."
        buildozer android clean
        rm -rf .buildozer
        rm -rf bin
        echo "清理完成"
        ;;
    4)
        echo ""
        echo "构建日志:"
        if [ -f ".buildozer/android/platform/build-arm64-v8a/build.log" ]; then
            tail -50 .buildozer/android/platform/build-arm64-v8a/build.log
        else
            echo "未找到构建日志"
        fi
        ;;
    5)
        echo ""
        echo "安装到设备..."
        if [ -f "bin/王者荣耀自动点击器-1.0.0-arm64-v8a-debug.apk" ]; then
            adb install -r bin/王者荣耀自动点击器-1.0.0-arm64-v8a-debug.apk
        else
            echo "错误: APK文件不存在"
            echo "请先构建APK"
        fi
        ;;
    6)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选项"
        ;;
esac

echo ""
echo "========================================"
echo "操作完成"
echo "========================================"