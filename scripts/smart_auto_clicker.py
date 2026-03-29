#!/usr/bin/env python3
"""
Smart Auto Clicker - Detect game interface and click accordingly
Uses template matching to identify current screen
"""

import cv2
import numpy as np
import os
import subprocess
import time
import json

class SmartAutoClicker:
    def __init__(self):
        self.adb_path = r"D:\\Program Files\\Microvirt\\MEmu\\adb.exe"
        self.adb_device = "127.0.0.1:21503"
        self.screenshot_path = "current_screen.png"
        
        # Button templates (will be created if not exist)
        self.templates = {
            "login_popup": "template_login_popup.png",
            "match_screen": "template_match.png",
            "start_game_screen": "template_start_game.png",
            "prepare_screen": "template_prepare.png",
            "ready_game": "template_ready_game.png",
            "game_over": "template_game_over.png",
            "in_game": "template_in_game.png"
        }
        
        # Text templates for text detection
        self.text_templates = {
            "login": "text_template_login.png",  # 开始游戏文字
            "game_lobby": "text_template_game_lobby.png",  # 对战文字
            "wangzhe_xiagu": "text_template_wangzhe_xiagu.png",  # 王者峡谷文字
            "settlement_hero": "text_template_settlement_hero.png",  # 结算英雄文字
            "return_room": "text_template_return_room.png"  # 返回房间文字
        }
        
        # Button coordinates for each screen
        self.buttons = {
            "login": {"x": 641, "y": 564, "desc": "登陆"},
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
        
        # Match threshold (0.7 = 70% similarity)
        self.match_threshold = 0.7
        
        # State tracking
        self.current_state = "unknown"
        self.last_state = "unknown"
        self.state_history = []
        
    def capture_screen(self):
        """Take screenshot from device"""
        try:
            temp_file = "/sdcard/temp_screen.png"
            cmd1 = [self.adb_path, "-s", self.adb_device, "shell", "screencap", "-p", temp_file]
            cmd2 = [self.adb_path, "-s", self.adb_device, "pull", temp_file, self.screenshot_path]
            cmd3 = [self.adb_path, "-s", self.adb_device, "shell", "rm", temp_file]
            
            subprocess.run(cmd1, capture_output=True, timeout=5)
            subprocess.run(cmd2, capture_output=True, timeout=5)
            subprocess.run(cmd3, capture_output=True, timeout=3)
            
            if os.path.exists(self.screenshot_path):
                return cv2.imread(self.screenshot_path, cv2.IMREAD_COLOR)
            return None
        except Exception as e:
            print(f"[ERROR] Screenshot failed: {e}")
            return None
    
    def detect_screen(self, screenshot):
        """Detect which screen we're on using template matching"""
        if screenshot is None:
            return "unknown", 0
        
        # Convert to grayscale for matching
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        best_match = "unknown"
        best_score = 0
        
        # Try to match each template
        for screen_name, template_file in self.templates.items():
            if not os.path.exists(template_file):
                continue
            
            template = cv2.imread(template_file, cv2.IMREAD_GRAYSCALE)
            if template is None:
                continue
            
            # Check if template is smaller than screenshot
            if template.shape[0] > screenshot_gray.shape[0] or \
               template.shape[1] > screenshot_gray.shape[1]:
                continue
            
            # Template matching
            result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_score and max_val >= self.match_threshold:
                best_score = max_val
                best_match = screen_name
        
        return best_match, best_score
    
    def detect_text_template(self, screenshot, template_name):
        """Detect text template in screenshot"""
        if template_name not in self.text_templates:
            return False, 0, 0, 0, 0, 0.0
        
        template_file = self.text_templates[template_name]
        if not os.path.exists(template_file):
            return False, 0, 0, 0, 0, 0.0
        
        template = cv2.imread(template_file, cv2.IMREAD_GRAYSCALE)
        if template is None:
            return False, 0, 0, 0, 0, 0.0
        
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Check if template is smaller than screenshot
        if template.shape[0] > screenshot_gray.shape[0] or \
           template.shape[1] > screenshot_gray.shape[1]:
            return False, 0, 0, 0, 0, 0.0
        
        # Template matching
        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= self.match_threshold:
            th, tw = template.shape
            x, y = max_loc
            return True, x, y, tw, th, max_val
        
        return False, 0, 0, 0, 0, max_val
    
    def detect_screen_with_text(self, screenshot):
        """Detect screen using both button templates and text templates"""
        # First, try button templates (higher priority)
        screen, score = self.detect_screen(screenshot)

        # If found match_screen or start_game_screen, return immediately
        if screen in ["match_screen", "start_game_screen"]:
            return screen, score, None

        # Try text template for login screen (check this first before login_popup)
        has_login, x, y, w, h, login_score = self.detect_text_template(screenshot, "login")
        if has_login:
            # Found login text
            return "login", login_score, {"text": "login", "pos": (x, y, w, h)}

        # Try text template for game lobby
        has_lobby, x, y, w, h, lobby_score = self.detect_text_template(screenshot, "game_lobby")
        if has_lobby:
            # Found game lobby text
            return "game_lobby", lobby_score, {"text": "game_lobby", "pos": (x, y, w, h)}

        # If no button template match, try text template for AI mode
        has_wangzhe, x, y, w, h, text_score = self.detect_text_template(screenshot, "wangzhe_xiagu")
        if has_wangzhe:
            # Found 王者峡谷 text - this is AI mode screen
            return "ai_mode_screen", text_score, {"text": "wangzhe_xiagu", "pos": (x, y, w, h)}

        # Try text template for settlement hero
        has_settlement, x, y, w, h, settlement_score = self.detect_text_template(screenshot, "settlement_hero")
        if has_settlement:
            # Found settlement hero text
            return "settlement_hero", settlement_score, {"text": "settlement_hero", "pos": (x, y, w, h)}

        # Try text template for return room
        has_return, x, y, w, h, return_score = self.detect_text_template(screenshot, "return_room")
        if has_return:
            # Found return room text
            return "return_room", return_score, {"text": "return_room", "pos": (x, y, w, h)}

        # Return button template result
        return screen, score, None
    
    def detect_by_color(self, screenshot):
        """Alternative: detect screen by dominant colors"""
        if screenshot is None:
            return "unknown", {}
        
        # Calculate average color in different regions
        height, width = screenshot.shape[:2]
        
        regions = {
            "top_left": screenshot[0:height//4, 0:width//4],
            "top_right": screenshot[0:height//4, width*3//4:width],
            "center": screenshot[height//3:height*2//3, width//3:width*2//3],
            "bottom": screenshot[height*3//4:height, :]
        }
        
        colors = {}
        for name, region in regions.items():
            avg_color = cv2.mean(region)[:3]  # BGR
            colors[name] = avg_color
        
        # Detect screen based on colors
        # This is a fallback method when templates don't match
        
        return "unknown", colors
    
    def click(self, x, y, desc=""):
        """Click at position"""
        try:
            cmd = [self.adb_path, "-s", self.adb_device, "shell", "input", "tap", str(x), str(y)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print(f"[OK] Clicked: {desc} at ({x}, {y})")
                return True
            else:
                print(f"[FAIL] Click failed: {desc}")
                return False
        except Exception as e:
            print(f"[ERROR] Click error: {e}")
            return False
    
    def execute_action(self, screen_name):
        """Execute appropriate action for current screen"""
        if screen_name == "unknown":
            print("[WARN] Unknown screen, waiting...")
            return False
        
        if screen_name not in self.buttons:
            print(f"[WARN] No action defined for screen: {screen_name}")
            return False
        
        button = self.buttons[screen_name]
        print(f"[ACTION] Executing: {button['desc']}")
        
        success = self.click(button["x"], button["y"], button["desc"])
        
        # Wait after click
        wait_time = 3
        if screen_name == "start_game_screen":
            wait_time = 5
        
        if success:
            print(f"[INFO] Waiting {wait_time}s for screen change...")
            time.sleep(wait_time)
        
        return success
    
    def run(self, max_loops=100, interval=2):
        """Main loop - detect screen and execute action"""
        print("="*60)
        print("SMART AUTO CLICKER")
        print("="*60)
        print("Mode: Auto-detect interface and click")
        print(f"Match threshold: {self.match_threshold}")
        print(f"Max loops: {max_loops}")
        print(f"Check interval: {interval}s")
        print("="*60)
        
        print("\nTemplate files:")
        for name, file in self.templates.items():
            exists = "[OK]" if os.path.exists(file) else "[--]"
            print(f"  {exists} {name}: {file}")
        
        print("\nText template files:")
        for name, file in self.text_templates.items():
            exists = "[OK]" if os.path.exists(file) else "[--]"
            print(f"  {exists} {name}: {file}")
        
        print("\nButton coordinates:")
        for name, btn in self.buttons.items():
            print(f"  {name}: ({btn['x']}, {btn['y']}) - {btn['desc']}")
        
        print("\n" + "="*60)
        print("Starting smart detection loop...")
        print("Press Ctrl+C to stop")
        print("="*60)
        
        loop_count = 0
        consecutive_unknown = 0
        max_unknown = 5
        
        try:
            while loop_count < max_loops:
                loop_count += 1
                print(f"\n[Loop {loop_count}/{max_loops}]")
                
                # Take screenshot
                print("[1] Capturing screen...")
                screenshot = self.capture_screen()
                
                if screenshot is None:
                    print("[ERROR] Failed to capture screen")
                    time.sleep(interval)
                    continue
                
                # Detect screen with text templates
                print("[2] Detecting interface...")
                screen_name, match_score, text_info = self.detect_screen_with_text(screenshot)
                
                # Fallback to color detection
                if screen_name == "unknown":
                    print("[2b] Trying color detection...")
                    _, colors = self.detect_by_color(screenshot)
                    # You can add color-based detection logic here
                
                if text_info:
                    print(f"[RESULT] Detected: {screen_name} (text: {text_info['text']}, score: {match_score:.2f})")
                else:
                    print(f"[RESULT] Detected: {screen_name} (score: {match_score:.2f})")
                
                # Update state
                self.last_state = self.current_state
                self.current_state = screen_name
                self.state_history.append({
                    "loop": loop_count,
                    "state": screen_name,
                    "score": match_score,
                    "time": time.strftime("%H:%M:%S")
                })
                
                # Handle unknown screens
                if screen_name == "unknown":
                    consecutive_unknown += 1
                    print(f"[WARN] Unknown screen ({consecutive_unknown}/{max_unknown})")

                    # Don't stop, just continue looping
                    time.sleep(interval)
                    continue
                else:
                    consecutive_unknown = 0
                
                # Execute action
                print("[3] Executing action...")
                success = self.execute_action(screen_name)
                
                if not success:
                    print("[WARN] Action failed, will retry")
                
                # Wait before next loop
                print(f"[4] Waiting {interval}s...")
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n[STOP] User interrupted")
        
        # Summary
        print("\n" + "="*60)
        print("EXECUTION SUMMARY")
        print("="*60)
        print(f"Total loops: {loop_count}")
        print(f"Final state: {self.current_state}")
        
        # Show state history
        if self.state_history:
            print("\nState history (last 10):")
            for entry in self.state_history[-10:]:
                print(f"  {entry['time']} Loop {entry['loop']}: {entry['state']} ({entry['score']:.2f})")

def main():
    clicker = SmartAutoClicker()
    clicker.run(max_loops=1000, interval=2)  # Increase max loops for continuous running

if __name__ == "__main__":
    main()