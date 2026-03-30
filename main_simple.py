#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
王者荣耀自动点击器 - 简化版
使用ADB方式，避免无障碍服务依赖问题
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import subprocess
import os
import time

class ADBAutoClicker:
    """ADB自动点击器"""

    def __init__(self):
        self.adb_path = self._find_adb()
        self.device_id = None
        self.is_connected = False

        if self.adb_path:
            self._connect_device()

    def _find_adb(self):
        """查找ADB路径"""
        # 常见ADB路径
        possible_paths = [
            r"D:\Program Files\Microvirt\MEmu\adb.exe",  # MuMu模拟器
            r"C:\Program Files\Nox\bin\adb.exe",  # 夜神模拟器
            r"C:\Program Files\LDPlayer\adb.exe",  # 雷电模拟器
            r"C:\Program Files\BlueStacks\HD-Adb.exe",  # BlueStacks
            "adb",  # 系统PATH
        ]

        for path in possible_paths:
            try:
                result = subprocess.run([path, "version"], capture_output=True, timeout=2)
                if result.returncode == 0:
                    print(f"找到ADB: {path}")
                    return path
            except:
                continue

        return None

    def _connect_device(self):
        """连接设备"""
        if not self.adb_path:
            return False

        try:
            # 列出设备
            result = subprocess.run(
                [self.adb_path, "devices"],
                capture_output=True,
                text=True,
                timeout=5
            )

            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                # 找到设备
                for line in lines[1:]:
                    if '\t' in line:
                        device_id, status = line.split('\t')
                        if status == 'device':
                            self.device_id = device_id
                            self.is_connected = True
                            print(f"已连接设备: {device_id}")
                            return True

            print("未找到设备")
            return False
        except Exception as e:
            print(f"连接设备失败: {e}")
            return False

    def click(self, x, y):
        """点击屏幕"""
        if not self.is_connected:
            print("设备未连接")
            return False

        try:
            cmd = [self.adb_path, "-s", self.device_id, "shell", "input", "tap", str(x), str(y)]
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            print(f"点击: ({x}, {y})")
            return result.returncode == 0
        except Exception as e:
            print(f"点击失败: {e}")
            return False

    def swipe(self, x1, y1, x2, y2, duration=300):
        """滑动屏幕"""
        if not self.is_connected:
            return False

        try:
            cmd = [
                self.adb_path, "-s", self.device_id, "shell", "input", "swipe",
                str(x1), str(y1), str(x2), str(y2), str(duration)
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception as e:
            print(f"滑动失败: {e}")
            return False

    def get_screen_size(self):
        """获取屏幕尺寸"""
        if not self.is_connected:
            return None

        try:
            cmd = [self.adb_path, "-s", self.device_id, "shell", "wm", "size"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            # 解析输出: Physical size: 1280x720
            if "Physical size:" in result.stdout:
                size_str = result.stdout.split("Physical size:")[1].strip()
                width, height = size_str.split('x')
                return int(width), int(height
            return None
        except Exception as e:
            print(f"获取屏幕尺寸失败: {e}")
            return None


class WangZheApp(App):
    """王者荣耀自动点击器主程序"""

    title = "王者荣耀自动点击器 v3.0"

    def build(self):
        """构建界面"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # 标题
        title_label = Label(
            text="王者荣耀自动点击器\nv3.0 (ADB版)",
            size_hint_y=None,
            height=80,
            font_size='20sp'
        )
        layout.add_widget(title_label)

        # 状态标签
        self.status_label = Label(
            text="状态: 未连接设备",
            size_hint_y=None,
            height=50,
            font_size='16sp'
        )
        layout.add_widget(self.status_label)

        # 初始化点击器
        self.clicker = ADBAutoClicker()

        # 更新状态
        if self.clicker.is_connected:
            screen_size = self.clicker.get_screen_size()
            if screen_size:
                self.status_label.text = f"状态: 已连接\n屏幕: {screen_size[0]}x{screen_size[1]}"
            else:
                self.status_label.text = "状态: 已连接"
        else:
            self.status_label.text = "状态: 设备未连接\n请确保ADB可用且设备已连接"

        # 按钮容器
        btn_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        btn_layout.bind(minimum_height=btn_layout.setter('height'))

        # 测试按钮
        test_btn = Button(text="测试点击 (屏幕中心)", size_hint_y=None, height=50)
        test_btn.bind(on_press=self._test_click)
        btn_layout.add_widget(test_btn)

        # 刷新设备按钮
        refresh_btn = Button(text="刷新设备连接", size_hint_y=None, height=50)
        refresh_btn.bind(on_press=self._refresh_device)
        btn_layout.add_widget(refresh_btn)

        # 滚动视图
        scroll = ScrollView()
        scroll.add_widget(btn_layout)
        layout.add_widget(scroll)

        return layout

    def _test_click(self, instance):
        """测试点击"""
        if not self.clicker.is_connected:
            self.status_label.text = "错误: 设备未连接"
            return

        # 点击屏幕中心
        screen_size = self.clicker.get_screen_size()
        if screen_size:
            center_x = screen_size[0] // 2
            center_y = screen_size[1] // 2
            self.clicker.click(center_x, center_y)
            self.status_label.text = f"已点击: ({center_x}, {center_y})"
        else:
            # 默认点击
            self.clicker.click(640, 360)
            self.status_label.text = "已点击: (640, 360)"

    def _refresh_device(self, instance):
        """刷新设备连接"""
        self.clicker._connect_device()
        if self.clicker.is_connected:
            screen_size = self.clicker.get_screen_size()
            if screen_size:
                self.status_label.text = f"状态: 已连接\n屏幕: {screen_size[0]}x{screen_size[1]}"
            else:
                self.status_label.text = "状态: 已连接"
        else:
            self.status_label.text = "状态: 设备未连接"


if __name__ == '__main__':
    WangZheApp().run()
