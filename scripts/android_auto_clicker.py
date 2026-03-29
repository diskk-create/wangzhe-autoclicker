#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android自动点击器 - 适配手机运行
找图 + 找字 + 坐标点击（优先级递减）
"""

import time
import threading
import json
import os

# 尝试导入OpenCV（如果可用）
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("[WARNING] OpenCV不可用，找图找字功能将被禁用")

# 检测Android平台
import sys
IS_ANDROID = 'android' in sys.modules or 'ANDROID_ARGUMENT' in os.environ


class AndroidAutoClicker:
    """Android自动点击器（找图+找字+坐标点击）"""
    
    def __init__(self, template_dir="assets/templates"):
        """
        初始化
        
        Args:
            template_dir: 模板文件目录
        """
        self.template_dir = template_dir
        self.screenshot_path = "current_screen.png"
        
        # 按钮坐标（基准分辨率1280x720）
        self.buttons = {
            "login": {"x": 641, "y": 564, "desc": "登录"},
            "login_popup": {"x": 1190, "y": 112, "desc": "关闭弹窗"},
            "game_lobby": {"x": 514, "y": 544, "desc": "游戏大厅"},
            "match_screen": {"x": 398, "y": 539, "desc": "王者峡谷匹配"},
            "ai_mode_screen": {"x": 730, "y": 601, "desc": "人机模式"},
            "start_game_screen": {"x": 1057, "y": 569, "desc": "开始游戏"},
            "prepare_screen": {"x": 775, "y": 660, "desc": "准备游戏"},
            "ready_game": {"x": 640, "y": 561, "desc": "准备进入游戏"},
            "game_over": {"x": 635, "y": 664, "desc": "游戏结束"},
            "settlement_hero": {"x": 645, "y": 621, "desc": "结算英雄"},
            "return_room": {"x": 739, "y": 651, "desc": "返回房间"}
        }
        
        # 图片模板
        self.image_templates = {
            "login_popup": "template_login_popup.png",
            "match_screen": "template_match.png",
            "start_game_screen": "template_start_game.png",
            "prepare_screen": "template_prepare.png",
            "ready_game": "template_ready_game.png",
            "game_over": "template_game_over.png",
            "in_game": "template_in_game.png"
        }
        
        # 文字模板
        self.text_templates = {
            "login": "text_template_login.png",
            "game_lobby": "text_template_game_lobby.png",
            "wangzhe_xiagu": "text_template_wangzhe_xiagu.png",
            "settlement_hero": "text_template_settlement_hero.png",
            "return_room": "text_template_return_room.png"
        }
        
        # 匹配阈值
        self.match_threshold = 0.7
        
        # 屏幕尺寸（运行时设置）
        self.screen_width = 1280
        self.screen_height = 720
        self.scale_x = 1.0
        self.scale_y = 1.0
        
        # 状态跟踪
        self.current_state = "unknown"
        self.is_running = False
        self.is_paused = False
        
        # 日志回调
        self.log_callback = None
    
    def set_screen_size(self, width, height):
        """设置屏幕尺寸并计算缩放比例"""
        self.screen_width = width
        self.screen_height = height
        
        # 基准分辨率：1280x720
        base_width = 1280
        base_height = 720
        
        self.scale_x = width / base_width
        self.scale_y = height / base_height
        
        self.log(f"屏幕尺寸: {width}x{height}")
        self.log(f"缩放比例: X={self.scale_x:.2f}, Y={self.scale_y:.2f}")
    
    def adapt_coordinate(self, x, y):
        """适配坐标"""
        return int(x * self.scale_x), int(y * self.scale_y)
    
    def log(self, message):
        """记录日志"""
        if self.log_callback:
            self.log_callback(message)
        print(f"[AutoClicker] {message}")
    
    def capture_screen(self):
        """
        截屏（Android平台）
        
        Returns:
            numpy.ndarray: 截屏图像，如果失败返回None
        """
        if not OPENCV_AVAILABLE:
            self.log("OpenCV不可用，无法截屏")
            return None
        
        try:
            if IS_ANDROID:
                # Android平台：使用无障碍服务截屏
                # TODO: 实现无障碍服务截屏
                self.log("Android平台截屏（待实现）")
                return None
            else:
                # 桌面平台：返回None
                self.log("桌面平台，无法截屏")
                return None
        except Exception as e:
            self.log(f"截屏失败: {e}")
            return None
    
    def match_template(self, screenshot, template_file):
        """
        模板匹配（找图）
        
        Args:
            screenshot: 截屏图像
            template_file: 模板文件路径
        
        Returns:
            tuple: (是否匹配, 匹配位置, 匹配置信度)
        """
        if not OPENCV_AVAILABLE or screenshot is None:
            return False, None, 0
        
        template_path = os.path.join(self.template_dir, template_file)
        if not os.path.exists(template_path):
            self.log(f"模板文件不存在: {template_file}")
            return False, None, 0
        
        try:
            # 读取模板
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                self.log(f"无法读取模板: {template_file}")
                return False, None, 0
            
            # 转换为灰度图
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            # 模板匹配
            result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= self.match_threshold:
                # 匹配成功，计算中心位置
                h, w = template_gray.shape
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                return True, (center_x, center_y), max_val
            
            return False, None, max_val
            
        except Exception as e:
            self.log(f"模板匹配失败: {e}")
            return False, None, 0
    
    def detect_screen(self, screenshot):
        """
        检测当前屏幕
        
        Args:
            screenshot: 截屏图像
        
        Returns:
            tuple: (屏幕名称, 匹配置信度)
        """
        if screenshot is None:
            return "unknown", 0
        
        best_match = "unknown"
        best_score = 0
        
        # 尝试匹配图片模板
        for screen_name, template_file in self.image_templates.items():
            matched, position, score = self.match_template(screenshot, template_file)
            if matched and score > best_score:
                best_match = screen_name
                best_score = score
        
        # 尝试匹配文字模板
        for screen_name, template_file in self.text_templates.items():
            matched, position, score = self.match_template(screenshot, template_file)
            if matched and score > best_score:
                best_match = screen_name
                best_score = score
        
        return best_match, best_score
    
    def click(self, x, y):
        """
        执行点击
        
        Args:
            x: X坐标（基准分辨率）
            y: Y坐标（基准分辨率）
        """
        # 适配坐标
        actual_x, actual_y = self.adapt_coordinate(x, y)
        
        self.log(f"点击: ({x}, {y}) -> ({actual_x}, {actual_y})")
        
        if IS_ANDROID:
            # Android平台：使用无障碍服务点击
            # TODO: 实现无障碍服务点击
            self.log("Android平台点击（待实现）")
        else:
            # 桌面平台：模拟点击（测试用）
            self.log("桌面平台模拟点击")
    
    def smart_click(self, button_name):
        """
        智能点击（找图 > 找字 > 坐标）
        
        Args:
            button_name: 按钮名称
        
        Returns:
            bool: 是否成功
        """
        # 优先级1: 找图
        if button_name in self.image_templates and OPENCV_AVAILABLE:
            screenshot = self.capture_screen()
            if screenshot is not None:
                matched, position, score = self.match_template(
                    screenshot,
                    self.image_templates[button_name]
                )
                if matched:
                    self.log(f"找图成功: {button_name} (置信度: {score:.2f})")
                    self.click(position[0], position[1])
                    return True
        
        # 优先级2: 找字
        if button_name in self.text_templates and OPENCV_AVAILABLE:
            screenshot = self.capture_screen()
            if screenshot is not None:
                matched, position, score = self.match_template(
                    screenshot,
                    self.text_templates[button_name]
                )
                if matched:
                    self.log(f"找字成功: {button_name} (置信度: {score:.2f})")
                    self.click(position[0], position[1])
                    return True
        
        # 优先级3: 坐标点击（兜底）
        if button_name in self.buttons:
            button = self.buttons[button_name]
            self.log(f"坐标点击: {button_name} ({button['desc']})")
            self.click(button['x'], button['y'])
            return True
        
        self.log(f"未找到按钮: {button_name}")
        return False
    
    def run_11_step_flow(self):
        """执行11步流程"""
        steps = [
            ("login", "登录", 3),
            ("login_popup", "关闭弹窗", 2),
            ("game_lobby", "游戏大厅", 2),
            ("match_screen", "王者峡谷匹配", 2),
            ("ai_mode_screen", "人机模式", 2),
            ("start_game_screen", "开始游戏", 3),
            ("prepare_screen", "准备游戏", 2),
            ("ready_game", "准备进入游戏", 10),
            ("game_over", "游戏结束", 60),
            ("settlement_hero", "结算英雄", 2),
            ("return_room", "返回房间", 3)
        ]
        
        for step_name, desc, wait_time in steps:
            if not self.is_running:
                self.log("脚本已停止")
                return
            
            while self.is_paused:
                time.sleep(0.1)
            
            self.log(f"步骤: {desc} ({step_name})")
            
            if self.smart_click(step_name):
                self.log(f"等待 {wait_time} 秒...")
                time.sleep(wait_time)
            else:
                self.log(f"步骤失败: {desc}")
                # 继续执行下一步
        
        self.log("11步流程完成")


# 测试代码
if __name__ == '__main__':
    clicker = AndroidAutoClicker()
    clicker.set_screen_size(1280, 720)
    
    print("=" * 60)
    print("Android自动点击器测试")
    print("=" * 60)
    print(f"OpenCV可用: {OPENCV_AVAILABLE}")
    print(f"Android平台: {IS_ANDROID}")
    print(f"屏幕尺寸: {clicker.screen_width}x{clicker.screen_height}")
    print("=" * 60)
    
    # 测试坐标适配
    x, y = clicker.adapt_coordinate(641, 564)
    print(f"坐标适配: (641, 564) -> ({x}, {y})")
    
    # 测试按钮
    print("\n按钮列表:")
    for name, button in clicker.buttons.items():
        print(f"  {name}: ({button['x']}, {button['y']}) - {button['desc']}")
