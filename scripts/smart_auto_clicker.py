#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
王者荣耀自动点击器 - Android无障碍服务版
核心脚本 - 完整支持找图和找字功能
"""

import os
import time
import threading
import json
from pathlib import Path

# Android相关导入
try:
    from jnius import autoclass, cast
    from android import mActivity
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False
    print("警告: Android环境未检测到，运行在模拟模式")

# 图像处理 - 可选依赖
try:
    import cv2
    import numpy as np
    CV_AVAILABLE = True
    print("OpenCV 已加载，图像识别功能可用")
except ImportError:
    CV_AVAILABLE = False
    print("警告: OpenCV未安装，图像识别功能不可用，仅使用坐标点击")


class ImageMatcher:
    """图像匹配器 - 完整支持找图和找字"""
    
    def __init__(self, template_dir='templates', threshold=0.7):
        """
        初始化图像匹配器
        
        Args:
            template_dir: 模板图片目录
            threshold: 匹配阈值 (0-1)
        """
        self.template_dir = Path(template_dir)
        self.threshold = threshold
        self.cv_available = CV_AVAILABLE
        
        # 按钮模板 (找图)
        self.button_templates = {}
        
        # 文字模板 (找字)
        self.text_templates = {}
        
        if self.cv_available:
            self._load_all_templates()
    
    def _load_all_templates(self):
        """加载所有模板图片"""
        if not self.template_dir.exists():
            print(f"模板目录不存在: {self.template_dir}")
            return
        
        print("\n" + "="*50)
        print("加载模板文件...")
        print("="*50)
        
        # 按钮模板列表 (找图)
        button_template_files = {
            'login_popup': 'template_login_popup.png',
            'match_screen': 'template_match.png',
            'start_game_screen': 'template_start_game.png',
            'prepare_screen': 'template_prepare.png',
            'ready_game': 'template_ready_game.png',
            'game_over': 'template_game_over.png',
            'in_game': 'template_in_game.png',
            'login': 'template_login.png',
            'game_lobby': 'template_game_lobby.png',
            'ai_mode': 'template_ai_mode.png',
            'check': 'template_check.png'
        }
        
        # 文字模板列表 (找字)
        text_template_files = {
            'login': 'text_template_login.png',           # 开始游戏文字
            'game_lobby': 'text_template_game_lobby.png', # 对战文字
            'wangzhe_xiagu': 'text_template_wangzhe_xiagu.png',  # 王者峡谷文字
            'settlement_hero': 'text_template_settlement_hero.png',  # 结算英雄文字
            'return_room': 'text_template_return_room.png',  # 返回房间文字
            'settlement_hero_new': 'text_template_settlement_hero_new.png'  # 新版结算
        }
        
        # 加载按钮模板
        print("\n[找图模板]:")
        for name, filename in button_template_files.items():
            template_path = self.template_dir / filename
            if template_path.exists():
                try:
                    template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
                    if template is not None:
                        self.button_templates[name] = template
                        print(f"  [OK] {name}: {filename}")
                    else:
                        print(f"  [--] {name}: 加载失败 {filename}")
                except Exception as e:
                    print(f"  [--] {name}: {e}")
            else:
                print(f"  [--] {name}: 文件不存在 {filename}")
        
        # 加载文字模板
        print("\n[找字模板]:")
        for name, filename in text_template_files.items():
            template_path = self.template_dir / filename
            if template_path.exists():
                try:
                    template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
                    if template is not None:
                        self.text_templates[name] = template
                        print(f"  [OK] {name}: {filename}")
                    else:
                        print(f"  [--] {name}: 加载失败 {filename}")
                except Exception as e:
                    print(f"  [--] {name}: {e}")
            else:
                print(f"  [--] {name}: 文件不存在 {filename}")
        
        print(f"\n已加载: {len(self.button_templates)} 个找图模板, {len(self.text_templates)} 个找字模板")
        print("="*50)
    
    def find_template(self, screenshot, template_key, is_text=False):
        """
        在截图中查找模板 (找图或找字)
        
        Args:
            screenshot: 截图 (numpy数组或文件路径)
            template_key: 模板键名
            is_text: 是否是文字模板
        
        Returns:
            (found, x, y, w, h, confidence) - 是否找到, x, y, 宽, 高, 置信度
        """
        if not self.cv_available:
            return False, 0, 0, 0, 0, 0
        
        # 选择模板库
        templates = self.text_templates if is_text else self.button_templates
        
        if template_key not in templates:
            return False, 0, 0, 0, 0, 0
        
        # 处理截图
        if isinstance(screenshot, str):
            screenshot = cv2.imread(screenshot, cv2.IMREAD_COLOR)
        elif isinstance(screenshot, bytes):
            nparr = np.frombuffer(screenshot, np.uint8)
            screenshot = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if screenshot is None:
            return False, 0, 0, 0, 0, 0
        
        # 转换为灰度图
        if len(screenshot.shape) == 3:
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        else:
            screenshot_gray = screenshot
        
        # 获取模板
        template = templates[template_key]
        
        # 检查模板尺寸
        if template.shape[0] > screenshot_gray.shape[0] or \
           template.shape[1] > screenshot_gray.shape[1]:
            print(f"模板 {template_key} 尺寸大于截图")
            return False, 0, 0, 0, 0, 0
        
        # 模板匹配
        try:
            result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            th, tw = template.shape
            
            if max_val >= self.threshold:
                x, y = max_loc
                center_x = x + tw // 2
                center_y = y + th // 2
                print(f"找到{'文字' if is_text else '按钮'} '{template_key}': 位置({center_x}, {center_y}), 尺寸({tw}x{th}), 置信度: {max_val:.2f}")
                return True, center_x, center_y, tw, th, max_val
            else:
                return False, 0, 0, 0, 0, max_val
        except Exception as e:
            print(f"模板匹配出错: {e}")
            return False, 0, 0, 0, 0, 0
    
    def find_button(self, screenshot, button_key):
        """找图 - 查找按钮模板"""
        return self.find_template(screenshot, button_key, is_text=False)
    
    def find_text(self, screenshot, text_key):
        """找字 - 查找文字模板"""
        return self.find_template(screenshot, text_key, is_text=True)
    
    def detect_screen_full(self, screenshot):
        """
        完整屏幕检测 - 同时使用找图和找字
        
        Args:
            screenshot: 截图
        
        Returns:
            (screen_name, score, match_info) - 屏幕名, 置信度, 匹配信息
        """
        if not self.cv_available or screenshot is None:
            return "unknown", 0, None
        
        best_match = "unknown"
        best_score = 0
        match_info = None
        
        # 1. 先尝试找图 - 按钮模板 (优先级高)
        priority_buttons = ['match_screen', 'start_game_screen', 'prepare_screen', 'ready_game', 'game_over']
        for button_key in priority_buttons:
            found, x, y, w, h, score = self.find_button(screenshot, button_key)
            if found and score > best_score:
                best_match = button_key
                best_score = score
                match_info = {'type': 'button', 'key': button_key, 'pos': (x, y), 'size': (w, h)}
        
        # 如果找到了优先按钮，直接返回
        if best_match != "unknown":
            return best_match, best_score, match_info
        
        # 2. 尝试找字 - 文字模板
        # 检查登录界面 (开始游戏文字)
        found, x, y, w, h, score = self.find_text(screenshot, 'login')
        if found and score > best_score:
            best_match = 'login'
            best_score = score
            match_info = {'type': 'text', 'key': 'login', 'pos': (x, y), 'size': (w, h)}
        
        # 检查游戏大厅 (对战文字)
        found, x, y, w, h, score = self.find_text(screenshot, 'game_lobby')
        if found and score > best_score:
            best_match = 'game_lobby'
            best_score = score
            match_info = {'type': 'text', 'key': 'game_lobby', 'pos': (x, y), 'size': (w, h)}
        
        # 检查王者峡谷 (AI模式选择)
        found, x, y, w, h, score = self.find_text(screenshot, 'wangzhe_xiagu')
        if found and score > best_score:
            best_match = 'ai_mode_screen'
            best_score = score
            match_info = {'type': 'text', 'key': 'wangzhe_xiagu', 'pos': (x, y), 'size': (w, h)}
        
        # 检查结算英雄
        found, x, y, w, h, score = self.find_text(screenshot, 'settlement_hero')
        if found and score > best_score:
            best_match = 'settlement_hero'
            best_score = score
            match_info = {'type': 'text', 'key': 'settlement_hero', 'pos': (x, y), 'size': (w, h)}
        
        # 检查新版结算
        found, x, y, w, h, score = self.find_text(screenshot, 'settlement_hero_new')
        if found and score > best_score:
            best_match = 'settlement_hero'
            best_score = score
            match_info = {'type': 'text', 'key': 'settlement_hero_new', 'pos': (x, y), 'size': (w, h)}
        
        # 检查返回房间
        found, x, y, w, h, score = self.find_text(screenshot, 'return_room')
        if found and score > best_score:
            best_match = 'return_room'
            best_score = score
            match_info = {'type': 'text', 'key': 'return_room', 'pos': (x, y), 'size': (w, h)}
        
        # 3. 再尝试其他找图模板
        for button_key in self.button_templates:
            if button_key in priority_buttons:
                continue
            found, x, y, w, h, score = self.find_button(screenshot, button_key)
            if found and score > best_score:
                best_match = button_key
                best_score = score
                match_info = {'type': 'button', 'key': button_key, 'pos': (x, y), 'size': (w, h)}
        
        return best_match, best_score, match_info
    
    def add_template(self, name, image_path, is_text=False):
        """
        添加新模板
        
        Args:
            name: 模板名称
            image_path: 图片路径
            is_text: 是否是文字模板
        """
        if not self.cv_available:
            print("OpenCV不可用，无法添加模板")
            return False
        
        try:
            template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if template is not None:
                if is_text:
                    self.text_templates[name] = template
                    print(f"添加文字模板成功: {name}")
                else:
                    self.button_templates[name] = template
                    print(f"添加按钮模板成功: {name}")
                return True
            else:
                print(f"无法读取图片: {image_path}")
                return False
        except Exception as e:
            print(f"添加模板出错: {e}")
            return False
    
    def set_threshold(self, threshold):
        """设置匹配阈值"""
        self.threshold = threshold
        print(f"匹配阈值已更新: {threshold}")
    
    def get_template_count(self):
        """获取模板数量"""
        return len(self.button_templates), len(self.text_templates)


class SmartAutoClicker:
    """智能自动点击器 - 完整支持找图和找字"""
    
    # 11步流程状态 (完整保留原有逻辑)
    STATES = {
        'login': {
            'name': '登录',
            'desc': '点击"开始游戏"登录',
            'next': 'login_popup',
            'use_image': True,
            'use_text': True,
            'button_template': 'login',
            'text_template': 'login',
            'fallback_coords': {'x': 641, 'y': 564}
        },
        'login_popup': {
            'name': '关闭弹窗',
            'desc': '关闭登录弹窗',
            'next': 'game_lobby',
            'use_image': True,
            'use_text': False,
            'button_template': 'login_popup',
            'text_template': None,
            'fallback_coords': {'x': 1190, 'y': 112}
        },
        'game_lobby': {
            'name': '游戏大厅',
            'desc': '点击"对战"',
            'next': 'match_screen',
            'use_image': True,
            'use_text': True,
            'button_template': 'game_lobby',
            'text_template': 'game_lobby',
            'fallback_coords': {'x': 514, 'y': 544}
        },
        'match_screen': {
            'name': '匹配',
            'desc': '点击"王者峡谷"',
            'next': 'ai_mode_screen',
            'use_image': True,
            'use_text': False,
            'button_template': 'match_screen',
            'text_template': None,
            'fallback_coords': {'x': 398, 'y': 539}
        },
        'ai_mode_screen': {
            'name': 'AI模式',
            'desc': '选择"人机"',
            'next': 'start_game_screen',
            'use_image': True,
            'use_text': True,
            'button_template': 'ai_mode',
            'text_template': 'wangzhe_xiagu',
            'fallback_coords': {'x': 730, 'y': 601}
        },
        'start_game_screen': {
            'name': '开始游戏',
            'desc': '点击"开始游戏"',
            'next': 'prepare_screen',
            'use_image': True,
            'use_text': False,
            'button_template': 'start_game_screen',
            'text_template': None,
            'fallback_coords': {'x': 1057, 'y': 569}
        },
        'prepare_screen': {
            'name': '准备游戏',
            'desc': '点击"准备"',
            'next': 'ready_game',
            'use_image': True,
            'use_text': False,
            'button_template': 'prepare_screen',
            'text_template': None,
            'fallback_coords': {'x': 775, 'y': 660}
        },
        'ready_game': {
            'name': '准备进入',
            'desc': '确认进入游戏',
            'next': 'in_game',
            'use_image': True,
            'use_text': False,
            'button_template': 'ready_game',
            'text_template': None,
            'fallback_coords': {'x': 640, 'y': 561}
        },
        'in_game': {
            'name': '游戏中',
            'desc': '等待游戏结束',
            'next': 'game_over',
            'use_image': True,
            'use_text': False,
            'button_template': 'in_game',
            'text_template': None,
            'fallback_coords': {'x': 640, 'y': 360}
        },
        'game_over': {
            'name': '游戏结束',
            'desc': '确认结束',
            'next': 'settlement_hero',
            'use_image': True,
            'use_text': False,
            'button_template': 'game_over',
            'text_template': None,
            'fallback_coords': {'x': 635, 'y': 664}
        },
        'settlement_hero': {
            'name': '结算英雄',
            'desc': '查看结算',
            'next': 'return_room',
            'use_image': True,
            'use_text': True,
            'button_template': None,
            'text_template': 'settlement_hero',
            'fallback_coords': {'x': 645, 'y': 621}
        },
        'return_room': {
            'name': '返回房间',
            'desc': '返回大厅',
            'next': 'game_lobby',
            'use_image': True,
            'use_text': True,
            'button_template': None,
            'text_template': 'return_room',
            'fallback_coords': {'x': 739, 'y': 651}
        }
    }
    
    def __init__(self, accessibility=None, config=None, log_callback=None):
        """
        初始化自动点击器
        
        Args:
            accessibility: 无障碍服务实例
            config: 配置字典
            log_callback: 日志回调函数
        """
        self.accessibility = accessibility
        self.config = config or {}
        self.log_callback = log_callback or print
        
        self.is_running = False
        self.is_paused = False
        self.current_state = 'login'
        self.loop_count = 0
        self.state_history = []
        
        # 获取配置
        self.buttons = self.config.get('buttons', {})
        self.settings = self.config.get('settings', {})
        
        self.wait_time = self.settings.get('wait_time', 3)
        self.threshold = self.settings.get('threshold', 0.7)
        self.max_loops = self.settings.get('max_loops', 100)
        self.interval = self.settings.get('interval', 2)
        self.use_image_matching = self.settings.get('use_image_matching', True)
        
        # 屏幕尺寸
        if accessibility:
            self.screen_width, self.screen_height = accessibility.get_screen_size()
        else:
            self.screen_width, self.screen_height = 1280, 720
        
        # 初始化图像匹配器
        self.image_matcher = ImageMatcher(
            template_dir='templates',
            threshold=self.threshold
        )
        
        button_count, text_count = self.image_matcher.get_template_count()
        self.log(f"图像识别功能: {'已启用' if self.image_matcher.cv_available else '未启用'}")
        self.log(f"找图模板: {button_count} 个")
        self.log(f"找字模板: {text_count} 个")
    
    def log(self, message):
        """输出日志"""
        timestamp = time.strftime('%H:%M:%S')
        if self.log_callback:
            self.log_callback(f"[{timestamp}] {message}")
        else:
            print(f"[{timestamp}] {message}")
    
    def get_button_coords(self, state):
        """
        获取按钮坐标，自动适配屏幕
        
        Args:
            state: 状态名称
        
        Returns:
            (x, y) 坐标元组
        """
        state_info = self.STATES.get(state, {})
        fallback = state_info.get('fallback_coords', {'x': 0, 'y': 0})
        button = self.buttons.get(state, fallback)
        
        # 计算缩放比例
        scale_x = self.screen_width / 1280
        scale_y = self.screen_height / 720
        
        # 缩放坐标
        x = int(button.get('x', fallback['x']) * scale_x)
        y = int(button.get('y', fallback['y']) * scale_y)
        
        return x, y
    
    def click(self, x, y):
        """
        执行点击操作
        
        Args:
            x: X坐标
            y: Y坐标
        
        Returns:
            是否成功
        """
        self.log(f'点击坐标: ({x}, {y})')
        
        if self.accessibility:
            return self.accessibility.click(x, y)
        else:
            self.log(f'[模拟] 点击 ({x}, {y})')
            return True
    
    def take_screenshot(self):
        """
        截取屏幕
        
        Returns:
            截图图像或None
        """
        if self.accessibility:
            return self.accessibility.take_screenshot()
        return None
    
    def detect_screen(self, screenshot=None):
        """
        检测当前屏幕状态
        
        Args:
            screenshot: 截图（可选）
        
        Returns:
            (state, score, match_info) - 状态名, 置信度, 匹配信息
        """
        if not self.image_matcher.cv_available:
            return "unknown", 0, None
        
        if screenshot is None:
            screenshot = self.take_screenshot()
        
        if screenshot is None:
            return "unknown", 0, None
        
        return self.image_matcher.detect_screen_full(screenshot)
    
    def find_and_click(self, state):
        """
        找图/找字并点击，如果找不到则使用坐标
        
        Args:
            state: 状态名称
        
        Returns:
            是否成功
        """
        state_info = self.STATES.get(state)
        if not state_info:
            self.log(f'未知状态: {state}')
            return False
        
        self.log(f'执行步骤: {state_info["name"]} - {state_info["desc"]}')
        
        x, y = None, None
        use_matching = state_info.get('use_image', False) and self.use_image_matching and self.image_matcher.cv_available
        
        # 尝试图像识别
        if use_matching:
            screenshot = self.take_screenshot()
            if screenshot is not None:
                # 先尝试找图 (按钮模板)
                button_template = state_info.get('button_template')
                if button_template:
                    found, bx, by, bw, bh, score = self.image_matcher.find_button(screenshot, button_template)
                    if found:
                        x, y = bx, by
                        self.log(f'找图成功: {button_template} -> ({x}, {y}), 置信度: {score:.2f}')
                
                # 再尝试找字 (文字模板)
                if x is None:
                    text_template = state_info.get('text_template')
                    if text_template:
                        found, tx, ty, tw, th, score = self.image_matcher.find_text(screenshot, text_template)
                        if found:
                            x, y = tx, ty
                            self.log(f'找字成功: {text_template} -> ({x}, {y}), 置信度: {score:.2f}')
                
                # 使用完整检测
                if x is None:
                    detected_state, score, match_info = self.detect_screen(screenshot)
                    if detected_state == state and match_info:
                        x, y = match_info['pos']
                        self.log(f'完整检测成功: {detected_state} -> ({x}, {y}), 置信度: {score:.2f}')
        
        # 使用坐标点击
        if x is None or y is None:
            x, y = self.get_button_coords(state)
            self.log(f'使用坐标点击: ({x}, {y})')
        
        # 执行点击
        success = self.click(x, y)
        
        if success:
            self.log(f'✅ {state_info["name"]} 完成')
        else:
            self.log(f'❌ {state_info["name"]} 失败')
        
        return success
    
    def run_step(self, state):
        """
        执行单步操作
        
        Args:
            state: 状态名称
        
        Returns:
            是否成功
        """
        return self.find_and_click(state)
    
    def run(self, max_loops=None):
        """
        运行自动点击流程
        
        Args:
            max_loops: 最大循环次数
        """
        if max_loops:
            self.max_loops = max_loops
        
        self.is_running = True
        self.is_paused = False
        self.loop_count = 0
        
        self.log('='*50)
        self.log('智能自动点击器启动')
        self.log('='*50)
        self.log(f'屏幕分辨率: {self.screen_width}x{self.screen_height}')
        self.log(f'匹配阈值: {self.threshold}')
        self.log(f'最大循环: {self.max_loops}')
        self.log(f'图像识别: {"已启用" if self.image_matcher.cv_available else "未启用"}')
        self.log('='*50)
        
        try:
            while self.is_running and self.loop_count < self.max_loops:
                # 检查暂停
                while self.is_paused and self.is_running:
                    time.sleep(0.1)
                
                if not self.is_running:
                    break
                
                self.loop_count += 1
                self.log(f'\n===== 第 {self.loop_count} 轮 =====')
                
                # 执行11步流程
                consecutive_unknown = 0
                for state in self.STATES:
                    if not self.is_running:
                        break
                    
                    # 检查暂停
                    while self.is_paused and self.is_running:
                        time.sleep(0.1)
                    
                    if not self.is_running:
                        break
                    
                    # 执行步骤
                    success = self.run_step(state)
                    
                    # 记录状态
                    self.state_history.append({
                        'loop': self.loop_count,
                        'state': state,
                        'success': success,
                        'time': time.strftime('%H:%M:%S')
                    })
                    
                    # 等待
                    wait_time = self.wait_time
                    if state == 'start_game_screen':
                        wait_time = 5  # 开始游戏等待更长
                    
                    if success:
                        time.sleep(wait_time)
                    else:
                        self.log(f'步骤失败，等待后重试...')
                        time.sleep(wait_time * 2)
                
                # 轮次间隔
                if self.is_running and self.loop_count < self.max_loops:
                    self.log(f'轮次完成，等待 {self.interval} 秒后开始下一轮...')
                    time.sleep(self.interval)
        
        except KeyboardInterrupt:
            self.log('用户中断')
        except Exception as e:
            self.log(f'运行错误: {e}')
            import traceback
            self.log(traceback.format_exc())
        finally:
            self.is_running = False
            self.log('='*50)
            self.log(f'运行结束，共完成 {self.loop_count} 轮')
            self.log('='*50)
    
    def stop(self):
        """停止运行"""
        self.is_running = False
        self.log('正在停止...')
    
    def pause(self):
        """暂停运行"""
        self.is_paused = True
        self.log('已暂停')
    
    def resume(self):
        """继续运行"""
        self.is_paused = False
        self.log('继续运行')
    
    def get_status(self):
        """
        获取当前状态
        
        Returns:
            状态字典
        """
        button_count, text_count = self.image_matcher.get_template_count()
        return {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'current_state': self.current_state,
            'loop_count': self.loop_count,
            'max_loops': self.max_loops,
            'screen_size': f'{self.screen_width}x{self.screen_height}',
            'image_matching': self.image_matcher.cv_available,
            'button_templates': button_count,
            'text_templates': text_count,
            'threshold': self.threshold
        }
    
    def add_template(self, name, image_path, is_text=False):
        """
        添加新模板
        
        Args:
            name: 模板名称
            image_path: 图片路径
            is_text: 是否是文字模板
        """
        return self.image_matcher.add_template(name, image_path, is_text)
    
    def set_threshold(self, threshold):
        """
        设置匹配阈值
        
        Args:
            threshold: 阈值 (0-1)
        """
        self.threshold = threshold
        self.image_matcher.set_threshold(threshold)


# 测试代码
if __name__ == '__main__':
    print("="*60)
    print("王者荣耀自动点击器 - Android无障碍服务版")
    print("完整支持找图和找字")
    print("="*60)
    
    # 创建实例
    clicker = SmartAutoClicker(
        log_callback=print
    )
    
    # 显示配置
    status = clicker.get_status()
    print(f"\n屏幕分辨率: {status['screen_size']}")
    print(f"等待时间: {clicker.wait_time}秒")
    print(f"匹配阈值: {status['threshold']}")
    print(f"最大循环: {status['max_loops']}")
    print(f"图像识别: {'可用' if status['image_matching'] else '不可用'}")
    print(f"找图模板: {status['button_templates']} 个")
    print(f"找字模板: {status['text_templates']} 个")
    
    print("\n按钮坐标:")
    for state, coords in clicker.STATES.items():
        x, y = clicker.get_button_coords(state)
        print(f"  {state}: ({x}, {y})")
    
    print("\n按 Ctrl+C 退出测试模式")
    try:
        clicker.run(max_loops=3)
    except KeyboardInterrupt:
        print("\n测试结束")
