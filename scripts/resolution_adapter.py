#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分辨率自动适配器
自动检测设备分辨率并适配坐标
"""

import json
import os
from typing import Dict, Tuple, Optional


class ResolutionAdapter:
    """分辨率自动适配器"""

    # 基准分辨率（竖屏）
    BASE_WIDTH = 720
    BASE_HEIGHT = 1280

    # 基准分辨率（横屏）
    BASE_WIDTH_LANDSCAPE = 1280
    BASE_HEIGHT_LANDSCAPE = 720

    def __init__(self, config_path: str = None):
        """
        初始化分辨率适配器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.current_width = self.BASE_WIDTH
        self.current_height = self.BASE_HEIGHT
        self.is_landscape = False
        self.scale_x = 1.0
        self.scale_y = 1.0

        # 设备信息
        self.device_info = {
            'width': self.BASE_WIDTH,
            'height': self.BASE_HEIGHT,
            'density': 'unknown',
            'orientation': 'portrait'
        }

        # 加载配置
        self.config = {}
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)

    def detect_resolution(self) -> Tuple[int, int]:
        """
        自动检测设备分辨率

        Returns:
            (width, height) tuple
        """
        try:
            # 尝试通过ADB获取分辨率
            import subprocess
            result = subprocess.run(
                ['adb', 'shell', 'wm', 'size'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # 解析输出: "Physical size: 1080x2340"
                output = result.stdout.strip()
                if 'Physical size:' in output:
                    size_str = output.split(':')[1].strip()
                    width, height = map(int, size_str.split('x'))
                    self.current_width = width
                    self.current_height = height
                    self.is_landscape = width > height
                    self.update_device_info()
                    return width, height

        except Exception as e:
            print(f"检测分辨率失败: {e}")

        # 返回默认值
        return self.BASE_WIDTH, self.BASE_HEIGHT

    def detect_density(self) -> str:
        """
        检测设备像素密度

        Returns:
            密度字符串（如 'hdpi', 'xhdpi'等）
        """
        try:
            import subprocess
            result = subprocess.run(
                ['adb', 'shell', 'wm', 'density'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                if 'Physical density:' in output:
                    density_str = output.split(':')[1].strip()
                    density = int(density_str)

                    # 根据密度值判断
                    if density <= 120:
                        return 'ldpi'
                    elif density <= 160:
                        return 'mdpi'
                    elif density <= 240:
                        return 'hdpi'
                    elif density <= 320:
                        return 'xhdpi'
                    elif density <= 480:
                        return 'xxhdpi'
                    else:
                        return 'xxxhdpi'

        except Exception as e:
            print(f"检测密度失败: {e}")

        return 'unknown'

    def update_device_info(self):
        """更新设备信息"""
        self.device_info = {
            'width': self.current_width,
            'height': self.current_height,
            'density': self.detect_density(),
            'orientation': 'landscape' if self.is_landscape else 'portrait'
        }

        # 计算缩放比例
        if self.is_landscape:
            self.scale_x = self.current_width / self.BASE_WIDTH_LANDSCAPE
            self.scale_y = self.current_height / self.BASE_HEIGHT_LANDSCAPE
        else:
            self.scale_x = self.current_width / self.BASE_WIDTH
            self.scale_y = self.current_height / self.BASE_HEIGHT

        print(f"设备信息更新: {self.device_info}")
        print(f"缩放比例: X={self.scale_x:.3f}, Y={self.scale_y:.3f}")

    def adapt_coordinate(self, x: int, y: int, from_base: bool = True) -> Tuple[int, int]:
        """
        适配坐标

        Args:
            x: X坐标
            y: Y坐标
            from_base: True表示从基准坐标转换到当前坐标，False表示反向转换

        Returns:
            适配后的(x, y)坐标
        """
        if from_base:
            # 从基准坐标转换到当前坐标
            adapted_x = int(x * self.scale_x)
            adapted_y = int(y * self.scale_y)
        else:
            # 从当前坐标转换到基准坐标
            adapted_x = int(x / self.scale_x)
            adapted_y = int(y / self.scale_y)

        return adapted_x, adapted_y

    def adapt_region(self, x1: int, y1: int, x2: int, y2: int, from_base: bool = True) -> Tuple[int, int, int, int]:
        """
        适配区域坐标

        Args:
            x1, y1: 左上角坐标
            x2, y2: 右下角坐标
            from_base: True表示从基准坐标转换，False表示反向转换

        Returns:
            适配后的(x1, y1, x2, y2)坐标
        """
        if from_base:
            return (
                int(x1 * self.scale_x),
                int(y1 * self.scale_y),
                int(x2 * self.scale_x),
                int(y2 * self.scale_y)
            )
        else:
            return (
                int(x1 / self.scale_x),
                int(y1 / self.scale_y),
                int(x2 / self.scale_x),
                int(y2 / self.scale_y)
            )

    def adapt_config(self, config: Dict) -> Dict:
        """
        适配整个配置文件的坐标

        Args:
            config: 配置字典

        Returns:
            适配后的配置字典
        """
        adapted_config = {}

        for key, value in config.items():
            if isinstance(value, dict):
                if 'x' in value and 'y' in value:
                    # 坐标配置
                    adapted_config[key] = {
                        'x': int(value['x'] * self.scale_x),
                        'y': int(value['y'] * self.scale_y),
                        'desc': value.get('desc', '')
                    }
                    if 'x2' in value and 'y2' in value:
                        # 区域配置
                        adapted_config[key]['x2'] = int(value['x2'] * self.scale_x)
                        adapted_config[key]['y2'] = int(value['y2'] * self.scale_y)
                else:
                    # 递归处理嵌套配置
                    adapted_config[key] = self.adapt_config(value)
            else:
                adapted_config[key] = value

        return adapted_config

    def get_device_info_string(self) -> str:
        """
        获取设备信息字符串

        Returns:
            格式化的设备信息字符串
        """
        orientation = "横屏" if self.is_landscape else "竖屏"
        return (
            f"分辨率: {self.current_width}x{self.current_height} ({orientation})\n"
            f"密度: {self.device_info['density']}\n"
            f"缩放: X={self.scale_x:.3f}, Y={self.scale_y:.3f}"
        )

    def load_config(self, config_path: str):
        """
        加载配置文件

        Args:
            config_path: 配置文件路径
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"配置已加载: {config_path}")
        except Exception as e:
            print(f"加载配置失败: {e}")

    def save_adapted_config(self, output_path: str):
        """
        保存适配后的配置

        Args:
            output_path: 输出文件路径
        """
        adapted_config = self.adapt_config(self.config)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(adapted_config, f, indent=2, ensure_ascii=False)
            print(f"适配配置已保存: {output_path}")
        except Exception as e:
            print(f"保存配置失败: {e}")

    def is_coordinate_in_screen(self, x: int, y: int) -> bool:
        """
        检查坐标是否在屏幕范围内

        Args:
            x: X坐标
            y: Y坐标

        Returns:
            是否在屏幕内
        """
        return 0 <= x < self.current_width and 0 <= y < self.current_height

    def get_safe_coordinate(self, x: int, y: int, margin: int = 10) -> Tuple[int, int]:
        """
        获取安全坐标（确保在屏幕内）

        Args:
            x: X坐标
            y: Y坐标
            margin: 边距

        Returns:
            安全的(x, y)坐标
        """
        safe_x = max(margin, min(x, self.current_width - margin))
        safe_y = max(margin, min(y, self.current_height - margin))
        return safe_x, safe_y


if __name__ == '__main__':
    # 测试代码
    adapter = ResolutionAdapter()

    # 检测分辨率
    width, height = adapter.detect_resolution()
    print(f"检测到分辨率: {width}x{height}")

    # 测试坐标适配
    test_x, test_y = 640, 360
    adapted_x, adapted_y = adapter.adapt_coordinate(test_x, test_y)
    print(f"坐标适配: ({test_x}, {test_y}) -> ({adapted_x}, {adapted_y})")

    # 打印设备信息
    print(adapter.get_device_info_string())
