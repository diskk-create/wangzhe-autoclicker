#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
王者荣耀自动点击器 - 稳定版
修复黑屏问题，增强错误处理
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
import time
import os
from pathlib import Path

# 延迟导入，避免启动时崩溃
PYJNIUS_AVAILABLE = False
CV_AVAILABLE = False
ANDROID_API_AVAILABLE = False
mActivity = None

class SimpleClicker:
    """简单点击器 - 优先保证启动"""

    def __init__(self):
        self.is_initialized = False
        self.screen_width = 1280
        self.screen_height = 720
        self.has_root = False

        # 按钮坐标（基准1280x720）
        self.buttons = {
            'login': {'x': 641, 'y': 564, 'desc': '登录'},
            'login_popup': {'x': 1190, 'y': 112, 'desc': '关闭弹窗'},
            'game_lobby': {'x': 514, 'y': 544, 'desc': '游戏大厅'},
            'match_screen': {'x': 398, 'y': 539, 'desc': '王者峡谷匹配'},
            'ai_mode_screen': {'x': 730, 'y': 601, 'desc': '人机模式'},
            'start_game_screen': {'x': 1057, 'y': 569, 'desc': '开始游戏'},
            'prepare_screen': {'x': 775, 'y': 660, 'desc': '准备游戏'},
            'ready_game': {'x': 640, 'y': 561, 'desc': '准备进入游戏'},
            'game_over': {'x': 635, 'y': 664, 'desc': '游戏结束'},
            'settlement_hero': {'x': 645, 'y': 621, 'desc': '结算英雄'},
            'return_room': {'x': 739, 'y': 651, 'desc': '返回房间'}
        }

        # 流程步骤
        self.flow_steps = [
            ('login', 3, '登录'),
            ('login_popup', 2, '关闭弹窗'),
            ('game_lobby', 2, '游戏大厅'),
            ('match_screen', 2, '王者峡谷匹配'),
            ('ai_mode_screen', 2, '人机模式'),
            ('start_game_screen', 3, '开始游戏'),
            ('prepare_screen', 2, '准备游戏'),
            ('ready_game', 10, '准备进入游戏'),
            ('game_over', 60, '游戏结束'),
            ('settlement_hero', 2, '结算英雄'),
            ('return_room', 3, '返回房间')
        ]

        # 延迟初始化Android
        Clock.schedule_once(self._init_android, 0.5)

    def _init_android(self, dt):
        """延迟初始化Android环境"""
        global PYJNIUS_AVAILABLE, ANDROID_API_AVAILABLE, mActivity

        try:
            from jnius import autoclass
            PYJNIUS_AVAILABLE = True

            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                mActivity = PythonActivity.mActivity

                # 获取屏幕尺寸
                display = mActivity.getWindowManager().getDefaultDisplay()
                Point = autoclass('android.graphics.Point')()
                display.getSize(Point)
                self.screen_width = Point.x
                self.screen_height = Point.y

                # 计算缩放比例
                self.scale_x = self.screen_width / 1280.0
                self.scale_y = self.screen_height / 720.0

                ANDROID_API_AVAILABLE = True
                self.is_initialized = True

                print(f"✓ Android初始化成功")
                print(f"  屏幕: {self.screen_width}x{self.screen_height}")
                print(f"  缩放: {self.scale_x:.2f}x{self.scale_y:.2f}")

            except Exception as e:
                print(f"✗ Android API初始化失败: {e}")
                self.is_initialized = True  # 继续运行，使用默认值

        except ImportError:
            print("✗ Pyjnius未安装，运行在桌面模式")
            self.is_initialized = True

    def click(self, x, y):
        """点击屏幕"""
        if not ANDROID_API_AVAILABLE:
            print(f"[桌面] 点击: ({int(x)}, {int(y)})")
            return True

        try:
            from jnius import autoclass
            Runtime = autoclass('java.lang.Runtime')
            TimeUnit = autoclass('java.util.concurrent.TimeUnit')
            runtime = Runtime.getRuntime()

            # 执行点击命令
            cmd = f"input tap {int(x)} {int(y)}"
            process = runtime.exec(cmd)
            process.waitFor(1, TimeUnit.SECONDS)

            exit_code = process.exitValue()
            if exit_code == 0:
                print(f"✓ 点击: ({int(x)}, {int(y)})")
                return True
            else:
                print(f"✗ 点击失败，退出码: {exit_code}")
                return False
        except Exception as e:
            print(f"✗ 点击异常: {e}")
            return False

    def smart_click(self, button_name):
        """智能点击 - 坐标点击"""
        if button_name in self.buttons:
            button = self.buttons[button_name]
            # 缩放坐标
            scaled_x = button['x'] * getattr(self, 'scale_x', 1.0)
            scaled_y = button['y'] * getattr(self, 'scale_y', 1.0)
            print(f"[坐标点击] {button['desc']}: ({int(scaled_x)}, {int(scaled_y)})")
            return self.click(scaled_x, scaled_y)

        print(f"✗ 未找到按钮: {button_name}")
        return False

    def run_flow(self, step_index=0, callback=None):
        """运行流程"""
        if step_index >= len(self.flow_steps):
            print("✓ 流程完成")
            if callback:
                callback("✓ 流程完成")
            return

        button_name, wait_time, desc = self.flow_steps[step_index]
        print(f"\n步骤 {step_index + 1}/{len(self.flow_steps)}: {desc}")

        # 点击按钮
        success = self.smart_click(button_name)

        if success:
            # 等待
            print(f"等待 {wait_time} 秒...")
            time.sleep(wait_time)

            # 下一步
            if callback:
                callback(f"步骤 {step_index + 1}/{len(self.flow_steps)}: {desc} ✓")

            # 继续下一步
            self.run_flow(step_index + 1, callback)
        else:
            if callback:
                callback(f"步骤 {step_index + 1}/{len(self.flow_steps)}: {desc} ✗")


