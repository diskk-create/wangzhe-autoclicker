#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
悬浮窗管理器
解决横屏切换时的闪退问题
"""

from kivy.core.window import Window
from kivy.clock import Clock


class FloatWindowManager:
    """
    悬浮窗管理器 - 单例模式
    防止Activity重建时重复添加悬浮窗导致的崩溃
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(FloatWindowManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化悬浮窗管理器"""
        if FloatWindowManager._initialized:
            return

        FloatWindowManager._initialized = True

        # 悬浮窗状态
        self.is_window_added = False
        self.is_window_visible = False
        self.current_orientation = 'portrait'

        # 窗口引用
        self.float_window = None
        self.window_params = {}

        # 配置变化回调
        self.on_config_change_callback = None

        # 绑定窗口事件
        if Window:
            Window.bind(on_keyboard=self._on_keyboard)
            # 注意：Kivy不直接支持on_config_change，需要在Android端处理

        print("悬浮窗管理器已初始化")

    @staticmethod
    def get_instance():
        """获取单例实例"""
        if FloatWindowManager._instance is None:
            FloatWindowManager._instance = FloatWindowManager()
        return FloatWindowManager._instance

    def add_float_window(self, window):
        """
        添加悬浮窗

        Args:
            window: 悬浮窗实例

        Returns:
            是否成功添加
        """
        if self.is_window_added:
            print("悬浮窗已存在，跳过添加")
            return False

        try:
            self.float_window = window
            self.is_window_added = True
            self.is_window_visible = True
            print("悬浮窗已添加")
            return True

        except Exception as e:
            print(f"添加悬浮窗失败: {e}")
            return False

    def remove_float_window(self):
        """
        移除悬浮窗

        Returns:
            是否成功移除
        """
        if not self.is_window_added:
            print("悬浮窗不存在，跳过移除")
            return False

        try:
            if self.float_window:
                # 清理悬浮窗
                self.float_window = None

            self.is_window_added = False
            self.is_window_visible = False
            print("悬浮窗已移除")
            return True

        except Exception as e:
            print(f"移除悬浮窗失败: {e}")
            return False

    def show_float_window(self):
        """显示悬浮窗"""
        if not self.is_window_added:
            print("悬浮窗不存在，无法显示")
            return False

        try:
            if self.float_window and hasattr(self.float_window, 'show'):
                self.float_window.show()
                self.is_window_visible = True
                print("悬浮窗已显示")
                return True
        except Exception as e:
            print(f"显示悬浮窗失败: {e}")
            return False

    def hide_float_window(self):
        """隐藏悬浮窗"""
        if not self.is_window_added:
            print("悬浮窗不存在，无法隐藏")
            return False

        try:
            if self.float_window and hasattr(self.float_window, 'hide'):
                self.float_window.hide()
                self.is_window_visible = False
                print("悬浮窗已隐藏")
                return True
        except Exception as e:
            print(f"隐藏悬浮窗失败: {e}")
            return False

    def handle_orientation_change(self, orientation):
        """
        处理屏幕方向变化

        Args:
            orientation: 'portrait' 或 'landscape'

        Returns:
            是否成功处理
        """
        if orientation == self.current_orientation:
            print(f"屏幕方向未变化: {orientation}")
            return True

        print(f"屏幕方向变化: {self.current_orientation} -> {orientation}")

        # 暂时隐藏悬浮窗
        was_visible = self.is_window_visible
        if was_visible:
            self.hide_float_window()

        # 更新方向
        old_orientation = self.current_orientation
        self.current_orientation = orientation

        # 调用配置变化回调
        if self.on_config_change_callback:
            try:
                self.on_config_change_callback(old_orientation, orientation)
            except Exception as e:
                print(f"配置变化回调失败: {e}")

        # 恢复悬浮窗显示
        if was_visible:
            # 延迟显示，等待布局完成
            Clock.schedule_once(lambda dt: self.show_float_window(), 0.5)

        return True

    def handle_config_change(self, config_type):
        """
        处理配置变化

        Args:
            config_type: 配置变化类型（orientation, screenSize, keyboardHidden等）

        Returns:
            是否成功处理
        """
        print(f"配置变化: {config_type}")

        # 根据配置类型处理
        if config_type == 'orientation':
            # 屏幕方向变化已在handle_orientation_change中处理
            pass
        elif config_type == 'screenSize':
            # 屏幕尺寸变化
            pass
        elif config_type == 'keyboardHidden':
            # 键盘状态变化
            pass

        return True

    def set_on_config_change_callback(self, callback):
        """
        设置配置变化回调

        Args:
            callback: 回调函数(old_orientation, new_orientation)
        """
        self.on_config_change_callback = callback

    def _on_keyboard(self, window, key, *args):
        """
        键盘事件处理

        Args:
            window: 窗口实例
            key: 按键代码

        Returns:
            是否消费事件
        """
        # 处理返回键等
        if key == 27:  # ESC/Back
            if self.is_window_visible:
                self.hide_float_window()
                return True

        return False

    def get_status(self):
        """
        获取悬浮窗状态

        Returns:
            状态字典
        """
        return {
            'is_added': self.is_window_added,
            'is_visible': self.is_window_visible,
            'orientation': self.current_orientation,
            'has_window': self.float_window is not None
        }

    def cleanup(self):
        """清理资源"""
        print("清理悬浮窗管理器...")
        self.remove_float_window()
        FloatWindowManager._instance = None
        FloatWindowManager._initialized = False


def get_window_manager():
    """获取悬浮窗管理器实例"""
    return FloatWindowManager.get_instance()


# Android端处理配置变化的辅助函数
def setup_android_config_changes():
    """
    在Android端设置配置变化处理
    需要在AndroidManifest.xml中添加:
    android:configChanges="orientation|screenSize|keyboardHidden"

    这样Activity不会在配置变化时重建，而是调用onConfigurationChanged
    """
    try:
        from jnius import autoclass

        # 获取Activity
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity

        # 注册配置变化监听
        # 注意：实际配置需要在AndroidManifest.xml中声明
        print("Android配置变化处理已设置")

        return True

    except Exception as e:
        print(f"设置Android配置变化失败: {e}")
        return False


if __name__ == '__main__':
    # 测试代码
    manager = FloatWindowManager.get_instance()

    print("悬浮窗管理器状态:")
    print(manager.get_status())

    # 测试添加
    class MockWindow:
        def show(self):
            print("MockWindow: show")

        def hide(self):
            print("MockWindow: hide")

    window = MockWindow()
    manager.add_float_window(window)
    print("\n添加悬浮窗后:")
    print(manager.get_status())

    # 测试方向变化
    manager.handle_orientation_change('landscape')
    print("\n方向变化后:")
    print(manager.get_status())

    # 清理
    manager.cleanup()
