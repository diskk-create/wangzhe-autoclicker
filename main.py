#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WangZhe Auto Clicker - Working Version
With Android API (delayed initialization)
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
import time

print("========================================")
print("WangZhe Auto Clicker Starting")
print("========================================")

# Global variables
PYJNIUS_AVAILABLE = False
ANDROID_API_AVAILABLE = False
mActivity = None


class SimpleClicker:
    """Simple Clicker - With Android API"""

    def __init__(self):
        self.is_initialized = False
        self.screen_width = 1280
        self.screen_height = 720
        self.has_root = False

        # Delay initialization
        Clock.schedule_once(self._init_android, 0.5)

    def _init_android(self, dt):
        """Initialize Android (delayed)"""
        global PYJNIUS_AVAILABLE, ANDROID_API_AVAILABLE, mActivity

        try:
            print("Initializing Android API...")
            from jnius import autoclass
            PYJNIUS_AVAILABLE = True

            # Get activity
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            mActivity = PythonActivity.mActivity

            # Get screen size
            display = mActivity.getWindowManager().getDefaultDisplay()
            Point = autoclass('android.graphics.Point')()
            display.getSize(Point)
            self.screen_width = Point.x
            self.screen_height = Point.y

            ANDROID_API_AVAILABLE = True
            self.is_initialized = True

            print(f"Android initialized: {self.screen_width}x{self.screen_height}")

        except Exception as e:
            print(f"Android init failed: {e}")
            PYJNIUS_AVAILABLE = False
            ANDROID_API_AVAILABLE = False
            self.is_initialized = True  # Still mark as initialized for test mode

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

            # Try method 1: input tap (needs ROOT or shell permission)
            cmd = f"input tap {x} {y}"
            print(f"[CLICK] Method 1: Executing shell command: {cmd}")
            process = runtime.exec(cmd)
            process.waitFor(1, TimeUnit.SECONDS)

            exit_code = process.exitValue()
            print(f"[CLICK] Method 1 result: exit code = {exit_code}")

            if exit_code == 0:
                print(f"[CLICK] SUCCESS - Click executed via input tap")
                return True
            else:
                print(f"[CLICK] Method 1 failed, exit code: {exit_code}")
                print(f"[CLICK] Trying method 2...")

                # Try method 2: su -c input tap (with ROOT)
                cmd2 = f"su -c input tap {x} {y}"
                print(f"[CLICK] Method 2: Executing with ROOT: {cmd2}")
                process2 = runtime.exec(cmd2)
                process2.waitFor(1, TimeUnit.SECONDS)

                exit_code2 = process2.exitValue()
                print(f"[CLICK] Method 2 result: exit code = {exit_code2}")

                if exit_code2 == 0:
                    print(f"[CLICK] SUCCESS - Click executed via ROOT")
                    return True
                else:
                    print(f"[CLICK] Method 2 failed, exit code: {exit_code2}")
                    return False

        except Exception as e:
            print(f"[CLICK] ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_screen_size(self):
        """Get screen size"""
        return self.screen_width, self.screen_height


class WangZheApp(App):
    """WangZhe Auto Clicker"""

    title = "WangZhe Auto Clicker v3.0.7"

    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Title
        title = Label(
            text="WangZhe Auto Clicker\nv3.0.7",
            size_hint_y=None,
            height=100,
            font_size='22sp',
            bold=True
        )
        layout.add_widget(title)

        # Status
        self.status = Label(
            text="Status: Initializing...",
            size_hint_y=None,
            height=100,
            font_size='16sp'
        )
        layout.add_widget(self.status)

        # Click counter
        self.click_count = 0

        # Initialize clicker
        self.clicker = SimpleClicker()

        # Update status after 1 second
        Clock.schedule_once(self._update_status, 1.0)

        # Scroll area
        scroll = ScrollView()
        btns = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        btns.bind(minimum_height=btns.setter('height'))

        # Test click button
        test_btn = Button(text="Test Click (Screen Center)", size_hint_y=None, height=70)
        test_btn.bind(on_press=self._test_click)
        btns.add_widget(test_btn)

        # Refresh status
        refresh_btn = Button(text="Refresh Status", size_hint_y=None, height=70)
        refresh_btn.bind(on_press=self._refresh)
        btns.add_widget(refresh_btn)

        scroll.add_widget(btns)
        layout.add_widget(scroll)

        print("UI build completed")
        return layout

    def _update_status(self, dt):
        """Update status"""
        if self.clicker.is_initialized and ANDROID_API_AVAILABLE:
            w, h = self.clicker.get_screen_size()
            self.status.text = f"Status: OK\nScreen: {w}x{h}"
        else:
            self.status.text = "Status: Test Mode\nScreen: 1280x720"

    def _test_click(self, instance):
        """Test click"""
        self.click_count += 1
        print(f"[BUTTON] Test Click button pressed (count: {self.click_count})")
        print(f"[BUTTON] Calling clicker.click(640, 360)")
        self.clicker.click(640, 360)
        self.status.text = f"Clicked: (640, 360)\nCount: {self.click_count}"
        print(f"[BUTTON] Click function returned")

    def _refresh(self, instance):
        """Refresh"""
        self._update_status(0)


if __name__ == '__main__':
    print("========================================")
    print("Starting Kivy App")
    print("========================================")
    try:
        WangZheApp().run()
    except Exception as e:
        print(f"Startup Error: {e}")
        import traceback
        traceback.print_exc()
