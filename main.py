#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
王者荣耀自动点击器 - 测试版
完全不调用Android API，只显示界面
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import time

print("========================================")
print("王者荣耀自动点击器启动")
print("========================================")


class SimpleClicker:
    """简单点击器 - 测试版，不调用Android API"""

    def __init__(self):
        self.is_initialized = True
        self.screen_width = 1280
        self.screen_height = 720
        self.has_root = False
        print("✓ 测试版初始化成功")

    def click(self, x, y):
        """点击屏幕（测试版）"""
        print(f"[测试] 点击: ({x}, {y})")
        return True

    def swipe(self, x1, y1, x2, y2, duration=300):
        """滑动屏幕（测试版）"""
        print(f"[测试] 滑动: ({x1}, {y1}) -> ({x2}, {y2})")
        return True

    def get_screen_size(self):
        """获取屏幕尺寸"""
        return self.screen_width, self.screen_height

    def open_settings(self):
        """打开设置（测试版）"""
        print("[测试] 打开设置")
        return True


class WangZheApp(App):
    """王者荣耀自动点击器 - 测试版"""

    title = "王者荣耀自动点击器 v3.0 测试版"

    def build(self):
        # 不设置全屏，避免黑屏
        # Window.fullscreen = 'auto'

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # 标题
        title = Label(
            text="王者荣耀自动点击器\nv3.0 测试版\n（不调用Android API）",
            size_hint_y=None,
            height=100,
            font_size='22sp',
            bold=True
        )
        layout.add_widget(title)

        # 状态
        self.status = Label(
            text="状态: 测试模式\n屏幕: 1280x720\n无ROOT",
            size_hint_y=None,
            height=100,
            font_size='16sp'
        )
        layout.add_widget(self.status)

        # 初始化点击器
        self.clicker = SimpleClicker()

        # 滚动区域
        scroll = ScrollView()
        btns = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        btns.bind(minimum_height=btns.setter('height'))

        # 11步流程按钮
        flow_btn = Button(text="运行完整流程（11步）", size_hint_y=None, height=70)
        flow_btn.bind(on_press=self._run_flow)
        btns.add_widget(flow_btn)

        # 单步测试按钮
        test_btn = Button(text="测试点击（屏幕中心）", size_hint_y=None, height=70)
        test_btn.bind(on_press=self._test_click)
        btns.add_widget(test_btn)

        # 打开设置
        settings_btn = Button(text="打开系统设置", size_hint_y=None, height=70)
        settings_btn.bind(on_press=self._open_settings)
        btns.add_widget(settings_btn)

        # 刷新状态
        refresh_btn = Button(text="刷新状态", size_hint_y=None, height=70)
        refresh_btn.bind(on_press=self._refresh)
        btns.add_widget(refresh_btn)

        scroll.add_widget(btns)
        layout.add_widget(scroll)

        print("✓ UI构建完成")
        return layout

    def _run_flow(self, instance):
        """运行完整流程"""
        self.status.text = "测试模式\n运行流程（未实现）"
        print("[测试] 运行完整流程")

    def _update_status(self, message):
        """更新状态"""
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: setattr(self.status, 'text', message), 0)

    def _test_click(self, instance):
        """测试点击"""
        self.status.text = "测试模式\n点击: (640, 360)"
        self.clicker.click(640, 360)

    def _open_settings(self, instance):
        """打开设置"""
        self.status.text = "测试模式\n打开设置"
        self.clicker.open_settings()

    def _refresh(self, instance):
        """刷新"""
        self.status.text = "状态: 测试模式\n屏幕: 1280x720\n无ROOT"


if __name__ == '__main__':
    print("========================================")
    print("启动Kivy应用")
    print("========================================")
    try:
        WangZheApp().run()
    except Exception as e:
        print(f"启动错误: {e}")
        import traceback
        traceback.print_exc()
