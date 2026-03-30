#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WangZhe Auto Clicker - Floating Window Version
With permissions and floating window support
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
import time
import threading

print("========================================")
print("WangZhe Auto Clicker Starting")
print("========================================")

# Global variables
PYJNIUS_AVAILABLE = False
ANDROID_API_AVAILABLE = False
mActivity = None
CV_AVAILABLE = False

# Try to load OpenCV
try:
    import cv2
    import numpy as np
    CV_AVAILABLE = True
    print("OpenCV loaded successfully")
except ImportError:
    print("OpenCV not available, image recognition disabled")


class ImageMatcher:
    """Image matcher for template matching"""

    def __init__(self, template_dir='templates', threshold=0.9):
        self.template_dir = template_dir
        self.threshold = threshold
        self.cv_available = CV_AVAILABLE
        self.button_templates = {}
        self.text_templates = {}

        if self.cv_available:
            self._load_templates()

    def _load_templates(self):
        """Load template images"""
        import os
        if not os.path.exists(self.template_dir):
            print(f"Template directory not found: {self.template_dir}")
            return

        print("Loading templates...")

        # Button templates
        button_files = {
            'login': 'template_login.png',
            'login_popup': 'template_login_popup.png',
            'game_lobby': 'template_game_lobby.png',
            'match_screen': 'template_match.png',
            'ai_mode_screen': 'template_ai_mode.png',
            'start_game_screen': 'template_start_game.png',
            'prepare_screen': 'template_prepare.png',
            'ready_game': 'template_ready_game.png',
            'game_over': 'template_game_over.png',
            'settlement_hero': 'template_settlement.png',
            'return_room': 'template_return.png',
        }

        for name, filename in button_files.items():
            path = os.path.join(self.template_dir, filename)
            if os.path.exists(path):
                template = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                if template is not None:
                    self.button_templates[name] = template
                    print(f"Loaded button template: {name}")

    def find_template(self, screenshot, template_key):
        """Find template in screenshot"""
        if not self.cv_available or screenshot is None:
            return False, 0, 0, 0, 0, 0

        if template_key not in self.button_templates:
            return False, 0, 0, 0, 0, 0

        try:
            template = self.button_templates[template_key]
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= self.threshold:
                h, w = template.shape
                return True, max_loc[0], max_loc[1], w, h, max_val
        except Exception as e:
            print(f"Template matching error: {e}")

        return False, 0, 0, 0, 0, 0


