#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
王者荣耀自动点击器 - 基础版
功能：坐标点击（无OpenCV，确保能构建成功）
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
from kivy.core.window import Window
import json
import os
import threading
import time

# === 修复：初始化属性，防止启动崩溃 ===
# 必须在导入后立即设置，避免后续代码访问未初始化的属性


class AutoClickerApp(App):
    """主应用类 - 基础版"""

    title = "王者荣耀自动点击器"
    use_kivy_settings = True

    def build(self):
        """构建应用界面"""

        # === 关键修复：先初始化所有属性 ===
        self.screen_width = Window.width if Window else 720
        self.screen_height = Window.height if Window else 1280
        self.orientation = 'portrait'
        self.is_running = False
        self.is_paused = False
        self.current_step = 0

        # 绑定窗口大小变化
        if Window:
            Window.bind(on_resize=self._on_window_resize)
            Window.bind(on_keyboard=self._on_keyboard)

        # 主布局
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 标题
        title_label = Label(
            text='[size=20][b]王者荣耀自动点击器[/b][/size]\n'
                 '[size=12]基础版 - 坐标点击[/size]',
            markup=True,
            size_hint_y=0.08
        )
        self.layout.add_widget(title_label)

        # 创建Tab面板
        self.panel = TabbedPanel(tab_pos='top_left')

        # Tab 1: 主控制
        self.create_main_tab()

        # Tab 2: 配置
        self.create_config_tab()

        # Tab 3: 日志
        self.create_log_tab()

        # Tab 4: 帮助
        self.create_help_tab()

        self.layout.add_widget(self.panel)

        # 状态栏
        self.status_label = Label(
            text='状态: 就绪',
            size_hint_y=0.05,
            color=(0, 1, 0, 1)
        )
        self.layout.add_widget(self.status_label)

        # 加载配置
        self.load_config()

        # 延迟检测设备
        Clock.schedule_once(lambda dt: self.log_message("基础版已启动，等待操作..."), 1)

        return self.layout

    def _on_window_resize(self, instance, width, height):
        """窗口大小变化处理"""
        self.screen_width = width
        self.screen_height = height
        self.orientation = 'landscape' if width > height else 'portrait'
        self.log_message(f"屏幕方向变化: {self.orientation} ({width}x{height})")

    def _on_keyboard(self, window, key, *args):
        """键盘事件处理"""
        # ESC键停止运行
        if key == 27 and self.is_running:
            self.stop_script(None)
            return True
        return False

    def _get_config_path(self):
        """获取配置文件路径"""
        if hasattr(self, 'user_data_dir'):
            config_dir = self.user_data_dir
        else:
            config_dir = os.path.expanduser('~/.wangzhe_autoclicker')
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, 'config.json')

    def create_main_tab(self):
        """创建主控制标签页"""
        tab = TabbedPanelItem(text='主控制')

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 脚本选择
        script_layout = BoxLayout(size_hint_y=0.1, spacing=5)
        script_layout.add_widget(Label(text='选择脚本:', size_hint_x=0.3))
        self.script_spinner = Spinner(
            text='11步流程',
            values=['11步流程', '快速测试', '自定义脚本'],
            size_hint_x=0.7
        )
        script_layout.add_widget(self.script_spinner)
        layout.add_widget(script_layout)

        # 参数设置
        params_layout = BoxLayout(size_hint_y=0.1, spacing=5)
        params_layout.add_widget(Label(text='循环次数:', size_hint_x=0.2))
        self.loop_input = TextInput(text='999', multiline=False, size_hint_x=0.2)
        params_layout.add_widget(self.loop_input)
        params_layout.add_widget(Label(text='等待(秒):', size_hint_x=0.2))
        self.wait_input = TextInput(text='2', multiline=False, size_hint_x=0.2)
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

        # 当前步骤显示
        self.step_label = Label(
            text='当前步骤: 无',
            size_hint_y=0.1,
            halign='left',
            valign='middle'
        )
        self.step_label.bind(size=self.step_label.setter('text_size'))
        layout.add_widget(self.step_label)

        tab.add_widget(layout)
        self.panel.add_widget(tab)

    def create_config_tab(self):
        """创建配置标签页"""
        tab = TabbedPanelItem(text='配置')

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 配置编辑器
        self.config_text = TextInput(
            text=self.get_default_config(),
            multiline=True,
            size_hint_y=0.8
        )
        layout.add_widget(self.config_text)

        # 按钮
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=5)
        btn_load = Button(text='重新加载')
        btn_load.bind(on_press=lambda x: self.load_config())
        btn_layout.add_widget(btn_load)

        btn_save = Button(text='保存配置')
        btn_save.bind(on_press=self.save_config)
        btn_layout.add_widget(btn_save)

        btn_reset = Button(text='重置默认')
        btn_reset.bind(on_press=lambda x: setattr(self.config_text, 'text', self.get_default_config()))
        btn_layout.add_widget(btn_reset)

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

        help_text = """[size=16][b]王者荣耀自动点击器 - 基础版[/b][/size]

[size=14][b]功能说明[/b][/size]
• 11步自动化流程
• 坐标点击模式
• 可配置坐标和等待时间

[size=14][b]使用说明[/b][/size]
1. 在"配置"标签页设置坐标
2. 在"主控制"标签页点击"开始"
3. 按 ESC 或点击"停止"结束

[size=14][b]11步流程[/b][/size]
1. 登录 - 点击"开始游戏"
2. 关闭弹窗 - 关闭活动弹窗
3. 游戏大厅 - 点击"对战"
4. 匹配 - 点击"王者峡谷"
5. AI模式 - 选择"人机"
6. 开始游戏 - 点击"开始"
7. 准备游戏 - 点击"准备"
8. 准备进入 - 确认进入游戏
9. 游戏中 - 等待游戏结束
10. 游戏结束 - 确认结束
11. 结算英雄 - 查看结算

[size=14][b]注意事项[/b][/size]
• 需要授予无障碍服务权限
• 需要授予悬浮窗权限
• 基准分辨率: 1280x720
• 其他分辨率需调整坐标

[size=14][b]版本信息[/b][/size]
版本: v3.0 (基础版)
功能: 坐标点击
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

    def get_default_config(self):
        """获取默认配置"""
        config = {
            "steps": [
                {"name": "登录", "x": 641, "y": 564, "wait": 3, "desc": "点击开始游戏"},
                {"name": "关闭弹窗", "x": 1190, "y": 112, "wait": 2, "desc": "关闭活动弹窗"},
                {"name": "游戏大厅", "x": 514, "y": 544, "wait": 2, "desc": "点击对战"},
                {"name": "匹配", "x": 398, "y": 539, "wait": 2, "desc": "点击王者峡谷"},
                {"name": "AI模式", "x": 730, "y": 601, "wait": 2, "desc": "选择人机"},
                {"name": "开始游戏", "x": 1057, "y": 569, "wait": 3, "desc": "点击开始"},
                {"name": "准备游戏", "x": 775, "y": 660, "wait": 2, "desc": "点击准备"},
                {"name": "准备进入", "x": 640, "y": 561, "wait": 10, "desc": "确认进入游戏"},
                {"name": "游戏中", "x": 640, "y": 360, "wait": 60, "desc": "等待游戏结束"},
                {"name": "游戏结束", "x": 635, "y": 664, "wait": 2, "desc": "确认结束"},
                {"name": "结算英雄", "x": 645, "y": 621, "wait": 3, "desc": "查看结算"}
            ],
            "settings": {
                "loop_count": 999,
                "default_wait": 2
            }
        }
        return json.dumps(config, indent=2, ensure_ascii=False)

    def load_config(self):
        """加载配置"""
        try:
            config_path = self._get_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.config_text.text = json.dumps(config, indent=2, ensure_ascii=False)
                    self.log_message("配置已加载")
            else:
                self.config_text.text = self.get_default_config()
                self.log_message("使用默认配置")
        except Exception as e:
            self.log_message(f"加载配置失败: {e}")

    def save_config(self, instance):
        """保存配置"""
        try:
            config = json.loads(self.config_text.text)
            config_path = self._get_config_path()
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.log_message("配置已保存")
        except json.JSONDecodeError as e:
            self.log_message(f"配置格式错误: {e}")
        except Exception as e:
            self.log_message(f"保存配置失败: {e}")

    def log_message(self, message):
        """记录日志"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.text += f"\n[{timestamp}] {message}"
        print(f"[{timestamp}] {message}")

    def start_script(self, instance):
        """开始运行脚本"""
        if self.is_running:
            self.log_message("脚本已在运行")
            return

        self.is_running = True
        self.is_paused = False
        self.current_step = 0

        self.btn_start.disabled = True
        self.btn_pause.disabled = False
        self.btn_stop.disabled = False
        self.status_label.text = '状态: 运行中'
        self.status_label.color = (0, 1, 0, 1)

        self.log_message("开始运行脚本")

        # 启动脚本线程
        self.script_thread = threading.Thread(target=self.run_script, daemon=True)
        self.script_thread.start()

    def run_script(self):
        """运行脚本（线程函数）"""
        try:
            # 加载配置
            config = json.loads(self.config_text.text)
            steps = config.get('steps', [])
            loop_count = int(self.loop_input.text)
            default_wait = int(self.wait_input.text)

            for loop in range(loop_count):
                if not self.is_running:
                    break

                self.log_message(f"第 {loop + 1}/{loop_count} 次循环")

                for i, step in enumerate(steps):
                    if not self.is_running:
                        break

                    while self.is_paused:
                        time.sleep(0.1)

                    self.current_step = i + 1
                    step_name = step.get('name', f'步骤{i+1}')
                    x = step.get('x', 640)
                    y = step.get('y', 360)
                    wait = step.get('wait', default_wait)

                    # 更新UI（需要在主线程）
                    Clock.schedule_once(
                        lambda dt, s=step_name: setattr(
                            self.step_label, 'text', f'当前步骤: {s}'
                        ),
                        0
                    )

                    self.log_message(f"执行: {step_name} ({x}, {y})")

                    # TODO: 这里添加实际的点击逻辑
                    # 使用无障碍服务或ADB进行点击
                    # click(x, y)

                    time.sleep(wait)

                if not self.is_running:
                    break

            self.log_message("脚本执行完成")

        except Exception as e:
            self.log_message(f"脚本执行错误: {e}")

        finally:
            # 更新UI（需要在主线程）
            Clock.schedule_once(self._script_finished, 0)

    def _script_finished(self, dt):
        """脚本结束"""
        self.is_running = False
        self.btn_start.disabled = False
        self.btn_pause.disabled = True
        self.btn_stop.disabled = True
        self.btn_pause.text = '⏸ 暂停'
        self.status_label.text = '状态: 就绪'
        self.step_label.text = '当前步骤: 无'

    def pause_script(self, instance):
        """暂停/继续脚本"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.text = '▶ 继续'
            self.status_label.text = '状态: 已暂停'
            self.status_label.color = (1, 0.5, 0, 1)
            self.log_message("脚本已暂停")
        else:
            self.btn_pause.text = '⏸ 暂停'
            self.status_label.text = '状态: 运行中'
            self.status_label.color = (0, 1, 0, 1)
            self.log_message("脚本继续运行")

    def stop_script(self, instance):
        """停止脚本"""
        self.is_running = False
        self.is_paused = False
        self.btn_start.disabled = False
        self.btn_pause.disabled = True
        self.btn_stop.disabled = True
        self.btn_pause.text = '⏸ 暂停'
        self.status_label.text = '状态: 已停止'
        self.status_label.color = (1, 0, 0, 1)
        self.step_label.text = '当前步骤: 无'
        self.log_message("脚本已停止")


if __name__ == '__main__':
    AutoClickerApp().run()
