#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
王者荣耀自动点击器 - 完整版
修复黑屏问题，保留找图找字功能
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


class ImageMatcher:
    """图像匹配器 - 找图和找字"""

    def __init__(self, template_dir='templates', threshold=0.9):
        self.template_dir = Path(template_dir)
        self.threshold = threshold
        self.cv_available = False
        self.button_templates = {}
        self.text_templates = {}

        # 延迟加载OpenCV
        self._load_opencv()

    def _load_opencv(self):
        """延迟加载OpenCV"""
        global CV_AVAILABLE
        try:
            import cv2
            import numpy as np
            self.cv2 = cv2
            self.np = np
            self.cv_available = True
            CV_AVAILABLE = True
            print("✓ OpenCV已加载")
        except ImportError:
            print("✗ OpenCV未安装，仅使用坐标点击")
            self.cv_available = False

    def load_templates(self):
        """加载模板文件（延迟加载）"""
        if not self.cv_available:
            print("⚠ OpenCV不可用，跳过模板加载")
            return

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

        print("\n加载模板文件:")
        # 加载按钮模板
        for name, filename in button_templates.items():
            path = self.template_dir / filename
            if path.exists():
                try:
                    template = self.cv2.imread(str(path), self.cv2.IMREAD_GRAYSCALE)
                    if template is not None:
                        self.button_templates[name] = template
                        print(f"  ✓ 按钮模板: {name}")
                except Exception as e:
                    print(f"  ✗ 加载失败 {name}: {e}")

        # 加载文字模板
        for name, filename in text_templates.items():
            path = self.template_dir / filename
            if path.exists():
                try:
                    template = self.cv2.imread(str(path), self.cv2.IMREAD_GRAYSCALE)
                    if template is not None:
                        self.text_templates[name] = template
                        print(f"  ✓ 文字模板: {name}")
                except Exception as e:
                    print(f"  ✗ 加载失败 {name}: {e}")

        print(f"\n共加载: {len(self.button_templates)}个按钮模板, {len(self.text_templates)}个文字模板")

    def match_template(self, screenshot, template):
        """模板匹配"""
        if not self.cv_available:
            return False, None, 0.0

        try:
            # 转换为灰度图
            if len(screenshot.shape) == 3:
                gray = self.cv2.cvtColor(screenshot, self.cv2.COLOR_BGR2GRAY)
            else:
                gray = screenshot

            # 模板匹配
            result = self.cv2.matchTemplate(gray, template, self.cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = self.cv2.minMaxLoc(result)

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

    def __init__(self):
        self.is_initialized = False
        self.screen_width = 1280
        self.screen_height = 720
        self.has_root = False
        self.scale_x = 1.0
        self.scale_y = 1.0

        # 图像匹配器（延迟加载）
        self.matcher = None

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

        # 延迟初始化
        Clock.schedule_once(self._init_android, 0.3)
        Clock.schedule_once(self._init_matcher, 1.0)

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
                print(f"✓ Android初始化成功")
                print(f"  屏幕: {self.screen_width}x{self.screen_height}")
                print(f"  缩放: {self.scale_x:.2f}x{self.scale_y:.2f}")

            except Exception as e:
                print(f"✗ Android API初始化失败: {e}")

        except ImportError:
            print("✗ Pyjnius未安装，运行在桌面模式")

        self.is_initialized = True

    def _init_matcher(self, dt):
        """延迟初始化图像匹配器"""
        print("\n初始化图像匹配器...")
        self.matcher = ImageMatcher(threshold=0.9)
        if self.matcher.cv_available:
            self.matcher.load_templates()

    def click(self, x, y):
        """点击屏幕"""
        global ANDROID_API_AVAILABLE

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
        """智能点击 - 优先找图，其次找字，最后坐标"""
        # 优先级1: 找图（如果有模板且OpenCV可用）
        if self.matcher and self.matcher.cv_available:
            if button_name in self.matcher.button_templates:
                # TODO: 实现截屏功能
                print(f"[找图] {button_name}（需要截屏功能）")

        # 优先级2: 找字（如果有模板且OpenCV可用）
        if self.matcher and self.matcher.cv_available:
            if button_name in self.matcher.text_templates:
                # TODO: 实现截屏功能
                print(f"[找字] {button_name}（需要截屏功能）")

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
            text="王者荣耀自动点击器\nv3.1 完整版",
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

        # 延迟更新状态
        Clock.schedule_once(self._update_status, 1.5)

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

        # 加载模板
        load_btn = Button(text="重新加载模板", size_hint_y=None, height=70)
        load_btn.bind(on_press=self._load_templates)
        btns.add_widget(load_btn)

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
            cv_status = "有OpenCV" if (self.clicker.matcher and self.clicker.matcher.cv_available) else "无OpenCV"
            self.status.text = f"状态: 已初始化\n屏幕: {w}x{h}\n{cv_status}"
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

    def _load_templates(self, instance):
        """重新加载模板"""
        if self.clicker.matcher:
            self.clicker.matcher.load_templates()
            self._update_status(0)
        else:
            self.status.text = "图像匹配器未初始化"

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
        global ANDROID_API_AVAILABLE, mActivity

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
            self._update_status(0)
        else:
            self.status.text = "初始化中..."


if __name__ == '__main__':
    try:
        WangZheApp().run()
    except Exception as e:
        print(f"启动错误: {e}")
        import traceback
        traceback.print_exc()