class SimpleClicker:
    """Simple Clicker - With Android API and Permissions"""

    # 11-step flow
    STATES = {
        'login': {
            'name': 'Login',
            'desc': 'Click "Start Game"',
            'next': 'login_popup',
            'coords': (641, 564)
        },
        'login_popup': {
            'name': 'Close Popup',
            'desc': 'Close login popup',
            'next': 'game_lobby',
            'coords': (640, 360)
        },
        'game_lobby': {
            'name': 'Game Lobby',
            'desc': 'Click "Battle"',
            'next': 'match_screen',
            'coords': (1178, 567)
        },
        'match_screen': {
            'name': 'Match Screen',
            'desc': 'Click match button',
            'next': 'ai_mode_screen',
            'coords': (640, 600)
        },
        'ai_mode_screen': {
            'name': 'AI Mode',
            'desc': 'Select AI mode',
            'next': 'start_game_screen',
            'coords': (640, 360)
        },
        'start_game_screen': {
            'name': 'Start Game',
            'desc': 'Click start game',
            'next': 'prepare_screen',
            'coords': (1153, 575)
        },
        'prepare_screen': {
            'name': 'Prepare',
            'desc': 'Click prepare button',
            'next': 'ready_game',
            'coords': (1153, 575)
        },
        'ready_game': {
            'name': 'Ready',
            'desc': 'Click ready button',
            'next': 'game_over',
            'coords': (1153, 575)
        },
        'game_over': {
            'name': 'Game Over',
            'desc': 'Continue after game',
            'next': 'settlement_hero',
            'coords': (640, 360)
        },
        'settlement_hero': {
            'name': 'Settlement',
            'desc': 'Click continue',
            'next': 'return_room',
            'coords': (640, 680)
        },
        'return_room': {
            'name': 'Return Room',
            'desc': 'Return to room',
            'next': 'game_lobby',
            'coords': (640, 680)
        }
    }

    def __init__(self):
        self.is_initialized = False
        self.screen_width = 1280
        self.screen_height = 720
        self.has_root = False
        self.has_permissions = False
        self.matcher = None
        self.current_state = 'login'
        self.is_running = False

        # Delay initialization - start after UI is ready
        Clock.schedule_once(self._init_android, 2.0)
        Clock.schedule_once(self._request_permissions, 2.5)
        Clock.schedule_once(self._init_matcher, 3.0)

    def _init_android(self, dt):
        """Initialize Android (delayed)"""
        global PYJNIUS_AVAILABLE, ANDROID_API_AVAILABLE, mActivity

        try:
            print("Initializing Android API...")
            from jnius import autoclass
            PYJNIUS_AVAILABLE = True
            print("Pyjnius loaded successfully")

            # Get activity with timeout
            print("Getting PythonActivity...")
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            mActivity = PythonActivity.mActivity
            print(f"Activity: {mActivity}")

            # Get screen size
            print("Getting screen size...")
            display = mActivity.getWindowManager().getDefaultDisplay()
            Point = autoclass('android.graphics.Point')()
            display.getSize(Point)
            self.screen_width = Point.x
            self.screen_height = Point.y
            print(f"Screen size: {self.screen_width}x{self.screen_height}")

            # Check ROOT
            print("Checking ROOT...")
            self._check_root()

            ANDROID_API_AVAILABLE = True
            self.is_initialized = True

            print(f"Android initialized successfully")
            print(f"ROOT access: {self.has_root}")

        except Exception as e:
            print(f"Android init failed: {e}")
            import traceback
            traceback.print_exc()
            PYJNIUS_AVAILABLE = False
            ANDROID_API_AVAILABLE = False
            self.is_initialized = True
            print("Continuing without Android API")

    def _check_root(self):
        """Check if device has ROOT access"""
        try:
            from jnius import autoclass
            Runtime = autoclass('java.lang.Runtime')
            runtime = Runtime.getRuntime()
            process = runtime.exec("su")
            process.waitFor()
            self.has_root = True
            print("ROOT access available")
        except:
            self.has_root = False
            print("ROOT access not available")

    def _request_permissions(self, dt):
        """Request necessary permissions"""
        print("Checking permissions...")
        self.has_permissions = True
        print("Permissions check skipped (will check on use)")

    def _init_matcher(self, dt):
        """Initialize image matcher"""
        try:
            self.matcher = ImageMatcher(threshold=0.9)
            print(f"Image matcher initialized: CV={CV_AVAILABLE}")
        except Exception as e:
            print(f"Image matcher init failed: {e}")
            self.matcher = None

    def capture_screen(self):
        """Capture screen"""
        if not CV_AVAILABLE:
            print("[CAPTURE] OpenCV not available")
            return None

        if not ANDROID_API_AVAILABLE:
            print("[CAPTURE] Android API not available")
            return None

        try:
            from jnius import autoclass
            Runtime = autoclass('java.lang.Runtime')
            TimeUnit = autoclass('java.util.concurrent.TimeUnit')
            runtime = Runtime.getRuntime()

            # Capture screen to file
            process = runtime.exec("screencap -p /sdcard/screen.png")
            process.waitFor(2, TimeUnit.SECONDS)

            # Read image
            import cv2
            img = cv2.imread("/sdcard/screen.png")

            if img is not None:
                print(f"[CAPTURE] Screen captured: {img.shape}")
                return img
            else:
                print("[CAPTURE] Failed to read screenshot")
                return None

        except Exception as e:
            print(f"[CAPTURE] Error: {e}")
            return None

    def click(self, x, y):
        """Click screen"""
        print(f"[CLICK] Attempting to click at ({x}, {y})")

        if not ANDROID_API_AVAILABLE:
            print(f"[CLICK] Test mode - Android API not available")
            return True

        try:
            from jnius import autoclass
            Runtime = autoclass('java.lang.Runtime')
            TimeUnit = autoclass('java.util.concurrent.TimeUnit')
            runtime = Runtime.getRuntime()

            # Method 1: input tap
            cmd = f"input tap {x} {y}"
            print(f"[CLICK] Method 1: {cmd}")
            process = runtime.exec(cmd)
            process.waitFor(1, TimeUnit.SECONDS)

            exit_code = process.exitValue()
            print(f"[CLICK] Method 1 result: exit code = {exit_code}")

            if exit_code == 0:
                print(f"[CLICK] SUCCESS")
                return True
            else:
                # Method 2: su -c input tap
                cmd2 = f"su -c input tap {x} {y}"
                print(f"[CLICK] Method 2: {cmd2}")
                process2 = runtime.exec(cmd2)
                process2.waitFor(1, TimeUnit.SECONDS)

                exit_code2 = process2.exitValue()
                print(f"[CLICK] Method 2 result: exit code = {exit_code2}")

                if exit_code2 == 0:
                    print(f"[CLICK] SUCCESS")
                    return True
                else:
                    print(f"[CLICK] FAILED")
                    return False

        except Exception as e:
            print(f"[CLICK] ERROR: {e}")
            return False

    def get_screen_size(self):
        """Get screen size"""
        return self.screen_width, self.screen_height

    def run_flow_step(self, state_name=None):
        """Run one step of the flow"""
        if state_name is None:
            state_name = self.current_state

        if state_name not in self.STATES:
            print(f"Unknown state: {state_name}")
            return False

        state = self.STATES[state_name]
        print(f"\n[STEP] {state['name']}: {state['desc']}")

        # Try image matching first
        x, y = None, None
        if self.matcher and CV_AVAILABLE:
            print(f"[STEP] Trying image matching...")
            screenshot = self.capture_screen()
            if screenshot is not None:
                # Try to find template
                found, fx, fy, fw, fh, score = self.matcher.find_template(screenshot, state_name)
                if found and score >= 0.9:
                    x = fx + fw // 2  # Center of matched region
                    y = fy + fh // 2
                    print(f"[STEP] Image matched at ({x}, {y}), score={score:.2f}")

        # Fallback to coordinates
        if x is None or y is None:
            x, y = state['coords']
            # Scale coordinates to screen size
            scale_x = self.screen_width / 1280
            scale_y = self.screen_height / 720
            scaled_x = int(x * scale_x)
            scaled_y = int(y * scale_y)
            print(f"[STEP] Using coordinates: ({scaled_x}, {scaled_y})")
            x, y = scaled_x, scaled_y

        # Click
        result = self.click(x, y)

        # Move to next state
        self.current_state = state['next']

        return result

    def run_full_flow(self, callback=None):
        """Run complete 11-step flow"""
        if self.is_running:
            print("Flow already running")
            return

        self.is_running = True
        self.current_state = 'login'

        def run():
            step = 0
            while self.is_running and step < 11:
                step += 1
                result = self.run_flow_step()

                if callback:
                    callback(f"Step {step}/11: {self.STATES[self.current_state]['name']}")

                if not result:
                    print(f"Flow stopped at step {step}")
                    break

                time.sleep(2)  # Wait between steps

            self.is_running = False
            if callback:
                callback("Flow completed!")

        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()


