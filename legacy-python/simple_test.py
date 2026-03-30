#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试 - 测试点击功能是否有反馈
"""

import subprocess
import time

def adb(cmd):
    """执行ADB命令"""
    result = subprocess.run(f"adb -s 127.0.0.1:21503 {cmd}", shell=True, capture_output=True, text=True)
    return result.stdout

print("="*60)
print("简单测试 - 点击功能")
print("="*60)

# 1. 启动应用
print("\n1. 启动应用...")
adb("shell am force-stop org.wangzhe.wangzheautoclicker")
time.sleep(1)
adb("shell monkey -p org.wangzhe.wangzheautoclicker -c android.intent.category.LAUNCHER 1")
time.sleep(3)

# 2. 清空日志
print("2. 清空日志...")
adb("logcat -c")

# 3. 点击屏幕
print("3. 点击Test Click按钮 (640, 450)...")
adb("shell input tap 640 450")
time.sleep(2)

# 4. 获取日志
print("4. 获取日志...")
logs = adb("logcat -d -s python:*")

print("\n" + "="*60)
print("日志输出:")
print("="*60)

# 查找关键信息
has_button = False
has_click = False
has_android = False

for line in logs.split('\n'):
    line = line.strip()
    if not line or 'python' not in line:
        continue

    if 'Android initialized' in line:
        has_android = True
        print(f"[OK] Android初始化: {line}")
    elif 'BUTTON' in line.upper():
        has_button = True
        print(f"[OK] 按钮事件: {line}")
    elif 'CLICK' in line.upper() and 'ATTEMPTING' in line.upper():
        has_click = True
        print(f"[OK] 点击事件: {line}")

print("\n" + "="*60)
print("测试结果:")
print("="*60)
print(f"Android初始化: {'成功' if has_android else '失败'}")
print(f"按钮点击事件: {'成功' if has_button else '失败'}")
print(f"点击功能: {'成功' if has_click else '失败'}")
print("="*60)

if not has_button:
    print("\n问题分析:")
    print("- 按钮点击事件没有触发")
    print("- 可能原因: Kivy没有接收到触摸事件")
    print("- 建议: 手动在模拟器中点击按钮测试")
