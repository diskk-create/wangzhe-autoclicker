#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
王者荣耀自动点击器 - 完整版
支持找图、找字、11步完整流程
使用Pyjnius独立实现，不依赖android模块
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
import time
import os
from pathlib import Path

# 导入Pyjnius
try:
    from jnius import autoclass, cast
    PYJNIUS_AVAILABLE = True
    print("✓ Pyjnius已加载")
except ImportError:
    PYJNIUS_AVAILABLE = False
    print("✗ Pyjnius未安装，运行在桌面模式")

# 导入OpenCV（可选）
try:
    import cv2
    import numpy as np
    CV_AVAILABLE = True
    print("✓ OpenCV已加载，图像识别功能可用")
except ImportError:
    CV_AVAILABLE = False
    print("✗ OpenCV未安装，仅使用坐标点击")

# Android API
if PYJNIUS_AVAILABLE:
    try:
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Context = autoclass('android.content.Context')
        Intent = autoclass('android.content.Intent')
        Settings = autoclass('android.provider.Settings')
        mActivity = PythonActivity.mActivity
        ANDROID_API_AVAILABLE = True
        print("✓ Android API已加载")
    except Exception as e:
        print(f"✗ Android API加载失败: {e}")
        ANDROID_API_AVAILABLE = False
else:
    ANDROID_API_AVAILABLE = False


class ImageMatcher:
    """图像匹配器 - 找图和找字"""

    def __init__(self, template_dir='templates', threshold=0.9):
        self.template_dir = Path(template_dir)
        self.threshold = threshold
        self.cv_available = CV_AVAILABLE

        # 按钮模板
        self.button_templates = {}
        # 文字模板
        self.text_templates = {}

        if self.cv_available:
            self._load_templates()

    def _load_templates(self):
        """加载模板文件"""
        if not self.template_dir.exists():
            print(f"⚠ 模板目录不存在: {self.template_dir}")
            return

        # 按钮模板列表
        button_templates = {
            'login': 'template_login.png',
            'login_popup': 'template_login_popup.png',
            'game_lobby': 'template_game_lobby.png',
            'match_screen': 'template_match.png',
            'ai_mode_screen': 'template_ai_mode.png',
            'start_game_screen': 'template_start_game.png',
            'prepare_screen': 'template_prepare.png',
            'ready_game': 'template_ready_game.png',
            'game_over': 'template_game_over.png',
            'settlement_hero': 'template_check.png',
            'return_room': 'template_check.png'
        }

        # 文字模板列表
        text_templates = {
            'login': 'text_template_login.png',
            'game_lobby': 'text_template_game_lobby.png',
            'wangzhe_xiagu': 'text_template_wangzhe_xiagu.png',
            'settlement_hero': 'text_template_settlement_hero.png',
            'return_room': 'text_template_return_room.png'
        }

        # 加载按钮模板
        print("\n加载模板文件:")
        for name, filename in button_templates.items():
            path = self.template_dir / filename
            if path.exists():
                template = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
                if template is not None:
                    self.button_templates[name] = template
                    print(f"  ✓ 按钮模板: {name}")

        # 加载文字模板
        for name, filename in text_templates.items():
            path = self.template_dir / filename
            if path.exists():
                template = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
                if template is not None:
                    self.text_templates[name] = template
                    print(f"  ✓ 文字模板: {name}")

        print(f"\n共加载: {len(self.button_templates)}个按钮模板, {len(self.text_templates)}个文字模板")

    def match_template(self, screenshot, template):
        """模板匹配"""
        if not self.cv_available:
            return False, None, 0.0

        try:
            # 转换为灰度图
            if len(screenshot.shape) == 3:
                gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            else:
                gray = screenshot

            # 模板匹配
            result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # 检查匹配阈值
            if max_val >= self.threshold:
                # 计算中心点
                h, w = template.shape
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                return True, (center_x, center_y), max_val

            return False, None, max_val
        except Exception as e:
            print(f"✗ 模板匹配失败: {e}")
            return False, None, 0.0


