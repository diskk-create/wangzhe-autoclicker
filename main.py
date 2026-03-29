#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
王者荣耀自动点击器 - Android版 (无障碍服务版)
主程序入口 - 使用Android无障碍服务实现自动化
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.properties import StringProperty, BooleanProperty
from kivy.core.image import Image as CoreImage
import json
import os
import threading
import time

# Android相关导入
try:
    from jnius import autoclass, cast
    from android import mActivity
    from android.permissions import request_permissions, Permission
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False
    print("警告: Android环境未检测到，运行在模拟模式")

# 导入核心脚本
from scripts.smart_auto_clicker import SmartAutoClicker
from scripts.config_manager import ConfigManager


class AccessibilityService:
    """Android无障碍服务封装"""
    
    def __init__(self):
        self.service = None
        self.is_connected = False
        
        if ANDROID_AVAILABLE:
            self._init_accessibility()
    
    def _init_accessibility(self):
        """初始化无障碍服务"""
        try:
            # 获取无障碍服务管理器
            AccessibilityManager = autoclass('android.view.accessibility.AccessibilityManager')
            context = mActivity.getApplicationContext()
            self.accessibility_manager = AccessibilityManager.getInstance(context)
            
            # 检查无障碍服务是否启用
            self.is_connected = self._check_accessibility_enabled()
        except Exception as e:
            print(f"初始化无障碍服务失败: {e}")
            self.is_connected = False
    
    def _check_accessibility_enabled(self):
        """检查无障碍服务是否启用"""
        try:
            context = mActivity.getApplicationContext()
            Settings = autoclass('android.provider.Settings')
            enabled_services = Settings.Secure.getString(
                context.getContentResolver(),
                Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
            )
            # 检查我们的服务是否在启用列表中
            package_name = context.getPackageName()
            return enabled_services and package_name in enabled_services
        except:
            return False
    
    def open_accessibility_settings(self):
        """打开无障碍设置页面"""
        if ANDROID_AVAILABLE:
            try:
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
                mActivity.startActivity(intent)
            except Exception as e:
                print(f"打开无障碍设置失败: {e}")
    
    def click(self, x, y):
        """执行点击操作"""
        if not self.is_connected:
            print("无障碍服务未连接，使用模拟点击")
            return self._simulate_click(x, y)
        
        try:
            # 使用无障碍服务执行点击
            # 这里需要配合自定义的无障碍服务实现
            pass
        except Exception as e:
            print(f"点击失败: {e}")
            return self._simulate_click(x, y)
    
    def _simulate_click(self, x, y):
        """模拟点击（备用方案）"""
        if ANDROID_AVAILABLE:
            try:
                # 使用Instrumentation发送点击事件
                Instrumentation = autoclass('android.app.Instrumentation')
                UiAutomation = autoclass('android.app.UiAutomation')
                MotionEvent = autoclass('android.view.MotionEvent')
                
                # 获取屏幕信息
                context = mActivity.getApplicationContext()
                display = context.getSystemService(context.WINDOW_SERVICE).getDefaultDisplay()
                metrics = autoclass('android.util.DisplayMetrics')()
                display.getMetrics(metrics)
                
                # 发送点击事件
                # 注意：实际需要ROOT权限或无障碍服务
                return True
            except Exception as e:
                print(f"模拟点击失败: {e}")
                return False
        return False
    
    def take_screenshot(self):
        """截取屏幕"""
        if not ANDROID_AVAILABLE:
            return None
        
        try:
            # 使用MediaProjection API截图（需要权限）
            MediaProjectionManager = autoclass('android.media.projection.MediaProjectionManager')
            context = mActivity.getApplicationContext()
            mpm = context.getSystemService(context.MEDIA_PROJECTION_SERVICE)
            
            # 创建截图intent
            # 注意：需要用户授权
            return None
        except Exception as e:
            print(f"截图失败: {e}")
            return None
    
    def get_screen_size(self):
        """获取屏幕尺寸"""
        if ANDROID_AVAILABLE:
            try:
                context = mActivity.getApplicationContext()
                display = context.getSystemService(context.WINDOW_SERVICE).getDefaultDisplay()
                metrics = autoclass('android.util.DisplayMetrics')()
                display.getMetrics(metrics)
                return metrics.widthPixels, metrics.heightPixels
            except:
                pass
        return 1280, 720  # 默认分辨率


