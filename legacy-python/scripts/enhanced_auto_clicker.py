#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版自动点击器
集成分辨率适配、设备检测和横屏处理
"""

import time
import threading
from typing import Optional, Dict, List, Tuple

from .resolution_adapter import ResolutionAdapter
from .device_detector import DeviceDetector
from .float_window_manager import FloatWindowManager


class EnhancedAutoClicker:
    """增强版自动点击器"""

    def __init__(self, config_path: str = None):
        """
        初始化增强版自动点击器

        Args:
            config_path: 配置文件路径
        """
        # 核心组件
        self.resolution_adapter = ResolutionAdapter(config_path)
        self.device_detector = DeviceDetector()
        self.float_window_manager = FloatWindowManager.get_instance()

        # 运行状态
        self.is_running = False
        self.is_paused = False
        self.stop_flag = False

        # 点击线程
        self.click_thread = None

        # 设备信息
        self.device_info = None
        self.compatibility_check = None

        # 回调
        self.on_status_change = None
        self.on_log = None

        # 初始化
        self._initialize()

    def _initialize(self):
        """初始化组件"""
        try:
            # 检测设备
            devices = self.device_detector.get_connected_devices()
            if devices:
                self.device_info = devices[0]
                self.compatibility_check = self.device_detector.check_compatibility(
                    self.device_info.get('device_id')
                )

                # 设置分辨率适配器
                self.resolution_adapter.current_width = self.device_info.get('screen_width', 720)
                self.resolution_adapter.current_height = self.device_info.get('screen_height', 1280)
                self.resolution_adapter.is_landscape = (
                    self.resolution_adapter.current_width > self.resolution_adapter.current_height
                )
                self.resolution_adapter.update_device_info()

                self._log(f"设备已连接: {self.device_info.get('model', 'unknown')}")
                self._log(self.resolution_adapter.get_device_info_string())

                # 检查兼容性
                if not self.compatibility_check.get('compatible', False):
                    self._log("警告: 设备不兼容!")
                    for error in self.compatibility_check.get('errors', []):
                        self._log(f"  错误: {error}")

                # 显示警告
                for warning in self.compatibility_check.get('warnings', []):
                    self._log(f"  警告: {warning}")
            else:
                self._log("警告: 未检测到设备")

            # 设置配置变化回调
            self.float_window_manager.set_on_config_change_callback(
                self._on_orientation_change
            )

        except Exception as e:
            self._log(f"初始化失败: {e}")

    def _log(self, message: str):
        """
        记录日志

        Args:
            message: 日志消息
        """
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"

        if self.on_log:
            self.on_log(log_message)

        print(log_message)

    def _update_status(self, status: str):
        """
        更新状态

        Args:
            status: 状态消息
        """
        if self.on_status_change:
            self.on_status_change(status)

    def _on_orientation_change(self, old_orientation: str, new_orientation: str):
        """
        处理屏幕方向变化

        Args:
            old_orientation: 旧方向
            new_orientation: 新方向
        """
        self._log(f"屏幕方向变化: {old_orientation} -> {new_orientation}")

        # 重新检测分辨率
        self.resolution_adapter.detect_resolution()

        # 更新设备信息
        if self.device_info:
            self.resolution_adapter.current_width = self.device_info.get('screen_width', 720)
            self.resolution_adapter.current_height = self.device_info.get('screen_height', 1280)
            self.resolution_adapter.update_device_info()

        self._log(f"新分辨率: {self.resolution_adapter.current_width}x{self.resolution_adapter.current_height}")

    def adapt_coordinate(self, x: int, y: int) -> Tuple[int, int]:
        """
        适配坐标

        Args:
            x: X坐标
            y: Y坐标

        Returns:
            适配后的(x, y)坐标
        """
        return self.resolution_adapter.adapt_coordinate(x, y)

    def get_device_info(self) -> str:
        """
        获取设备信息

        Returns:
            设备信息字符串
        """
        if self.device_info:
            return self.device_detector.get_device_info_string(
                self.device_info.get('device_id')
            )
        return "未检测到设备"

    def check_compatibility(self) -> Dict:
        """
        检查兼容性

        Returns:
            兼容性检查结果
        """
        return self.compatibility_check or {
            'compatible': False,
            'errors': ['设备未连接'],
            'warnings': []
        }

    def start(self, script_name: str = 'default', **kwargs):
        """
        开始运行脚本

        Args:
            script_name: 脚本名称
            **kwargs: 脚本参数
        """
        if self.is_running:
            self._log("脚本已在运行")
            return False

        # 检查兼容性
        if self.compatibility_check and not self.compatibility_check.get('compatible'):
            self._log("设备不兼容，无法运行")
            return False

        self.is_running = True
        self.is_paused = False
        self.stop_flag = False

        self._update_status("运行中")
        self._log(f"开始运行脚本: {script_name}")

        # 启动点击线程
        self.click_thread = threading.Thread(
            target=self._run_script,
            args=(script_name,),
            kwargs=kwargs,
            daemon=True
        )
        self.click_thread.start()

        return True

    def _run_script(self, script_name: str, **kwargs):
        """
        运行脚本（线程函数）

        Args:
            script_name: 脚本名称
            **kwargs: 脚本参数
        """
        try:
            self._log("脚本线程已启动")

            # 示例：简单的点击循环
            max_loops = kwargs.get('max_loops', 10)
            wait_time = kwargs.get('wait_time', 1)

            for i in range(max_loops):
                if self.stop_flag:
                    self._log("用户停止脚本")
                    break

                while self.is_paused:
                    time.sleep(0.1)

                self._log(f"执行第 {i+1}/{max_loops} 次循环")

                # 这里添加实际的点击逻辑
                # 使用 self.adapt_coordinate() 适配坐标

                time.sleep(wait_time)

            self._log("脚本执行完成")

        except Exception as e:
            self._log(f"脚本执行错误: {e}")

        finally:
            self.is_running = False
            self._update_status("就绪")

    def pause(self):
        """暂停脚本"""
        if not self.is_running:
            return False

        self.is_paused = not self.is_paused
        status = "已暂停" if self.is_paused else "运行中"
        self._update_status(status)
        self._log(f"脚本{status}")

        return True

    def stop(self):
        """停止脚本"""
        if not self.is_running:
            return False

        self.stop_flag = True
        self.is_running = False
        self.is_paused = False

        self._update_status("已停止")
        self._log("停止脚本")

        return True

    def get_status(self) -> Dict:
        """
        获取状态

        Returns:
            状态字典
        """
        return {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'device_info': self.device_info,
            'resolution': {
                'width': self.resolution_adapter.current_width,
                'height': self.resolution_adapter.current_height,
                'orientation': 'landscape' if self.resolution_adapter.is_landscape else 'portrait'
            },
            'float_window': self.float_window_manager.get_status()
        }


if __name__ == '__main__':
    # 测试代码
    clicker = EnhancedAutoClicker()

    # 获取设备信息
    print("\n设备信息:")
    print(clicker.get_device_info())

    # 检查兼容性
    print("\n兼容性检查:")
    compat = clicker.check_compatibility()
    print(f"兼容: {compat.get('compatible')}")

    # 测试坐标适配
    print("\n坐标适配测试:")
    x, y = clicker.adapt_coordinate(640, 360)
    print(f"基准坐标(640, 360) -> 适配后({x}, {y})")

    # 获取状态
    print("\n当前状态:")
    import json
    print(json.dumps(clicker.get_status(), indent=2, ensure_ascii=False))
