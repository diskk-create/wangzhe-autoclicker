#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WangZhe Auto Clicker v3.4.1 - Android Floating Window Version
使用Android原生API实现真正的悬浮窗
"""

import threading
import time
import os

# Try to import Android API
try:
    from jnius import autoclass
    PYJNIUS_AVAILABLE = True
except:
    PYJNIUS_AVAILABLE = False

ANDROID_API_AVAILABLE = False
mActivity = None

# Android classes
if PYJNIUS_AVAILABLE:
    try:
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        WindowManager = autoclass('android.view.WindowManager')
        WindowManagerLayoutParams = autoclass('android.view.WindowManager$LayoutParams')
        PixelFormat = autoclass('android.graphics.PixelFormat')
        Gravity = autoclass('android.view.Gravity')
        Context = autoclass('android.content.Context')
        ANDROID_CLASSES_AVAILABLE = True
    except:
        ANDROID_CLASSES_AVAILABLE = False
else:
    ANDROID_CLASSES_AVAILABLE = False

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, RoundedRectangle, Line
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import NumericProperty, BooleanProperty, ListProperty

print("=" * 50)
print("WangZhe Floating Ball v3.4.1")
print("Android Native Floating Window")
print("=" * 50)


class FloatingBall(Widget):
    """Floating ball widget"""
    
    ball_size = NumericProperty(70)
    is_expanded = BooleanProperty(False)
    ball_color = ListProperty([0.2, 0.6, 0.9, 0.95])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (70, 70)
        self.pos = (100, 100)
        self.touch_start_pos = None
        self.is_dragging = False
        self.drag_threshold = 15
        self.bind(pos=self.update_ball, size=self.update_ball)
    
    def update_ball(self, *args):
        """Update ball graphics"""
        self.canvas.clear()
        with self.canvas:
            # Outer glow
            Color(0.2, 0.6, 0.9, 0.2)
            Ellipse(pos=(self.x - 5, self.y - 5), size=(self.width + 10, self.height + 10))
            # Shadow
            Color(0, 0, 0, 0.4)
            Ellipse(pos=(self.x + 4, self.y - 4), size=self.size)
            # Main ball
            Color(*self.ball_color)
            Ellipse(pos=self.pos, size=self.size)
            # Highlight
            Color(1, 1, 1, 0.4)
            Ellipse(pos=(self.x + 12, self.y + 25), size=(30, 18))
            # Play icon
            Color(1, 1, 1, 0.9)
            cx, cy = self.center
            points = [cx - 8, cy - 10, cx - 8, cy + 10, cx + 12, cy]
            Line(points=points, width=2, close=False)


class FloatingMenu(BoxLayout):
    """Expandable menu panel"""
    
    def __init__(self, app_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (200, 320)
        self.opacity = 0
        self.pos = (-1000, -1000)
        self.app_instance = app_instance
        self.padding = [10, 10, 10, 10]
        self.spacing = 8
        
        with self.canvas.before:
            Color(0.12, 0.12, 0.12, 0.95)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])
        
        self.bind(pos=self.update_bg, size=self.update_bg)
        self._build_menu()
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def _build_menu(self):
        title = Label(
            text="[b]WangZhe Clicker[/b]\n[size=11]v3.4.1[/size]",
            markup=True,
            size_hint_y=None,
            height=50,
            color=(0.95, 0.95, 0.95, 1),
            halign='center'
        )
        title.bind(texture_size=title.setter('size'))
        self.add_widget(title)
        
        self.status_label = Label(
            text="[color=00ff00]● Ready[/color]",
            markup=True,
            size_hint_y=None,
            height=30,
            font_size=12,
            color=(0.8, 0.8, 0.8, 1)
        )
        self.add_widget(self.status_label)
        
        buttons = [
            ("▶ Start", self._on_start, (0.15, 0.6, 0.25, 0.9)),
            ("⏸ Stop", self._on_stop, (0.7, 0.25, 0.25, 0.9)),
            ("🔄 Test", self._on_test, (0.25, 0.45, 0.75, 0.9)),
            ("✕ Exit", self._on_exit, (0.4, 0.4, 0.4, 0.9)),
        ]
        
        for text, callback, color in buttons:
            btn = Button(
                text=text,
                size_hint_y=None,
                height=45,
                background_color=color,
                background_normal='',
                font_size=14,
                bold=True
            )
            btn.bind(on_press=callback)
            self.add_widget(btn)
    
    def _on_start(self, instance):
        if self.app_instance:
            self.app_instance.start_flow()
            self.status_label.text = "[color=00ff00]● Running[/color]"
    
    def _on_stop(self, instance):
        if self.app_instance:
            self.app_instance.stop_flow()
            self.status_label.text = "[color=ffff00]● Stopped[/color]"
    
    def _on_test(self, instance):
        if self.app_instance:
            self.app_instance.test_click()
    
    def _on_exit(self, instance):
        if self.app_instance:
            self.app_instance.exit_app()
    
    def show(self, pos):
        self.pos = pos
        anim = Animation(opacity=1, duration=0.2, t='out_quad')
        anim.start(self)
    
    def hide(self):
        anim = Animation(opacity=0, duration=0.15, t='in_quad')
        anim.bind(on_complete=lambda *args: setattr(self, 'pos', (-1000, -1000)))
        anim.start(self)


class SimpleClicker:
    """Simple clicker for Android"""
    
    def __init__(self):
        self.screen_width = 1280
        self.screen_height = 720
        self.has_root = False
        self.is_initialized = False
        self.is_running = False
        Clock.schedule_once(self._init_android, 0.5)
    
    def _init_android(self, dt):
        global ANDROID_API_AVAILABLE, mActivity
        
        if PYJNIUS_AVAILABLE:
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                mActivity = PythonActivity.mActivity
                
                display = mActivity.getWindowManager().getDefaultDisplay()
                Point = autoclass('android.graphics.Point')()
                display.getSize(Point)
                self.screen_width = Point.x
                self.screen_height = Point.y
                
                self._check_root()
                ANDROID_API_AVAILABLE = True
                self.is_initialized = True
                print(f"Android: {self.screen_width}x{self.screen_height}, ROOT: {self.has_root}")
            except Exception as e:
                print(f"Android init failed: {e}")
    
    def _check_root(self):
        try:
            from jnius import autoclass
            Runtime = autoclass('java.lang.Runtime')
            process = Runtime.getRuntime().exec("which su")
            process.waitFor()
            self.has_root = (process.exitValue() == 0)
        except:
            self.has_root = False
    
    def click(self, x, y):
        try:
            from jnius import autoclass
            Runtime = autoclass('java.lang.Runtime')
            TimeUnit = autoclass('java.util.concurrent.TimeUnit')
            runtime = Runtime.getRuntime()
            
            cmd = f"input tap {x} {y}"
            process = runtime.exec(cmd)
            process.waitFor(1, TimeUnit.SECONDS)
            
            if process.exitValue() == 0:
                print(f"Click OK: ({x}, {y})")
                return True
            
            if self.has_root:
                cmd = f"su -c input tap {x} {y}"
                process = runtime.exec(cmd)
                process.waitFor(1, TimeUnit.SECONDS)
                if process.exitValue() == 0:
                    print(f"ROOT Click OK: ({x}, {y})")
                    return True
            
            return False
        except Exception as e:
            print(f"Click failed: {e}")
            return False


class FloatingBallApp(App):
    """Main app with floating ball"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clicker = SimpleClicker()
        self.is_running = False
        self.floating_ball = None
        self.floating_menu = None
        self.is_android = False
    
    def build(self):
        """Build the app"""
        # Check if running on Android
        self.is_android = PYJNIUS_AVAILABLE
        
        if self.is_android:
            # Android: Setup floating window
            self._setup_android_floating_window()
        else:
            # Desktop: Normal window
            Window.size = (350, 400)
            Window.left = 50
            Window.top = 50
            try:
                Window.always_on_top = True
            except:
                pass
        
        # Main layout
        layout = FloatLayout()
        
        # Create floating ball
        self.floating_ball = FloatingBall()
        self.floating_ball.pos = (140, 165)
        layout.add_widget(self.floating_ball)
        
        # Create menu
        self.floating_menu = FloatingMenu(app_instance=self)
        self.floating_menu.pos = (-1000, -1000)
        layout.add_widget(self.floating_menu)
        
        # Bind touch events
        self._bind_touch_events(layout)
        
        return layout
    
    def _setup_android_floating_window(self):
        """Setup Android floating window"""
        if not ANDROID_CLASSES_AVAILABLE:
            print("Android classes not available")
            return
        
        try:
            # Get window parameters
            window = mActivity.getWindow()
            params = window.getAttributes()
            
            # Set window to floating mode
            # Note: This requires SYSTEM_ALERT_WINDOW permission
            # and may not work on all Android versions
            
            print("Attempting to setup floating window...")
            
            # Try to minimize window
            # This is a simplified approach - real floating window
            # needs Android Service and WindowManager
            
        except Exception as e:
            print(f"Floating window setup failed: {e}")
    
    def _bind_touch_events(self, layout):
        """Bind touch events"""
        original_touch_down = layout.on_touch_down
        original_touch_up = layout.on_touch_up
        original_touch_move = layout.on_touch_move
        
        def custom_touch_down(touch):
            if self.floating_ball.collide_point(*touch.pos):
                self.floating_ball.touch_start_pos = touch.pos
                self.floating_ball.is_dragging = False
                return True
            elif self.floating_menu.opacity > 0:
                if not self.floating_menu.collide_point(*touch.pos):
                    self._collapse_menu()
            return original_touch_down(touch) if original_touch_down else False
        
        def custom_touch_move(touch):
            if self.floating_ball.touch_start_pos:
                dx = touch.pos[0] - self.floating_ball.touch_start_pos[0]
                dy = touch.pos[1] - self.floating_ball.touch_start_pos[1]
                distance = (dx**2 + dy**2) ** 0.5
                
                if distance > self.floating_ball.drag_threshold:
                    self.floating_ball.is_dragging = True
                    new_x = touch.pos[0] - self.floating_ball.width / 2
                    new_y = touch.pos[1] - self.floating_ball.height / 2
                    self.floating_ball.pos = (new_x, new_y)
                return True
            return original_touch_move(touch) if original_touch_move else False
        
        def custom_touch_up(touch):
            if self.floating_ball.touch_start_pos:
                if not self.floating_ball.is_dragging:
                    self._toggle_menu()
                self.floating_ball.touch_start_pos = None
                self.floating_ball.is_dragging = False
                return True
            return original_touch_up(touch) if original_touch_up else False
        
        layout.on_touch_down = custom_touch_down
        layout.on_touch_up = custom_touch_up
        layout.on_touch_move = custom_touch_move
    
    def _toggle_menu(self):
        """Toggle menu"""
        if self.floating_menu.opacity == 0:
            self._expand_menu()
        else:
            self._collapse_menu()
    
    def _expand_menu(self):
        """Expand menu"""
        ball = self.floating_ball
        menu = self.floating_menu
        
        menu_x = ball.x + ball.width + 15
        menu_y = ball.center_y - menu.height / 2
        
        menu_x = min(menu_x, Window.width - menu.width - 10)
        menu_y = max(10, min(menu_y, Window.height - menu.height - 10))
        
        menu.show((menu_x, menu_y))
        ball.is_expanded = True
        ball.ball_color = [0.3, 0.8, 0.3, 0.95]
    
    def _collapse_menu(self):
        """Collapse menu"""
        self.floating_menu.hide()
        self.floating_ball.is_expanded = False
        self.floating_ball.ball_color = [0.2, 0.6, 0.9, 0.95]
    
    def start_flow(self):
        """Start flow"""
        print("Start flow")
        self.is_running = True
        self.floating_ball.ball_color = [0.2, 0.9, 0.3, 0.95]
        
        def run_flow():
            while self.is_running:
                self.clicker.click(640, 360)
                time.sleep(2)
        
        thread = threading.Thread(target=run_flow, daemon=True)
        thread.start()
    
    def stop_flow(self):
        """Stop flow"""
        print("Stop flow")
        self.is_running = False
        self.floating_ball.ball_color = [0.2, 0.6, 0.9, 0.95]
    
    def test_click(self):
        """Test click"""
        print("Test click")
        self.clicker.click(640, 360)
    
    def exit_app(self):
        """Exit app"""
        print("Exit")
        self.stop_flow()
        App.get_running_app().stop()


if __name__ == '__main__':
    FloatingBallApp().run()
