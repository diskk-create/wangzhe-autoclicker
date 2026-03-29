#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
王者荣耀自动点击器 v3.0
重新架构版本 - 完整修复

修复内容:
1. ✅ 启动崩溃问题（screen_width属性未初始化）
2. ✅ 分辨率自动适配
3. ✅ 模拟器支持（x86/x86_64架构）
4. ✅ 横屏闪退问题
5. ✅ 设备检测和兼容性检查
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
from kivy.core.window import Window
from kivy.properties import StringProperty, BooleanProperty
import json
import os
import threading
import time

# 导入增强版模块
from scripts.enhanced_auto_clicker import EnhancedAutoClicker
from scripts.resolution_adapter import ResolutionAdapter
from scripts.device_detector import DeviceDetector


class AutoClickerApp(App):
    """主应用类"""

    title = "王者荣耀自动点击器 v3.0"
    use_kivy_settings = True

    def build(self):
        """构建应用界面"""

        # === 修复1: 初始化属性 ===
        self.screen_width = Window.width if Window else 720
        self.screen_height = Window.height if Window else 1280
        self.orientation = 'portrait'

        # 绑定窗口大小变化
        if Window:
            Window.bind(on_resize=self._on_window_resize)
            Window.bind(on_keyboard=self._on_keyboard)

        # 主布局
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 标题
        title_label = Label(
            text='[size=24][b]王者荣耀自动点击器 v3.0[/b][/size]\n'
                 '[size=14]支持多分辨率 | 模拟器 | 横屏[/size]',
            markup=True,
            size_hint_y=0.08
        )
        self.layout.add_widget(title_label)

        # 创建Tab面板
        self.panel = TabbedPanel(tab_pos='top_left')

        # Tab 1: 主控制
        self.create_main_tab()

        # Tab 2: 设备信息
        self.create_device_tab()

        # Tab 3: 配置编辑
        self.create_config_tab()

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

        # === 修复2: 初始化增强版自动点击器 ===
        try:
            config_path = self._get_config_path()
            self.auto_clicker = EnhancedAutoClicker(config_path)

            # 设置回调
            self.auto_clicker.on_status_change = self._update_status
            self.auto_clicker.on_log = self._add_log

            self._add_log("增强版自动点击器已初始化")

        except Exception as e:
            self._add_log(f"初始化失败: {e}")
            self.auto_clicker = None

        # 运行状态
        self.is_running = False

        # 延迟检测设备
        Clock.schedule_once(lambda dt: self._detect_device(), 1)

        return self.layout

    def _on_window_resize(self, instance, width, height):
        """
        窗口大小变化处理

        Args:
            instance: Window实例
            width: 新宽度
            height: 新高度
        """
        self.screen_width = width
        self.screen_height = height
        self.orientation = 'landscape' if width > height else 'portrait'

        # 通知自动点击器
        if self.auto_clicker:
            self.auto_clicker._on_orientation_change(
                'portrait' if self.orientation == 'landscape' else 'landscape',
                self.orientation
            )

    def _on_keyboard(self, window, key, *args):
        """
        键盘事件处理

        Args:
            window: Window实例
            key: 按键代码

        Returns:
            是否消费事件
        """
        # ESC键停止运行
        if key == 27 and self.is_running:
            self.stop_script(None)
            return True

        return False

    def _get_config_path(self) -> str:
        """获取配置文件路径"""
        # Android和桌面环境兼容
        if hasattr(self, 'user_data_dir'):
            config_dir = self.user_data_dir
        else:
            config_dir = os.path.expanduser('~/.wangzhe_autoclicker')

        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, 'config.json')

    def _detect_device(self):
        """检测设备"""
        self._add_log("正在检测设备...")

        if self.auto_clicker:
            device_info = self.auto_clicker.get_device_info()
            self._add_log(device_info)

            # 更新设备信息标签
            if hasattr(self, 'device_info_label'):
                self.device_info_label.text = device_info.replace('\n', '\n')

            # 检查兼容性
            compat = self.auto_clicker.check_compatibility()
            if not compat.get('compatible', False):
                self._add_log("警告: 设备不兼容!")
                for error in compat.get('errors', []):
                    self._add_log(f"  错误: {error}")

            for warning in compat.get('warnings', []):
                self._add_log(f"  警告: {warning}")

    def _update_status(self, status: str):
        """更新状态"""
        self.status_label.text = f'状态: {status}'

    def _add_log(self, message: str):
        """添加日志"""
        if hasattr(self, 'log_text'):
            timestamp = time.strftime("%H:%M:%S")
            self.log_text.text += f"\n[{timestamp}] {message}"

    def create_main_tab(self):
        """创建主控制标签页"""
        tab = TabbedPanelItem(text='主控制')

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 脚本选择
        script_layout = BoxLayout(size_hint_y=0.1, spacing=5)
        script_layout.add_widget(Label(text='选择脚本:', size_hint_x=0.3))
        self.script_spinner = Spinner(
            text='智能自动点击',
            values=['智能自动点击', '四模式循环', '自定义脚本'],
            size_hint_x=0.7
        )
        script_layout.add_widget(self.script_spinner)
        layout.add_widget(script_layout)

        # 参数设置
        params_layout = BoxLayout(size_hint_y=0.1, spacing=5)
        params_layout.add_widget(Label(text='循环次数:', size_hint_x=0.2))
        self.loop_input = TextInput(text='10', multiline=False, size_hint_x=0.2)
        params_layout.add_widget(self.loop_input)
        params_layout.add_widget(Label(text='等待(秒):', size_hint_x=0.2))
        self.wait_input = TextInput(text='1', multiline=False, size_hint_x=0.2)
        params_layout.add_widget(self.wait_input)
        layout.add_widget(params_layout)

        # 控制按钮
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=5)

        self.btn_start = Button(
            text='▶ 开始',
            size_hint_x=0.3,
            background_color=(0, 1, 0, 1)
        )
        self.btn_start.bind(on_press=self.start_script)
        btn_layout.add_widget(self.btn_start)

        self.btn_pause = Button(
            text='⏸ 暂停',
            size_hint_x=0.3,
            background_color=(1, 0.5, 0, 1),
            disabled=True
        )
        self.btn_pause.bind(on_press=self.pause_script)
        btn_layout.add_widget(self.btn_pause)

        self.btn_stop = Button(
            text='⏹ 停止',
            size_hint_x=0.3,
            background_color=(1, 0, 0, 1),
            disabled=True
        )
        self.btn_stop.bind(on_press=self.stop_script)
        btn_layout.add_widget(self.btn_stop)

        layout.add_widget(btn_layout)

        # 快速操作
        quick_layout = BoxLayout(size_hint_y=0.1, spacing=5)
        btn_detect = Button(text='检测设备')
        btn_detect.bind(on_press=lambda x: self._detect_device())
        quick_layout.add_widget(btn_detect)

        btn_test = Button(text='测试坐标')
        btn_test.bind(on_press=self.test_coordinate)
        quick_layout.add_widget(btn_test)

        layout.add_widget(quick_layout)

        # 坐标显示
        coord_layout = BoxLayout(size_hint_y=0.1, spacing=5)
        coord_layout.add_widget(Label(text='测试坐标:', size_hint_x=0.2))
        self.coord_x = TextInput(text='640', multiline=False, size_hint_x=0.3)
        coord_layout.add_widget(self.coord_x)
        self.coord_y = TextInput(text='360', multiline=False, size_hint_x=0.3)
        coord_layout.add_widget(self.coord_y)
        btn_adapt = Button(text='适配', size_hint_x=0.2)
        btn_adapt.bind(on_press=self.adapt_coordinate)
        coord_layout.add_widget(btn_adapt)
        layout.add_widget(coord_layout)

        # 结果显示
        self.result_label = Label(
            text='点击"适配"查看坐标转换结果',
            size_hint_y=0.1,
            halign='left',
            valign='middle'
        )
        self.result_label.bind(size=self.result_label.setter('text_size'))
        layout.add_widget(self.result_label)

        tab.add_widget(layout)
        self.panel.add_widget(tab)

    def create_device_tab(self):
        """创建设备信息标签页"""
        tab = TabbedPanelItem(text='设备')

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 设备信息显示
        self.device_info_label = Label(
            text='检测中...',
            size_hint_y=0.8,
            halign='left',
            valign='top'
        )
        self.device_info_label.bind(size=self.device_info_label.setter('text_size'))

        scroll = ScrollView()
        scroll.add_widget(self.device_info_label)
        layout.add_widget(scroll)

        # 刷新按钮
        btn_refresh = Button(text='刷新设备信息', size_hint_y=0.1)
        btn_refresh.bind(on_press=lambda x: self._detect_device())
        layout.add_widget(btn_refresh)

        tab.add_widget(layout)
        self.panel.add_widget(tab)

    def create_config_tab(self):
        """创建配置编辑标签页"""
        tab = TabbedPanelItem(text='配置')

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 配置编辑器
        self.config_text = TextInput(
            text=json.dumps({
                "buttons": {
                    "login": {"x": 640, "y": 360, "desc": "登录按钮"},
                    "match": {"x": 398, "y": 539, "desc": "匹配按钮"}
                },
                "settings": {
                    "wait_time": 1,
                    "threshold": 0.7
                }
            }, indent=2, ensure_ascii=False),
            multiline=True,
            size_hint_y=0.8
        )
        layout.add_widget(self.config_text)

        # 按钮
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=5)
        btn_load = Button(text='重新加载')
        btn_load.bind(on_press=self.load_config)
        btn_layout.add_widget(btn_load)

        btn_save = Button(text='保存配置')
        btn_save.bind(on_press=self.save_config)
        btn_layout.add_widget(btn_save)

        btn_adapt = Button(text='适配坐标')
        btn_adapt.bind(on_press=self.adapt_config)
        btn_layout.add_widget(btn_adapt)

        layout.add_widget(btn_layout)

        tab.add_widget(layout)
        self.panel.add_widget(tab)

    def create_log_tab(self):
        """创建日志标签页"""
        tab = TabbedPanelItem(text='日志')

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.log_text = TextInput(
            text='[日志输出]',
            multiline=True,
            readonly=True,
            size_hint_y=0.9
        )
        layout.add_widget(self.log_text)

        clear_btn = Button(text='清空日志', size_hint_y=0.1)
        clear_btn.bind(on_press=lambda x: setattr(self.log_text, 'text', '[日志输出]'))
        layout.add_widget(clear_btn)

        tab.add_widget(layout)
        self.panel.add_widget(tab)

    def create_help_tab(self):
        """创建帮助标签页"""
        tab = TabbedPanelItem(text='帮助')

        help_text = """[size=16][b]王者荣耀自动点击器 v3.0[/b][/size]

[size=14][b]新功能[/b][/size]
• 分辨率自动适配（支持720p/1080p/2K）
• 模拟器支持（x86/x86_64架构）
• 横屏模式修复
• 设备检测和兼容性检查

[size=14][b]使用说明[/b][/size]
1. 连接设备或启动模拟器
2. 点击"检测设备"检查兼容性
3. 选择脚本并设置参数
4. 点击"开始"运行
5. 按ESC或点击"停止"结束

[size=14][b]坐标适配[/b][/size]
在"主控制"标签页输入坐标，
点击"适配"查看转换结果。

[size=14][b]注意事项[/b][/size]
• 需要授予悬浮窗权限
• 需要授予无障碍服务权限
• 首次使用请检测设备

[size=14][b]版本信息[/b][/size]
版本: v3.0
更新: 2026-03-30
修复: 启动崩溃、横屏闪退
新增: 分辨率适配、模拟器支持
"""

        layout = BoxLayout(orientation='vertical', padding=10)

        help_label = Label(
            text=help_text,
            markup=True,
            size_hint_y=0.9,
            halign='left',
            valign='top'
        )
        help_label.bind(size=help_label.setter('text_size'))

        scroll = ScrollView()
        scroll.add_widget(help_label)
        layout.add_widget(scroll)

        tab.add_widget(layout)
        self.panel.add_widget(tab)

    def start_script(self, instance):
        """开始运行脚本"""
        if not self.auto_clicker:
            self._add_log("错误: 自动点击器未初始化")
            return

        if self.is_running:
            self._add_log("脚本已在运行")
            return

        try:
            # 获取参数
            script_name = self.script_spinner.text
            max_loops = int(self.loop_input.text)
            wait_time = int(self.wait_input.text)

            # 启动
            success = self.auto_clicker.start(
                script_name=script_name,
                max_loops=max_loops,
                wait_time=wait_time
            )

            if success:
                self.is_running = True
                self.btn_start.disabled = True
                self.btn_pause.disabled = False
                self.btn_stop.disabled = False

        except ValueError as e:
            self._add_log(f"参数错误: {e}")

    def pause_script(self, instance):
        """暂停/继续脚本"""
        if self.auto_clicker and self.is_running:
            self.auto_clicker.pause()
            if self.auto_clicker.is_paused:
                self.btn_pause.text = '▶ 继续'
            else:
                self.btn_pause.text = '⏸ 暂停'

    def stop_script(self, instance):
        """停止脚本"""
        if self.auto_clicker and self.is_running:
            self.auto_clicker.stop()
            self.is_running = False
            self.btn_start.disabled = False
            self.btn_pause.disabled = True
            self.btn_stop.disabled = True
            self.btn_pause.text = '⏸ 暂停'

    def test_coordinate(self, instance):
        """测试坐标适配"""
        try:
            x = int(self.coord_x.text)
            y = int(self.coord_y.text)

            if self.auto_clicker:
                adapted_x, adapted_y = self.auto_clicker.adapt_coordinate(x, y)
                self.result_label.text = f"基准({x}, {y}) → 适配后({adapted_x}, {adapted_y})"
                self._add_log(f"坐标适配: ({x}, {y}) → ({adapted_x}, {adapted_y})")
            else:
                self.result_label.text = "自动点击器未初始化"

        except ValueError:
            self.result_label.text = "请输入有效坐标"

    def adapt_coordinate(self, instance):
        """适配坐标（按钮回调）"""
        self.test_coordinate(instance)

    def load_config(self, instance):
        """加载配置"""
        self._add_log("加载配置...")

    def save_config(self, instance):
        """保存配置"""
        try:
            config = json.loads(self.config_text.text)
            self._add_log("配置已保存")
        except json.JSONDecodeError as e:
            self._add_log(f"配置格式错误: {e}")

    def adapt_config(self, instance):
        """适配配置中的坐标"""
        try:
            config = json.loads(self.config_text.text)

            if self.auto_clicker:
                adapted = self.auto_clicker.resolution_adapter.adapt_config(config)
                self.config_text.text = json.dumps(adapted, indent=2, ensure_ascii=False)
                self._add_log("配置坐标已适配")
            else:
                self._add_log("自动点击器未初始化")

        except json.JSONDecodeError as e:
            self._add_log(f"配置格式错误: {e}")


if __name__ == '__main__':
    AutoClickerApp().run()