class WangZheApp(App):
    """王者荣耀自动点击器"""

    title = "王者荣耀自动点击器 v3.1"

    def build(self):
        # 设置全屏
        try:
            Window.fullscreen = 'auto'
        except:
            pass

        # 主布局
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # 标题
        title = Label(
            text="王者荣耀自动点击器\nv3.1 稳定版",
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
            height=120,
            font_size='14sp'
        )
        layout.add_widget(self.status)

        # 初始化点击器
        self.clicker = SimpleClicker()

        # 延迟更新状态
        Clock.schedule_once(self._update_status, 1.0)

        # 按钮
        btns = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        btns.bind(minimum_height=btns.setter('height'))

        # 运行完整流程
        flow_btn = Button(text="运行完整流程 (11步)", size_hint_y=None, height=70)
        flow_btn.bind(on_press=self._run_flow)
        btns.add_widget(flow_btn)

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

    def _update_status(self, dt):
        """更新状态"""
        if self.clicker.is_initialized:
            w, h = self.clicker.screen_width, self.clicker.screen_height
            self.status.text = f"状态: 已初始化\n屏幕: {w}x{h}\n模式: 坐标点击"
        else:
            self.status.text = "状态: 初始化中..."

    def _run_flow(self, instance):
        """运行完整流程"""
        import threading

        def run():
            self.clicker.run_flow(callback=self._update_status_text)

        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

        self.status.text = "正在运行流程..."

    def _update_status_text(self, message):
        """更新状态文本"""
        Clock.schedule_once(lambda dt: setattr(self.status, 'text', message), 0)

    def _test_click(self, instance):
        """测试点击"""
        if not self.clicker.is_initialized:
            self.status.text = "初始化中...\n点击: (640, 360)"
            self.clicker.click(640, 360)
            return

        w, h = self.clicker.screen_width, self.clicker.screen_height
        cx, cy = w // 2, h // 2

        success = self.clicker.click(cx, cy)
        if success:
            self.status.text = f"✓ 点击成功\n位置: ({cx}, {cy})"
        else:
            self.status.text = "✗ 点击失败\n可能需要ROOT权限"

    def _open_settings(self, instance):
        """打开设置"""
        if ANDROID_API_AVAILABLE:
            try:
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                intent = Intent(Settings.ACTION_SETTINGS)
                mActivity.startActivity(intent)
                self.status.text = "已打开系统设置"
            except:
                self.status.text = "打开设置失败"
        else:
            self.status.text = "桌面模式"

    def _refresh(self, instance):
        """刷新"""
        if self.clicker.is_initialized:
            w, h = self.clicker.screen_width, self.clicker.screen_height
            self.status.text = f"屏幕: {w}x{h}\n模式: 坐标点击"
        else:
            self.status.text = "初始化中..."


if __name__ == '__main__':
    try:
        WangZheApp().run()
    except Exception as e:
        print(f"启动错误: {e}")
        import traceback
        traceback.print_exc()