class FloatingBoxLayout(BoxLayout):
    """Floating window layout with transparency"""

    def __init__(self, **kwargs):
        super(FloatingBoxLayout, self).__init__(**kwargs)

        # Set transparency
        with self.canvas.before:
            Color(0, 0, 0, 0.5)  # 50% transparent black
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos


class WangZheApp(App):
    """WangZhe Auto Clicker - Floating Window"""

    title = "WangZhe Auto Clicker v3.3.3"

    def build(self):
        # Set window transparency and size
        Window.size = (300, 500)  # Floating window size
        Window.left = 100
        Window.top = 100

        # Create floating layout
        layout = FloatingBoxLayout(orientation='vertical', padding=10, spacing=10)

        # Title
        title = Label(
            text="WangZhe Clicker\nv3.3.3 - Debug",
            size_hint_y=None,
            height=60,
            font_size='16sp',
            bold=True
        )
        layout.add_widget(title)

        # Status
        self.status = Label(
            text="Status: Initializing...",
            size_hint_y=None,
            height=60,
            font_size='12sp'
        )
        layout.add_widget(self.status)

        # Click counter
        self.click_count = 0

        # Initialize clicker
        self.clicker = SimpleClicker()

        # Update status after 2 seconds
        Clock.schedule_once(self._update_status, 2.0)

        # Buttons
        btn_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        btn_layout.bind(minimum_height=btn_layout.setter('height'))

        # Run full flow button
        flow_btn = Button(text="Run Flow (11 Steps)", size_hint_y=None, height=50)
        flow_btn.bind(on_press=self._run_flow)
        btn_layout.add_widget(flow_btn)

        # Test click button
        test_btn = Button(text="Test Click", size_hint_y=None, height=50)
        test_btn.bind(on_press=self._test_click)
        btn_layout.add_widget(test_btn)

        # Quick step buttons
        for state_name in ['login', 'game_lobby', 'start_game_screen']:
            state = SimpleClicker.STATES[state_name]
            btn = Button(text=f"{state['name']}", size_hint_y=None, height=40)
            btn.state_name = state_name
            btn.bind(on_press=self._run_step)
            btn_layout.add_widget(btn)

        # Refresh status
        refresh_btn = Button(text="Refresh Status", size_hint_y=None, height=50)
        refresh_btn.bind(on_press=self._refresh)
        btn_layout.add_widget(refresh_btn)

        # Exit button
        exit_btn = Button(text="Exit", size_hint_y=None, height=50)
        exit_btn.bind(on_press=self._exit_app)
        btn_layout.add_widget(exit_btn)

        layout.add_widget(btn_layout)

        print("UI build completed")
        return layout

    def _update_status(self, dt):
        """Update status"""
        if self.clicker.is_initialized and ANDROID_API_AVAILABLE:
            w, h = self.clicker.get_screen_size()
            cv_status = "CV OK" if CV_AVAILABLE else "CV N/A"
            root_status = "ROOT OK" if self.clicker.has_root else "ROOT N/A"
            perm_status = "PERM OK" if self.clicker.has_permissions else "PERM N/A"
            self.status.text = f"Screen: {w}x{h}\n{cv_status}\n{root_status}\n{perm_status}"
        else:
            self.status.text = "Status: Test Mode"

    def _run_flow(self, instance):
        """Run full flow"""
        print(f"[BUTTON] Run Full Flow button pressed")
        self.status.text = "Running flow..."
        self.clicker.run_full_flow(callback=self._update_flow_status)

    def _update_flow_status(self, message):
        """Update flow status"""
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: setattr(self.status, 'text', message), 0)

    def _test_click(self, instance):
        """Test click"""
        self.click_count += 1
        print(f"[BUTTON] Test Click button pressed (count: {self.click_count})")
        self.clicker.click(640, 360)
        self.status.text = f"Clicked: (640, 360)\nCount: {self.click_count}"

    def _run_step(self, instance):
        """Run single step"""
        state_name = instance.state_name
        print(f"[BUTTON] Run step: {state_name}")
        self.clicker.run_flow_step(state_name)
        self.status.text = f"Step: {SimpleClicker.STATES[state_name]['name']}"

    def _refresh(self, instance):
        """Refresh"""
        self._update_status(0)

    def _exit_app(self, instance):
        """Exit app"""
        print("[APP] Exit requested")
        App.get_running_app().stop()


if __name__ == '__main__':
    print("========================================")
    print("Starting Kivy App - Floating Window")
    print("========================================")
    try:
        WangZheApp().run()
    except Exception as e:
        print(f"Startup Error: {e}")
        import traceback
        traceback.print_exc()
