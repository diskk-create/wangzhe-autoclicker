#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
王者荣耀自动点击器 - Pyjnius独立版
不依赖android模块，使用Pyjnius直接调用Java API
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import time

# 只导入Pyjnius，不导入android模块
try:
    from jnius import autoclass, cast
    PYJNIUS_AVAILABLE = True
    print("✓ Pyjnius已加载")
except ImportError:
    PYJNIUS_AVAILABLE = False
    print("✗ Pyjnius未安装，运行在桌面模式")

# 定义Java类
if PYJNIUS_AVAILABLE:
    try:
        # Kivy的PythonActivity
        PythonActivity = autoclass('org.kivy.android.PythonActivity')

        # Android基础类
        Context = autoclass('android.content.Context')
        Intent = autoclass('android.content.Intent')
        Settings = autoclass('android.provider.Settings')

        # 获取当前Activity
        mActivity = PythonActivity.mActivity

        ANDROID_API_AVAILABLE = True
        print("✓ Android API已加载")
    except Exception as e:
        print(f"✗ Android API加载失败: {e}")
        ANDROID_API_AVAILABLE = False
else:
    ANDROID_API_AVAILABLE = False


class SimpleClicker:
    """简单点击器 - 使用Runtime.exec执行shell命令"""

    def __init__(self):
        self.is_initialized = False
        self.screen_width = 1280
        self.screen_height = 720
        self.has_root = False

        if ANDROID_API_AVAILABLE:
            self._init_android()

    def _init_android(self):
        """初始化Android环境"""
        try:
            # 获取屏幕尺寸
            display = mActivity.getWindowManager().getDefaultDisplay()
            Point = autoclass('android.graphics.Point')()
            display.getSize(Point)
            self.screen_width = Point.x
            self.screen_height = Point.y

            # 测试是否有ROOT权限
            self._check_root()

            self.is_initialized = True
            print(f"✓ Android初始化成功")
            print(f"  屏幕: {self.screen_width}x{self.screen_height}")
            print(f"  ROOT: {'有' if self.has_root else '无'}")
        except Exception as e:
            print(f"✗ Android初始化失败: {e}")
            self.is_initialized = False

    def _check_root(self):
        """检查ROOT权限"""
        try:
            Runtime = autoclass('java.lang.Runtime')
            process = Runtime.getRuntime().exec("su")
            process.waitFor()
            self.has_root = (process.exitValue() == 0)
        except:
            self.has_root = False

    def click(self, x, y):
        """点击屏幕"""
        if not ANDROID_API_AVAILABLE:
            print(f"[桌面模式] 点击: ({x}, {y})")
            return True

        try:
            Runtime = autoclass('java.lang.Runtime')
            runtime = Runtime.getRuntime()

            # 方法1: 尝试使用input命令（需要ROOT或特殊权限）
            cmd = f"input tap {x} {y}"
            process = runtime.exec(cmd)
            process.waitFor(1, autoclass('java.util.concurrent.TimeUnit').SECONDS)

            exit_code = process.exitValue()
            if exit_code == 0:
                print(f"✓ 点击成功: ({x}, {y})")
                return True
            else:
                print(f"✗ 点击失败，退出码: {exit_code}")
                return False
        except Exception as e:
            print(f"✗ 点击异常: {e}")
            return False

    def swipe(self, x1, y1, x2, y2, duration=300):
        """滑动屏幕"""
        if not ANDROID_API_AVAILABLE:
            print(f"[桌面模式] 滑动: ({x1}, {y1}) -> ({x2}, {y2})")
            return True

        try:
            Runtime = autoclass('java.lang.Runtime')
            runtime = Runtime.getRuntime()

            cmd = f"input swipe {x1} {y1} {x2} {y2} {duration}"
            process = runtime.exec(cmd)
            process.waitFor(1, autoclass('java.util.concurrent.TimeUnit').SECONDS)

            exit_code = process.exitValue()
            return exit_code == 0
        except Exception as e:
            print(f"✗ 滑动异常: {e}")
            return False

    def get_screen_size(self):
        """获取屏幕尺寸"""
        return self.screen_width, self.screen_height

    def open_settings(self):
        """打开设置"""
        if not ANDROID_API_AVAILABLE:
            print("[桌面模式] 打开设置")
            return True

        try:
            intent = Intent(Settings.ACTION_SETTINGS)
            mActivity.startActivity(intent)
            return True
        except Exception as e:
            print(f"✗ 打开设置失败: {e}")
            return False


class WangZheApp(App):
    """王者荣耀自动点击器"""

    title = "王者荣耀自动点击器 v3.0"

    def build(self):
        # 不设置全屏，避免黑屏问题
        # Window.fullscreen = 'auto'

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # 标题
        title = Label(
            text="王者荣耀自动点击器\nv3.0 (Pyjnius独立版)",
            size_hint_y=None,
            height=100,
            font_size='22sp',
            bold=True
        )
        layout.add_widget(title)

        # 状态
        self.status = Label(
            text="状态: 初始化中...",
            size_hint_y=None,
            height=100,
            font_size='16sp'
        )
        layout.add_widget(self.status)

        # 初始化点击器
        self.clicker = SimpleClicker()

        # 更新状态
        if self.clicker.is_initialized:
            w, h = self.clicker.get_screen_size()
            root_status = "有ROOT" if self.clicker.has_root else "无ROOT"
            self.status.text = f"状态: 已初始化\n屏幕: {w}x{h}\n{root_status}"
        else:
            self.status.text = "状态: 桌面模式\n（在Android设备上运行）"

        # 按钮
        btns = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        btns.bind(minimum_height=btns.setter('height'))

        # 测试点击
        test_btn = Button(text="测试点击 (屏幕中心)", size_hint_y=None, height=70)
        test_btn.bind(on_press=self._test_click)
        btns.add_widget(test_btn)

        # 打开设置
        settings_btn = Button(text="打开系统设置", size_hint_y=None, height=70)
        settings_btn.bind(on_press=self._open_settings)
        btns.add_widget(settings_btn)

        # 刷新
        refresh_btn = Button(text="刷新屏幕信息", size_hint_y=None, height=70)
        refresh_btn.bind(on_press=self._refresh)
        btns.add_widget(refresh_btn)

        scroll = ScrollView()
        scroll.add_widget(btns)
        layout.add_widget(scroll)

        return layout

    def _test_click(self, instance):
        """测试点击"""
        if not self.clicker.is_initialized:
            self.status.text = "桌面模式\n点击: (640, 360)"
            self.clicker.click(640, 360)
            return

        w, h = self.clicker.get_screen_size()
        cx, cy = w // 2, h // 2

        success = self.clicker.click(cx, cy)
        if success:
            self.status.text = f"✓ 点击成功\n位置: ({cx}, {cy})"
        else:
            self.status.text = f"✗ 点击失败\n可能需要ROOT权限"

    def _open_settings(self, instance):
        """打开设置"""
        self.clicker.open_settings()
        self.status.text = "已打开系统设置"

    def _refresh(self, instance):
        """刷新"""
        if self.clicker.is_initialized:
            self.clicker._init_android()
            w, h = self.clicker.get_screen_size()
            root_status = "有ROOT" if self.clicker.has_root else "无ROOT"
            self.status.text = f"屏幕: {w}x{h}\n{root_status}"
        else:
            self.status.text = "桌面模式"


if __name__ == '__main__':
    WangZheApp().run()
