#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备检测器
检测设备架构、系统版本等信息
"""

import subprocess
import platform
import re
from typing import Dict, Optional, List


class DeviceDetector:
    """设备检测器"""

    # 支持的架构
    SUPPORTED_ARCHS = {
        'armeabi-v7a': 'ARM 32-bit',
        'arm64-v8a': 'ARM 64-bit',
        'x86': 'x86 32-bit',
        'x86_64': 'x86 64-bit'
    }

    # 模拟器特征
    EMULATOR_SIGNATURES = [
        'generic',
        'emulator',
        'sdk',
        'google_sdk',
        'droid4x',
        'andy',
        'nox',
        'bluestacks',
        'genymotion',
        'memu'
    ]

    def __init__(self):
        """初始化设备检测器"""
        self.device_info = {}
        self.is_connected = False
        self.is_emulator = False
        self.architecture = None
        self.android_version = None
        self.device_model = None

    def check_adb_available(self) -> bool:
        """
        检查ADB是否可用

        Returns:
            ADB是否可用
        """
        try:
            result = subprocess.run(
                ['adb', 'version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_connected_devices(self) -> List[Dict]:
        """
        获取已连接的设备列表

        Returns:
            设备信息列表
        """
        devices = []

        try:
            result = subprocess.run(
                ['adb', 'devices', '-l'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # 跳过第一行标题
                    if line.strip() and '\t' in line:
                        parts = line.split('\t')
                        if len(parts) >= 2 and parts[1] == 'device':
                            device_id = parts[0].strip()
                            device_info = self.get_device_info(device_id)
                            devices.append(device_info)

        except Exception as e:
            print(f"获取设备列表失败: {e}")

        return devices

    def get_device_info(self, device_id: str = None) -> Dict:
        """
        获取设备详细信息

        Args:
            device_id: 设备ID（可选）

        Returns:
            设备信息字典
        """
        info = {
            'device_id': device_id or 'unknown',
            'model': 'unknown',
            'brand': 'unknown',
            'manufacturer': 'unknown',
            'android_version': 'unknown',
            'sdk_version': 'unknown',
            'architecture': 'unknown',
            'cpu_abi': 'unknown',
            'cpu_abi2': 'unknown',
            'is_emulator': False,
            'screen_width': 0,
            'screen_height': 0,
            'density': 'unknown',
            'supported': False
        }

        try:
            # 基本属性
            properties = {
                'model': 'ro.product.model',
                'brand': 'ro.product.brand',
                'manufacturer': 'ro.product.manufacturer',
                'android_version': 'ro.build.version.release',
                'sdk_version': 'ro.build.version.sdk',
                'cpu_abi': 'ro.product.cpu.abi',
                'cpu_abi2': 'ro.product.cpu.abi2'
            }

            for key, prop in properties.items():
                cmd = ['adb']
                if device_id:
                    cmd.extend(['-s', device_id])
                cmd.extend(['shell', 'getprop', prop])

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    info[key] = result.stdout.strip()

            # 检测架构
            if info['cpu_abi']:
                info['architecture'] = info['cpu_abi']

            # 检测是否为模拟器
            info['is_emulator'] = self._check_is_emulator(info)

            # 获取屏幕分辨率
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['shell', 'wm', 'size'])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                match = re.search(r'(\d+)x(\d+)', result.stdout)
                if match:
                    info['screen_width'] = int(match.group(1))
                    info['screen_height'] = int(match.group(2))

            # 获取密度
            cmd = ['adb']
            if device_id:
                cmd.extend(['-s', device_id])
            cmd.extend(['shell', 'wm', 'density'])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                match = re.search(r'(\d+)', result.stdout)
                if match:
                    density = int(match.group(1))
                    info['density'] = self._get_density_name(density)

            # 检查是否支持
            info['supported'] = info['architecture'] in self.SUPPORTED_ARCHS

        except Exception as e:
            print(f"获取设备信息失败: {e}")

        return info

    def _check_is_emulator(self, info: Dict) -> bool:
        """
        检测是否为模拟器

        Args:
            info: 设备信息

        Returns:
            是否为模拟器
        """
        # 检查设备模型
        model = info.get('model', '').lower()
        brand = info.get('brand', '').lower()
        manufacturer = info.get('manufacturer', '').lower()

        for signature in self.EMULATOR_SIGNATURES:
            if (signature in model or
                signature in brand or
                signature in manufacturer):
                return True

        # 检查架构（x86通常是模拟器）
        if info.get('architecture', '').startswith('x86'):
            return True

        return False

    def _get_density_name(self, density: int) -> str:
        """
        根据密度值获取密度名称

        Args:
            density: 密度值

        Returns:
            密度名称
        """
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

    def check_compatibility(self, device_id: str = None) -> Dict:
        """
        检查设备兼容性

        Args:
            device_id: 设备ID（可选）

        Returns:
            兼容性检查结果
        """
        result = {
            'compatible': False,
            'architecture': None,
            'is_emulator': False,
            'warnings': [],
            'errors': []
        }

        # 获取设备信息
        info = self.get_device_info(device_id)

        # 检查架构
        arch = info.get('architecture', 'unknown')
        result['architecture'] = arch

        if arch not in self.SUPPORTED_ARCHS:
            result['errors'].append(f"不支持的架构: {arch}")
            result['errors'].append("支持的架构: " + ', '.join(self.SUPPORTED_ARCHS.keys()))
        else:
            result['compatible'] = True

        # 检查是否为模拟器
        if info.get('is_emulator', False):
            result['is_emulator'] = True
            result['warnings'].append("检测到模拟器环境")

            # 检查模拟器架构
            if arch.startswith('x86'):
                result['warnings'].append(f"模拟器使用{x86}架构，可能需要ARM转译")

        # 检查Android版本
        try:
            sdk_version = int(info.get('sdk_version', '0'))
            if sdk_version < 24:  # Android 7.0
                result['warnings'].append(f"Android版本过低 (API {sdk_version})，建议使用Android 7.0及以上")
        except ValueError:
            result['warnings'].append("无法检测Android版本")

        # 检查屏幕分辨率
        width = info.get('screen_width', 0)
        height = info.get('screen_height', 0)
        if width > 0 and height > 0:
            if width < 720 or height < 1280:
                result['warnings'].append(f"屏幕分辨率较低 ({width}x{height})，可能影响体验")

        return result

    def get_device_info_string(self, device_id: str = None) -> str:
        """
        获取设备信息字符串

        Args:
            device_id: 设备ID（可选）

        Returns:
            格式化的设备信息字符串
        """
        info = self.get_device_info(device_id)

        lines = [
            f"设备ID: {info.get('device_id', 'unknown')}",
            f"型号: {info.get('model', 'unknown')}",
            f"品牌: {info.get('brand', 'unknown')}",
            f"制造商: {info.get('manufacturer', 'unknown')}",
            f"Android版本: {info.get('android_version', 'unknown')} (API {info.get('sdk_version', 'unknown')})",
            f"架构: {info.get('architecture', 'unknown')} ({self.SUPPORTED_ARCHS.get(info.get('architecture'), '未知')})",
            f"屏幕: {info.get('screen_width', 0)}x{info.get('screen_height', 0)}",
            f"密度: {info.get('density', 'unknown')}",
            f"类型: {'模拟器' if info.get('is_emulator') else '真机'}",
            f"兼容性: {'✓ 支持' if info.get('supported') else '✗ 不支持'}"
        ]

        return '\n'.join(lines)


if __name__ == '__main__':
    # 测试代码
    detector = DeviceDetector()

    # 检查ADB
    if detector.check_adb_available():
        print("ADB可用")

        # 获取设备列表
        devices = detector.get_connected_devices()
        print(f"\n已连接设备数: {len(devices)}")

        for device in devices:
            print("\n" + "=" * 50)
            print(detector.get_device_info_string(device['device_id']))

            # 检查兼容性
            compat = detector.check_compatibility(device['device_id'])
            print("\n兼容性检查:")
            print(f"  兼容: {'是' if compat['compatible'] else '否'}")
            print(f"  模拟器: {'是' if compat['is_emulator'] else '否'}")
            if compat['warnings']:
                print("  警告:")
                for warning in compat['warnings']:
                    print(f"    - {warning}")
            if compat['errors']:
                print("  错误:")
                for error in compat['errors']:
                    print(f"    - {error}")
    else:
        print("ADB不可用，请确保ADB已安装并添加到PATH")
