#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
王者荣耀自动点击器 - Pyjnius版
使用Pyjnius直接调用Android API，避免无障碍服务依赖问题
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
import time

# 尝试导入Pyjnius
try:
    from jnius import autoclass, cast
    PYJNIUS_AVAILABLE = True
    print("Pyjnius已加载")
except ImportError:
    PYJNIUS_AVAILABLE = False
    print("警告: Pyjnius未安装，运行在模拟模式")

# Android类
if PYJNIUS_AVAILABLE:
    try:
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Settings = autoclass('android.provider.Settings')
        Uri = autoclass('android.net.Uri')
        Build = autoclass('android.os.Build')
        VERSION = autoclass('android.os.Build$VERSION')
        ANDROID_AVAILABLE = True
        print("Android API已加载")
    except Exception as e:
        print(f"Android API加载失败: {e}")
        ANDROID_AVAILABLE = False
else:
    ANDROID_AVAILABLE = False


class AndroidClicker:
    """Android点击器 - 使用Pyjnius"""

    def __init__(self):
        self.is_initialized = False
        self.screen_width = 1280
        self.screen_height = 720

        if ANDROID_AVAILABLE:
            self._init_android()

    def _init_android(self):
        """初始化Android环境"""
        try:
            # 获取当前Activity
            self.activity = PythonActivity.mActivity

            # 获取屏幕尺寸
            self._get_screen_size()

            self.is_initialized = True
            print(f"Android环境初始化成功")
            print(f"屏幕尺寸: {self.screen_width}x{self.screen_height}")
        except Exception as e:
            print(f"Android环境初始化失败: {e}")
            self.is_initialized = False

    def _get_screen_size(self):
        """获取屏幕尺寸"""
        try:
            display = self.activity.getWindowManager().getDefaultDisplay()
            point = autoclass('android.graphics.Point')()
            display.getSize(point)
            self.screen_width = point.x
            self.screen_height = point.y
        except Exception as e:
            print(f"获取屏幕尺寸失败: {e}")
            # 使用默认值
            self.screen_width = 1280
            self.screen_height = 720

    def open_accessibility_settings(self):
        """打开无障碍设置"""
        if not ANDROID_AVAILABLE:
            print("Android环境不可用")
            return False

        try:
            intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
            self.activity.startActivity(intent)
            print("已打开无障碍设置")
            return True
        except Exception as e:
            print(f"打开无障碍设置失败: {e}")
            return False

    def click(self, x, y):
        """模拟点击（使用ADB命令或Runtime.exec）"""
        if not ANDROID_AVAILABLE:
            print(f"模拟点击: ({x}, {y})")
            return True

        try:
            # 方法1: 使用Runtime.exec执行input tap命令
            Runtime = autoclass('java.lang.Runtime')
            runtime = Runtime.getRuntime()

            # 执行点击命令
            cmd = f"input tap {x} {y}"
            process = runtime.exec(cmd)
            process.waitFor()

            print(f"点击: ({x}, {y})")
            return True
        except Exception as e:
            print(f"点击失败: {e}")
            return False

    def swipe(self, x1, y1, x2, y2, duration=300):
        """模拟滑动"""
        if not ANDROID_AVAILABLE:
            print(f"模拟滑动: ({x1}, {y1}) -> ({x2}, {y2})")
            return True

        try:
            Runtime = autoclass('java.lang.Runtime')
            runtime = Runtime.getRuntime()

            # 执行滑动命令
            cmd = f"input swipe {x1} {y1} {x2} {y2} {duration}"
            process = runtime.exec(cmd)
            process.waitFor()

            print(f"滑动: ({x1}, {y1}) -> ({x2}, {y2})")
            return True
        except Exception as e:
            print(f"滑动失败: {e}")
            return False

    def get_screen_size(self):
        """获取屏幕尺寸"""
        return self.screen_width, self.screen_height


class WangZheApp(App):
    """王者荣耀自动点击器主程序"""

    title = "王者荣耀自动点击器 v3.0"

    def build(self):
        """构建界面"""
        # 设置全屏
        Window.fullscreen = 'auto'

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # 标题
        title_label = Label(
            text="王者荣耀自动点击器\nv3.0 (Pyjnius版)",
            size_hint_y=None,
            height=80,
            font_size='20sp'
        )
        layout.add_widget(title_label)

        # 状态标签
        self.status_label = Label(
            text="状态: 初始化中...",
            size_hint_y=None,
            height=80,
            font_size='16sp'
        )
        layout.add_widget(self.status_label)

        # 初始化点击器
        self.clicker = AndroidClicker()

        # 更新状态
        if self.clicker.is_initialized:
            screen_size = self.clicker.get_screen_size()
            self.status_label.text = f"状态: 已初始化\n屏幕: {screen_size[0]}x{screen_size[1]}"
        else:
            self.status_label.text = "状态: 运行在模拟模式\n（需要在Android设备上运行）"

        # 按钮容器
        btn_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        btn_layout.bind(minimum_height=btn_layout.setter('height'))

        # 测试按钮
        test_btn = Button(text="测试点击 (屏幕中心)", size_hint_y=None, height=60)
        test_btn.bind(on_press=self._test_click)
        btn_layout.add_widget(test_btn)

        # 打开设置按钮
        settings_btn = Button(text="打开无障碍设置", size_hint_y=None, height=60)
        settings_btn.bind(on_press=self._open_settings)
        btn_layout.add_widget(settings_btn)

        # 刷新屏幕尺寸按钮
        refresh_btn = Button(text="刷新屏幕尺寸", size_hint_y=None, height=60)
        refresh_btn.bind(on_press=self._refresh_screen)
        btn_layout.add_widget(refresh_btn)

        # 滚动视图
        scroll = ScrollView()
        scroll.add_widget(btn_layout)
        layout.add_widget(scroll)

        return layout

    def _test_click(self, instance):
        """测试点击"""
        if not self.clicker.is_initialized:
            self.status_label.text = "状态: 运行在模拟模式\n点击: (640, 360)"
            self.clicker.click(640, 360)
            return

        # 点击屏幕中心
        screen_size = self.clicker.get_screen_size()
        center_x = screen_size[0] // 2
        center_y = screen_size[1] // 2

        success = self.clicker.click(center_x, center_y)
        if success:
            self.status_label.text = f"已点击: ({center_x}, {center_y})"
        else:
            self.status_label.text = f"点击失败"

    def _open_settings(self, instance):
        """打开无障碍设置"""
        self.clicker.open_accessibility_settings()
        self.status_label.text = "已打开无障碍设置"

    def _refresh_screen(self, instance):
        """刷新屏幕尺寸"""
        if self.clicker.is_initialized:
            self.clicker._get_screen_size()
            screen_size = self.clicker.get_screen_size()
            self.status_label.text = f"屏幕尺寸: {screen_size[0]}x{screen_size[1]}"
        else:
            self.status_label.text = "运行在模拟模式"


if __name__ == '__main__':
    WangZheApp().run()