class AutoClickerApp(App):
    """主应用类"""
    
    title = "王者荣耀自动点击器"
    
    def build(self):
        """构建应用界面"""
        # 检查权限
        if ANDROID_AVAILABLE:
            self._request_permissions()
        
        # 创建主布局
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题
        title_label = Label(
            text='[size=24][b]王者荣耀自动点击器[/b][/size]\n[size=14]v2.0 - Android原生版[/size]',
            markup=True,
            size_hint_y=0.08
        )
        self.layout.add_widget(title_label)
        
        # 创建Tab面板
        self.panel = TabbedPanel(tab_pos='top_left')
        
        # Tab 1: 主控制
        self.create_main_tab()
        
        # Tab 2: 配置编辑
        self.create_config_tab()
        
        # Tab 3: 权限设置
        self.create_permission_tab()
        
        # Tab 4: 日志查看
        self.create_log_tab()
        
        # Tab 5: 帮助信息
        self.create_help_tab()
        
        self.layout.add_widget(self.panel)
        
        # 状态栏
        self.status_label = Label(
            text='状态: 就绪',
            size_hint_y=0.05,
            color=(0, 1, 0, 1)
        )
        self.layout.add_widget(self.status_label)
        
        # 初始化
        self.config_manager = ConfigManager()
        self.accessibility = AccessibilityService()
        self.auto_clicker = None
        self.is_running = False
        self.screen_width, self.screen_height = self.accessibility.get_screen_size()
        
        return self.layout
    
    def _request_permissions(self):
        """请求必要权限"""
        try:
            request_permissions([
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])
        except:
            pass
    
    def create_main_tab(self):
        """创建主控制标签页"""
        tab = TabbedPanelItem(text='主控制')
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 无障碍服务状态
        status_box = BoxLayout(size_hint_y=0.1, spacing=5)
        self.accessibility_status = Label(
            text='⚠️ 无障碍服务: 未启用',
            color=(1, 0.5, 0, 1)
        )
        status_box.add_widget(self.accessibility_status)
        
        btn_open_accessibility = Button(
            text='打开设置',
            size_hint_x=0.3,
            background_color=(0.5, 0.5, 1, 1)
        )
        btn_open_accessibility.bind(on_press=self.open_accessibility_settings)
        status_box.add_widget(btn_open_accessibility)
        layout.add_widget(status_box)
        
        # 屏幕信息
        screen_info = BoxLayout(size_hint_y=0.08)
        self.screen_info_label = Label(
            text=f'屏幕分辨率: {self.screen_width}x{self.screen_height}',
            halign='left'
        )
        screen_info.add_widget(self.screen_info_label)
        layout.add_widget(screen_info)
        
        # 脚本选择
        script_layout = BoxLayout(size_hint_y=0.1, spacing=5)
        script_layout.add_widget(Label(text='选择脚本:', size_hint_x=0.3))
        self.script_spinner = Spinner(
            text='智能自动点击器',
            values=['智能自动点击器', '四模式循环', '自定义脚本'],
            size_hint_x=0.7
        )
        script_layout.add_widget(self.script_spinner)
        layout.add_widget(script_layout)
        
        # 控制按钮组
        btn_layout = BoxLayout(orientation='vertical', spacing=10)
        
        # 开始按钮
        self.btn_start = Button(
            text='▶ 开始运行',
            size_hint_y=0.15,
            background_color=(0, 1, 0, 1),
            font_size=20
        )
        self.btn_start.bind(on_press=self.start_script)
        btn_layout.add_widget(self.btn_start)
        
        # 停止按钮
        self.btn_stop = Button(
            text='⏹ 停止运行',
            size_hint_y=0.15,
            background_color=(1, 0, 0, 1),
            font_size=20,
            disabled=True
        )
        self.btn_stop.bind(on_press=self.stop_script)
        btn_layout.add_widget(self.btn_stop)
        
        # 暂停/继续按钮
        self.btn_pause = Button(
            text='⏸ 暂停',
            size_hint_y=0.15,
            background_color=(1, 0.5, 0, 1),
            font_size=20,
            disabled=True
        )
        self.btn_pause.bind(on_press=self.pause_script)
        btn_layout.add_widget(self.btn_pause)
        
        layout.add_widget(btn_layout)
        
        # 运行状态显示
        status_display = BoxLayout(orientation='vertical', size_hint_y=0.2)
        self.run_status = Label(
            text='[b]运行状态[/b]\n\n等待启动...\n\n提示: 请先启用无障碍服务',
            markup=True,
            halign='center',
            valign='middle'
        )
        status_display.add_widget(self.run_status)
        layout.add_widget(status_display)
        
        tab.add_widget(layout)
        self.panel.add_widget(tab)
    
    def create_config_tab(self):
        """创建配置编辑标签页"""
        tab = TabbedPanelItem(text='配置')
        
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # 11步流程配置
        layout.add_widget(Label(text='[b][size=18]11步流程配置[/size][/b]', markup=True, size_hint_y=0.05))
        
        # 加载配置
        config = self.config_manager.load_config()
        buttons_config = config.get('buttons', {})
        
        # 步骤配置项
        self.config_inputs = {}
        steps = [
            ('login', '1. 登录', 641, 564),
            ('login_popup', '2. 关闭弹窗', 1190, 112),
            ('game_lobby', '3. 游戏大厅', 514, 544),
            ('match_screen', '4. 匹配', 398, 539),
            ('ai_mode_screen', '5. AI模式', 730, 601),
            ('start_game_screen', '6. 开始游戏', 1057, 569),
            ('prepare_screen', '7. 准备游戏', 775, 660),
            ('ready_game', '8. 准备进入', 640, 561),
            ('game_over', '9. 游戏结束', 635, 664),
            ('settlement_hero', '10. 结算英雄', 645, 621),
            ('return_room', '11. 返回房间', 739, 651)
        ]
        
        for step_key, step_name, default_x, default_y in steps:
            # 从配置读取或使用默认值
            saved = buttons_config.get(step_key, {})
            x_val = saved.get('x', default_x)
            y_val = saved.get('y', default_y)
            
            step_layout = BoxLayout(size_hint_y=0.06, spacing=5)
            step_layout.add_widget(Label(text=step_name, size_hint_x=0.3))
            
            x_input = TextInput(text=str(x_val), multiline=False, size_hint_x=0.25, input_filter='int')
            y_input = TextInput(text=str(y_val), multiline=False, size_hint_x=0.25, input_filter='int')
            
            self.config_inputs[step_key] = {'x': x_input, 'y': y_input}
            
            step_layout.add_widget(Label(text='X:', size_hint_x=0.05))
            step_layout.add_widget(x_input)
            step_layout.add_widget(Label(text='Y:', size_hint_x=0.05))
            step_layout.add_widget(y_input)
            
            layout.add_widget(step_layout)
        
        # 图像识别设置
        layout.add_widget(Label(text='', size_hint_y=0.03))
        layout.add_widget(Label(text='[b][size=18]图像识别设置[/size][/b]', markup=True, size_hint_y=0.05))
        
        # 图像识别开关
        image_switch_layout = BoxLayout(size_hint_y=0.06, spacing=5)
        image_switch_layout.add_widget(Label(text='启用图像识别:', size_hint_x=0.3))
        self.image_matching_spinner = Spinner(
            text='是' if settings.get('use_image_matching', True) else '否',
            values=['是', '否'],
            size_hint_x=0.7
        )
        image_switch_layout.add_widget(self.image_matching_spinner)
        layout.add_widget(image_switch_layout)
        
        # 匹配阈值
        threshold_layout = BoxLayout(size_hint_y=0.06, spacing=5)
        threshold_layout.add_widget(Label(text='匹配阈值(0-1):', size_hint_x=0.3))
        self.threshold_input = TextInput(text=str(settings.get('threshold', 0.7)), multiline=False, size_hint_x=0.7)
        threshold_layout.add_widget(self.threshold_input)
        layout.add_widget(threshold_layout)
        
        # 通用设置
        layout.add_widget(Label(text='', size_hint_y=0.03))
        layout.add_widget(Label(text='[b][size=18]通用设置[/size][/b]', markup=True, size_hint_y=0.05))
        
        # 等待时间
        wait_layout = BoxLayout(size_hint_y=0.06, spacing=5)
        wait_layout.add_widget(Label(text='等待时间(秒):', size_hint_x=0.3))
        self.wait_time_input = TextInput(text=str(settings.get('wait_time', 3)), multiline=False, size_hint_x=0.7)
        wait_layout.add_widget(self.wait_time_input)
        layout.add_widget(wait_layout)
        
        # 最大循环次数
        loop_layout = BoxLayout(size_hint_y=0.06, spacing=5)
        loop_layout.add_widget(Label(text='最大循环次数:', size_hint_x=0.3))
        self.max_loops_input = TextInput(text=str(settings.get('max_loops', 100)), multiline=False, size_hint_x=0.7)
        loop_layout.add_widget(self.max_loops_input)
        layout.add_widget(loop_layout)
        
        # 循环间隔
        interval_layout = BoxLayout(size_hint_y=0.06, spacing=5)
        interval_layout.add_widget(Label(text='循环间隔(秒):', size_hint_x=0.3))
        self.interval_input = TextInput(text=str(settings.get('interval', 5)), multiline=False, size_hint_x=0.7)
        interval_layout.add_widget(self.interval_input)
        layout.add_widget(interval_layout)
        
        # 保存按钮
        btn_save = Button(
            text='💾 保存配置',
            size_hint_y=0.08,
            background_color=(0, 1, 0, 1),
            font_size=16
        )
        btn_save.bind(on_press=self.save_config)
        layout.add_widget(btn_save)
        
        # 重置按钮
        btn_reset = Button(
            text='🔄 重置为默认',
            size_hint_y=0.08,
            background_color=(1, 0.5, 0, 1),
            font_size=16
        )
        btn_reset.bind(on_press=self.reset_config)
        layout.add_widget(btn_reset)
        
        scroll.add_widget(layout)
        tab.add_widget(scroll)
        self.panel.add_widget(tab)
    
    def create_permission_tab(self):
        """创建权限设置标签页"""
        tab = TabbedPanelItem(text='权限')
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        layout.add_widget(Label(
            text='[size=20][b]权限设置指南[/b][/size]',
            markup=True,
            size_hint_y=0.1
        ))
        
        # 无障碍服务
        accessibility_box = BoxLayout(orientation='vertical', size_hint_y=0.2, spacing=10)
        accessibility_box.add_widget(Label(
            text='[b]1. 无障碍服务 (必须)[/b]\n用于模拟点击和屏幕识别',
            markup=True,
            halign='left'
        ))
        btn_accessibility = Button(
            text='打开无障碍设置',
            background_color=(0.5, 0.5, 1, 1),
            font_size=16
        )
        btn_accessibility.bind(on_press=self.open_accessibility_settings)
        accessibility_box.add_widget(btn_accessibility)
        layout.add_widget(accessibility_box)
        
        # 悬浮窗权限
        overlay_box = BoxLayout(orientation='vertical', size_hint_y=0.2, spacing=10)
        overlay_box.add_widget(Label(
            text='[b]2. 悬浮窗权限 (推荐)[/b]\n用于显示控制悬浮窗',
            markup=True,
            halign='left'
        ))
        btn_overlay = Button(
            text='打开悬浮窗设置',
            background_color=(0.5, 0.5, 1, 1),
            font_size=16
        )
        btn_overlay.bind(on_press=self.open_overlay_settings)
        overlay_box.add_widget(btn_overlay)
        layout.add_widget(overlay_box)
        
        # 存储权限
        storage_box = BoxLayout(orientation='vertical', size_hint_y=0.2, spacing=10)
        storage_box.add_widget(Label(
            text='[b]3. 存储权限 (必须)[/b]\n用于保存配置和日志',
            markup=True,
            halign='left'
        ))
        btn_storage = Button(
            text='请求存储权限',
            background_color=(0.5, 0.5, 1, 1),
            font_size=16
        )
        btn_storage.bind(on_press=self.request_storage_permission)
        storage_box.add_widget(btn_storage)
        layout.add_widget(storage_box)
        
        # 状态显示
        self.permission_status = Label(
            text='[b]当前状态:[/b]\n检查权限状态...',
            markup=True,
            size_hint_y=0.2
        )
        layout.add_widget(self.permission_status)
        
        # 刷新按钮
        btn_refresh = Button(
            text='🔄 刷新权限状态',
            size_hint_y=0.1,
            background_color=(0.3, 0.3, 0.3, 1)
        )
        btn_refresh.bind(on_press=self.refresh_permission_status)
        layout.add_widget(btn_refresh)
        
        tab.add_widget(layout)
        self.panel.add_widget(tab)
    
    def create_log_tab(self):
        """创建日志查看标签页"""
        tab = TabbedPanelItem(text='日志')
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 日志文本框
        self.log_text = TextInput(
            text='[自动点击器日志]\n\n等待运行...\n',
            readonly=True,
            multiline=True,
            size_hint_y=0.85,
            font_name='DroidSansMono'
        )
        layout.add_widget(self.log_text)
        
        # 按钮组
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=5)
        
        btn_clear = Button(text='清空', background_color=(1, 0.5, 0, 1))
        btn_clear.bind(on_press=self.clear_log)
        btn_layout.add_widget(btn_clear)
        
        btn_export = Button(text='导出', background_color=(0.5, 0.5, 1, 1))
        btn_export.bind(on_press=self.export_log)
        btn_layout.add_widget(btn_export)
        
        layout.add_widget(btn_layout)
        
        tab.add_widget(layout)
        self.panel.add_widget(tab)
    
    def create_help_tab(self):
        """创建帮助信息标签页"""
        tab = TabbedPanelItem(text='帮助')
        
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        help_text = '''
[size=20][b]王者荣耀自动点击器 v2.0[/b][/size]
[b]Android原生版 - 使用无障碍服务[/b]

[color=ff0000][b]⚠️ 重要提示[/b][/color]
本应用使用Android无障碍服务实现自动化，
[b]必须先启用无障碍服务才能正常工作！[/b]

[b]使用步骤：[/b]
1. 切换到"权限"标签页
2. 点击"打开无障碍设置"
3. 找到"王者荣耀自动点击器"
4. 开启无障碍服务权限
5. 返回应用，开始使用

[b]11步流程说明：[/b]
① 登录 - 点击"开始游戏"
② 关闭弹窗 - 关闭活动弹窗
③ 游戏大厅 - 点击"对战"
④ 匹配 - 点击"王者峡谷"
⑤ AI模式 - 选择"人机"
⑥ 开始游戏 - 点击"开始"
⑦ 准备游戏 - 点击"准备"
⑧ 准备进入 - 确认进入
⑨ 游戏结束 - 确认结束
⑩ 结算英雄 - 查看结算
⑪ 返回房间 - 返回大厅

[b]配置说明：[/b]
• 坐标基于1280x720分辨率
• 自动适配不同屏幕尺寸
• 可在配置页面调整坐标
• 匹配阈值建议0.6-0.8

[b]注意事项：[/b]
⚠️ 仅用于学习研究目的
⚠️ 请勿用于违规操作
⚠️ 可能违反游戏服务条款

[b]常见问题：[/b]
Q: 点击无反应？
A: 检查无障碍服务是否开启

Q: 坐标不准？
A: 在配置页面调整坐标值

Q: 识别失败？
A: 降低匹配阈值或更新模板

[b]版本信息：[/b]
v2.0 - Android原生版
使用无障碍服务实现
支持Android 7.0+
        '''
        
        help_label = Label(
            text=help_text,
            markup=True,
            size_hint_y=None,
            halign='left',
            valign='top',
            text_size=(None, None)
        )
        help_label.bind(texture_size=help_label.setter('size'))
        
        layout.add_widget(help_label)
        scroll.add_widget(layout)
        tab.add_widget(scroll)
        self.panel.add_widget(tab)
    
    # ========== 控制方法 ==========
    
    def open_accessibility_settings(self, instance=None):
        """打开无障碍设置"""
        if ANDROID_AVAILABLE:
            self.accessibility.open_accessibility_settings()
            self.log('已打开无障碍设置页面')
        else:
            self.log('模拟模式: 无法打开无障碍设置')
    
    def open_overlay_settings(self, instance=None):
        """打开悬浮窗设置"""
        if ANDROID_AVAILABLE:
            try:
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION)
                mActivity.startActivity(intent)
                self.log('已打开悬浮窗设置')
            except Exception as e:
                self.log(f'打开悬浮窗设置失败: {e}')
    
    def request_storage_permission(self, instance=None):
        """请求存储权限"""
        if ANDROID_AVAILABLE:
            try:
                request_permissions([
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE
                ])
                self.log('已请求存储权限')
            except Exception as e:
                self.log(f'请求权限失败: {e}')
    
    def refresh_permission_status(self, instance=None):
        """刷新权限状态"""
        status_text = '[b]当前状态:[/b]\n'
        
        if ANDROID_AVAILABLE:
            # 检查无障碍服务
            if self.accessibility.is_connected:
                status_text += '✅ 无障碍服务: 已启用\n'
            else:
                status_text += '❌ 无障碍服务: 未启用\n'
            
            # 检查存储权限
            try:
                context = mActivity.getApplicationContext()
                if context.checkSelfPermission(Permission.WRITE_EXTERNAL_STORAGE) == 0:
                    status_text += '✅ 存储权限: 已授权\n'
                else:
                    status_text += '❌ 存储权限: 未授权\n'
            except:
                status_text += '⚠️ 存储权限: 无法检查\n'
        else:
            status_text += '⚠️ 运行在模拟模式\n'
        
        self.permission_status.text = status_text
        self.log('已刷新权限状态')
    
    def start_script(self, instance):
        """开始运行脚本"""
        # 检查无障碍服务
        if ANDROID_AVAILABLE and not self.accessibility.is_connected:
            popup = Popup(
                title='警告',
                content=Label(text='请先启用无障碍服务！\n\n在"权限"标签页中设置'),
                size_hint=(0.8, 0.4)
            )
            popup.open()
            return
        
        self.is_running = True
        self.btn_start.disabled = True
        self.btn_stop.disabled = False
        self.btn_pause.disabled = False
        
        self.update_status('运行中...')
        self.log('脚本开始运行')
        
        # 更新无障碍状态显示
        if self.accessibility.is_connected:
            self.accessibility_status.text = '✅ 无障碍服务: 已启用'
            self.accessibility_status.color = (0, 1, 0, 1)
        
        # 在后台线程运行脚本
        threading.Thread(target=self.run_script_thread, daemon=True).start()
    
    def run_script_thread(self):
        """脚本运行线程"""
        try:
            script_name = self.script_spinner.text
            self.log(f'运行脚本: {script_name}')
            
            # 获取配置
            config = self.config_manager.load_config()
            max_loops = int(self.max_loops_input.text) if self.max_loops_input.text.isdigit() else 100
            
            # 创建自动点击器实例
            self.auto_clicker = SmartAutoClicker(
                accessibility=self.accessibility,
                config=config,
                log_callback=self.log
            )
            
            # 运行脚本
            self.auto_clicker.run(max_loops=max_loops)
            
        except Exception as e:
            self.log(f'错误: {str(e)}')
            import traceback
            self.log(traceback.format_exc())
        finally:
            Clock.schedule_once(lambda dt: self.script_finished())
    
    def stop_script(self, instance):
        """停止运行脚本"""
        self.is_running = False
        if self.auto_clicker:
            self.auto_clicker.stop()
        
        self.update_status('已停止')
        self.log('脚本已停止')
        
        self.btn_start.disabled = False
        self.btn_stop.disabled = True
        self.btn_pause.disabled = True
    
    def pause_script(self, instance):
        """暂停/继续脚本"""
        if self.auto_clicker:
            if self.auto_clicker.is_paused:
                self.auto_clicker.resume()
                instance.text = '⏸ 暂停'
                self.update_status('运行中...')
                self.log('脚本继续运行')
            else:
                self.auto_clicker.pause()
                instance.text = '▶ 继续'
                self.update_status('已暂停')
                self.log('脚本已暂停')
    
    def script_finished(self):
        """脚本运行完成"""
        self.is_running = False
        self.btn_start.disabled = False
        self.btn_stop.disabled = True
        self.btn_pause.disabled = True
        self.btn_pause.text = '⏸ 暂停'
        
        self.update_status('完成')
        self.log('脚本运行完成')
    
    # ========== 配置方法 ==========
    
    def save_config(self, instance):
        """保存配置"""
        config = {
            'buttons': {},
            'settings': {
                'wait_time': float(self.wait_time_input.text) if self.wait_time_input.text else 3,
                'threshold': float(self.threshold_input.text) if self.threshold_input.text else 0.7,
                'max_loops': int(self.max_loops_input.text) if self.max_loops_input.text.isdigit() else 100,
                'interval': float(self.interval_input.text) if self.interval_input.text else 5,
                'use_image_matching': self.image_matching_spinner.text == '是'
            }
        }
        
        # 保存11步坐标
        for step_key, inputs in self.config_inputs.items():
            try:
                config['buttons'][step_key] = {
                    'x': int(inputs['x'].text) if inputs['x'].text else 0,
                    'y': int(inputs['y'].text) if inputs['y'].text else 0
                }
            except ValueError:
                config['buttons'][step_key] = {'x': 0, 'y': 0}
        
        self.config_manager.save_config(config)
        self.log('配置已保存')
        
        popup = Popup(
            title='成功',
            content=Label(text='配置已保存！'),
            size_hint=(0.6, 0.3)
        )
        popup.open()
    
    def reset_config(self, instance):
        """重置配置为默认值"""
        self.wait_time_input.text = '3'
        self.threshold_input.text = '0.7'
        self.max_loops_input.text = '100'
        self.interval_input.text = '5'
        
        default_coords = {
            'login': (641, 564),
            'login_popup': (1190, 112),
            'game_lobby': (514, 544),
            'match_screen': (398, 539),
            'ai_mode_screen': (730, 601),
            'start_game_screen': (1057, 569),
            'prepare_screen': (775, 660),
            'ready_game': (640, 561),
            'game_over': (635, 664),
            'settlement_hero': (645, 621),
            'return_room': (739, 651)
        }
        
        for step_key, (x, y) in default_coords.items():
            if step_key in self.config_inputs:
                self.config_inputs[step_key]['x'].text = str(x)
                self.config_inputs[step_key]['y'].text = str(y)
        
        self.log('配置已重置为默认值')
    
    # ========== 辅助方法 ==========
    
    def clear_log(self, instance):
        """清空日志"""
        self.log_text.text = '[自动点击器日志]\n\n'
        self.log('日志已清空')
    
    def export_log(self, instance):
        """导出日志"""
        try:
            log_path = os.path.join(os.getcwd(), 'autoclicker_log.txt')
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(self.log_text.text)
            self.log(f'日志已导出到: {log_path}')
        except Exception as e:
            self.log(f'导出失败: {e}')
    
    def log(self, message):
        """添加日志"""
        timestamp = time.strftime('%H:%M:%S')
        Clock.schedule_once(lambda dt: self._append_log(f'[{timestamp}] {message}'))
    
    def _append_log(self, text):
        """在主线程添加日志"""
        self.log_text.text += text + '\n'
    
    def update_status(self, status):
        """更新状态"""
        Clock.schedule_once(lambda dt: self._set_status(status))
    
    def _set_status(self, status):
        """在主线程更新状态"""
        self.status_label.text = f'状态: {status}'
        if status == '运行中...':
            self.status_label.color = (0, 1, 0, 1)
            self.run_status.text = '[b]运行状态[/b]\n\n✅ 正在运行...\n\n点击"停止"可中止'
        elif status == '已暂停':
            self.status_label.color = (1, 0.5, 0, 1)
            self.run_status.text = '[b]运行状态[/b]\n\n⏸ 已暂停\n\n点击"继续"恢复运行'
        elif status == '已停止':
            self.status_label.color = (1, 0, 0, 1)
            self.run_status.text = '[b]运行状态[/b]\n\n⏹ 已停止\n\n点击"开始"重新运行'
        elif status == '完成':
            self.status_label.color = (0, 1, 0, 1)
            self.run_status.text = '[b]运行状态[/b]\n\n✅ 运行完成\n\n可以开始新一轮'


if __name__ == '__main__':
    AutoClickerApp().run()
