#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动测试点击功能
通过ADB监控模拟器，自动测试点击是否有反馈
"""

import subprocess
import time
from datetime import datetime

def adb_command(cmd, device="127.0.0.1:21503"):
    """执行ADB命令"""
    full_cmd = f"adb -s {device} {cmd}"
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def get_screen():
    """获取屏幕截图"""
    adb_command("shell screencap -p /sdcard/test_screen.png")
    adb_command("pull /sdcard/test_screen.png C:\\Users\\Administrator\\Desktop\\test_screen.png")
    adb_command("shell rm /sdcard/test_screen.png")
    return "C:\\Users\\Administrator\\Desktop\\test_screen.png"

def tap_screen(x, y):
    """点击屏幕"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 点击屏幕: ({x}, {y})")
    stdout, stderr, code = adb_command(f"shell input tap {x} {y}")
    time.sleep(0.5)

def check_app_running():
    """检查应用是否运行"""
    stdout, _, _ = adb_command("shell pidof org.wangzhe.wangzheautoclicker")
    return stdout.strip() != ""

def start_app():
    """启动应用"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 启动应用...")
    adb_command("shell monkey -p org.wangzhe.wangzheautoclicker -c android.intent.category.LAUNCHER 1")
    time.sleep(3)

def monitor_log(duration=10):
    """监控日志"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始监控日志 {duration} 秒...")

    # 清空日志
    adb_command("logcat -c")

    # 启动应用
    start_app()

    # 等待应用启动
    time.sleep(2)

    # 点击按钮
    tap_screen(640, 450)

    # 等待日志
    time.sleep(2)

    # 获取日志
    stdout, _, _ = adb_command("logcat -d -s python:*")

    print("\n" + "="*60)
    print("日志输出:")
    print("="*60)

    # 查找关键日志
    found_button = False
    found_click = False
    found_android = False

    for line in stdout.split('\n'):
        if 'BUTTON' in line or 'Test Click button pressed' in line:
            print(f"[OK] [按钮事件] {line}")
            found_button = True
        elif 'CLICK' in line and 'python' in line:
            print(f"[OK] [点击事件] {line}")
            found_click = True
        elif 'Android initialized' in line:
            print(f"[OK] [初始化] {line}")
            found_android = True

    print("\n" + "="*60)
    print("测试结果:")
    print("="*60)
    print(f"Android初始化: {'成功' if found_android else '失败'}")
    print(f"按钮点击事件: {'成功' if found_button else '失败'}")
    print(f"点击功能: {'成功' if found_click else '失败'}")
    print("="*60)

    return found_android, found_button, found_click

def test_click_feedback():
    """测试点击反馈"""
    print("\n" + "="*60)
    print("测试点击反馈")
    print("="*60)

    # 1. 打开设置
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 打开设置...")
    adb_command("shell am start -a android.settings.SETTINGS")
    time.sleep(2)

    # 2. 截图保存当前状态
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 截图保存当前状态...")
    screen1 = get_screen()

    # 3. 点击屏幕某个位置（应该在设置界面触发某些效果）
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 点击设置界面...")
    tap_screen(640, 360)

    # 4. 截图保存点击后状态
    time.sleep(1)
    screen2 = get_screen()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 对比截图...")
    print(f"截图1: {screen1}")
    print(f"截图2: {screen2}")
    print("提示: 如果两张截图不同，说明点击有反馈")

    # 5. 返回我们的应用
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 返回应用...")
    start_app()
    time.sleep(2)

def test_auto_click():
    """自动测试应用内点击"""
    print("\n" + "="*60)
    print("自动测试应用内点击")
    print("="*60)

    # 1. 启动应用
    start_app()

    # 2. 截图保存初始状态
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 截图保存初始状态...")
    screen_before = get_screen()

    # 3. 点击Test Click按钮
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 点击Test Click按钮...")
    tap_screen(640, 450)

    # 4. 等待并截图
    time.sleep(1)
    screen_after = get_screen()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 对比截图...")
    print(f"点击前: {screen_before}")
    print(f"点击后: {screen_after}")
    print("提示: 如果点击计数增加，说明按钮有响应")

def main():
    print("="*60)
    print("王者荣耀自动点击器 - 自动测试脚本")
    print("="*60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"设备: 127.0.0.1:21503")
    print("="*60)

    # 测试1: 监控日志
    print("\n[测试1] 监控应用日志...")
    found_android, found_button, found_click = monitor_log()

    # 测试2: 测试点击反馈
    print("\n[测试2] 测试点击反馈...")
    test_click_feedback()

    # 测试3: 自动测试应用内点击
    print("\n[测试3] 自动测试应用内点击...")
    test_auto_click()

    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n总结:")
    print(f"1. Android初始化: {'成功' if found_android else '失败'}")
    print(f"2. 按钮点击事件: {'成功' if found_button else '失败'}")
    print(f"3. 点击功能: {'成功' if found_click else '失败'}")
    print("\n如果按钮点击事件失败，可能是:")
    print("- Kivy没有接收到触摸事件")
    print("- 按钮坐标不正确")
    print("- 需要手动测试")
    print("="*60)

if __name__ == "__main__":
    main()