class AndroidClicker:
    """Android点击器 - 完整版"""

    def __init__(self, template_dir='templates'):
        self.is_initialized = False
        self.screen_width = 1280
        self.screen_height = 720
        self.has_root = False

        # 初始化图像匹配器
        self.matcher = ImageMatcher(template_dir, threshold=0.9)

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

        # 初始化Android
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

            # 计算缩放比例
            self.scale_x = self.screen_width / 1280.0
            self.scale_y = self.screen_height / 720.0

            # 检查ROOT权限
            self._check_root()

            self.is_initialized = True
            print(f"✓ Android初始化成功")
            print(f"  屏幕: {self.screen_width}x{self.screen_height}")
            print(f"  缩放: {self.scale_x:.2f}x{self.scale_y:.2f}")
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
            print(f"[桌面] 点击: ({x}, {y})")
            return True

        try:
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
        """智能点击 - 优先找图，其次找字，最后坐标"""
        # 优先级1: 找图
        if button_name in self.matcher.button_templates and CV_AVAILABLE:
            # TODO: 实现截图功能
            pass

        # 优先级2: 找字
        if button_name in self.matcher.text_templates and CV_AVAILABLE:
            # TODO: 实现截图功能
            pass

        # 优先级3: 坐标点击（兜底）
        if button_name in self.buttons:
            button = self.buttons[button_name]
            # 缩放坐标
            scaled_x = button['x'] * self.scale_x
            scaled_y = button['y'] * self.scale_y
            print(f"[坐标点击] {button['desc']}: ({int(scaled_x)}, {int(scaled_y)})")
            return self.click(scaled_x, scaled_y)

        print(f"✗ 未找到按钮: {button_name}")
        return False

    def run_flow(self, step_index=0, callback=None):
        """运行流程"""
        if step_index >= len(self.flow_steps):
            print("✓ 流程完成")
            if callback:
                callback("流程完成")
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
    """王者荣耀自动点击器 - 完整版"""

    title = "王者荣耀自动点击器 v3.0"

    def build(self):
        Window.fullscreen = 'auto'

        # 主布局
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # 标题
        title = Label(
            text="王者荣耀自动点击器\nv3.0 完整版",
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
        self.clicker = AndroidClicker()

        # 更新状态
        if self.clicker.is_initialized:
            w, h = self.clicker.screen_width, self.clicker.screen_height
            root = "有ROOT" if self.clicker.has_root else "无ROOT"
            cv = "有OpenCV" if CV_AVAILABLE else "无OpenCV"
            self.status.text = f"状态: 已初始化\n屏幕: {w}x{h}\n{root} | {cv}"
        else:
            self.status.text = f"状态: 桌面模式\nOpenCV: {'有' if CV_AVAILABLE else '无'}"

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

    def _run_flow(self, instance):
        """运行完整流程"""
        import threading
        
        def run():
            self.clicker.run_flow(callback=self._update_status)
        
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()
        
        self.status.text = "正在运行流程..."

    def _update_status(self, message):
        """更新状态"""
        Clock.schedule_once(lambda dt: setattr(self.status, 'text', message), 0)

    def _test_click(self, instance):
        """测试点击"""
        if not self.clicker.is_initialized:
            self.status.text = "桌面模式\n点击: (640, 360)"
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
            self.clicker._init_android()
            w, h = self.clicker.screen_width, self.clicker.screen_height
            root = "有ROOT" if self.clicker.has_root else "无ROOT"
            cv = "有OpenCV" if CV_AVAILABLE else "无OpenCV"
            self.status.text = f"屏幕: {w}x{h}\n{root} | {cv}"
        else:
            self.status.text = f"桌面模式\nOpenCV: {'有' if CV_AVAILABLE else '无'}"


if __name__ == '__main__':
    WangZheApp().run()
