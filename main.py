#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WangZhe Auto Clicker v3.4.0 - Floating Ball Mode
Features:
- Floating ball on desktop (draggable)
- Click to expand/collapse menu
- Always on top
- Smooth animations
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

# Try to import OpenCV
try:
    import cv2
    import numpy as np
    CV_AVAILABLE = True
except:
    CV_AVAILABLE = False

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
print("WangZhe Floating Ball v3.4.0")
print("=" * 50)


class FloatingBall(Widget):
    """Floating ball widget - draggable ball with animations"""
    
    ball_size = NumericProperty(70)
    is_expanded = BooleanProperty(False)
    ball_color = ListProperty([0.2, 0.6, 0.9, 0.95])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (70, 70)
        self.pos = (100, 100)
        
        # Touch tracking
        self.touch_start_pos = None
        self.is_dragging = False
        self.drag_threshold = 15
        
        # Draw ball
        self.bind(pos=self.update_ball, size=self.update_ball)
    
    def update_ball(self, *args):
        """Update ball graphics"""
        self.canvas.clear()
        with self.canvas:
            # Outer glow
            Color(0.2, 0.6, 0.9, 0.2)
            Ellipse(pos=(self.x - 5, self.y - 5), size=(self.width + 10, self.height + 10))
            
            # Ball shadow
            Color(0, 0, 0, 0.4)
            Ellipse(pos=(self.x + 4, self.y - 4), size=self.size)
            
            # Main ball
            Color(*self.ball_color)
            Ellipse(pos=self.pos, size=self.size)
            
            # Inner highlight
            Color(1, 1, 1, 0.4)
            Ellipse(pos=(self.x + 12, self.y + 25), size=(30, 18))
            
            # Center play icon
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
        
        # Padding
        self.padding = [10, 10, 10, 10]
        self.spacing = 8
        
        # Background
        with self.canvas.before:
            Color(0.12, 0.12, 0.12, 0.95)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])
        
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        # Build menu
        self._build_menu()
    
    def update_bg(self, *args):
        """Update background"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def _build_menu(self):
        """Build menu buttons"""
        # Title
        title = Label(
            text="[b]WangZhe Clicker[/b]\n[size=11]v3.4.0[/size]",
            markup=True,
            size_hint_y=None,
            height=50,
            color=(0.95, 0.95, 0.95, 1),
            halign='center'
        )
        title.bind(texture_size=title.setter('size'))
        self.add_widget(title)
        
        # Status label
        self.status_label = Label(
            text="[color=00ff00]● Ready[/color]",
            markup=True,
            size_hint_y=None,
            height=30,
            font_size=12,
            color=(0.8, 0.8, 0.8, 1)
        )
        self.add_widget(self.status_label)
        
        # Buttons
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
        """Start flow"""
        print("[MENU] Start pressed")
        if self.app_instance:
            self.app_instance.start_flow()
            self.status_label.text = "[color=00ff00]● Running[/color]"
    
    def _on_stop(self, instance):
        """Stop flow"""
        print("[MENU] Stop pressed")
        if self.app_instance:
            self.app_instance.stop_flow()
            self.status_label.text = "[color=ffff00]● Stopped[/color]"
    
    def _on_test(self, instance):
        """Test click"""
        print("[MENU] Test pressed")
        if self.app_instance:
            self.app_instance.test_click()
    
    def _on_exit(self, instance):
        """Exit app"""
        print("[MENU] Exit pressed")
        if self.app_instance:
            self.app_instance.exit_app()
    
    def show(self, pos):
        """Show menu with animation"""
        self.pos = pos
        anim = Animation(opacity=1, duration=0.2, t='out_quad')
        anim.start(self)
    
    def hide(self):
        """Hide menu"""
        anim = Animation(opacity=0, duration=0.15, t='in_quad')
        anim.bind(on_complete=lambda *args: setattr(self, 'pos', (-1000, -1000)))
        anim.start(self)


class SimpleClicker:
    """Simple clicker for floating ball app"""
    
    def __init__(self):
        self.screen_width = 1280
        self.screen_height = 720
        self.has_root = False
        self.is_initialized = False
        self.is_running = False
        
        # Initialize Android API
        Clock.schedule_once(self._init_android, 0.5)
    
    def _init_android(self, dt):
        """Initialize Android API"""
        global ANDROID_API_AVAILABLE, mActivity
        
        try:
            if PYJNIUS_AVAILABLE:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                mActivity = PythonActivity.mActivity
                
                # Get screen size
                display = mActivity.getWindowManager().getDefaultDisplay()
                Point = autoclass('android.graphics.Point')()
                display.getSize(Point)
                self.screen_width = Point.x
                self.screen_height = Point.y
                
                # Check ROOT
                self._check_root()
                
                ANDROID_API_AVAILABLE = True
                self.is_initialized = True
                print(f"Android initialized: {self.screen_width}x{self.screen_height}")
        
        except Exception as e:
            print(f"Android init failed: {e}")
    
    def _check_root(self):
        """Check ROOT access"""
        try:
            from jnius import autoclass
            Runtime = autoclass('java.lang.Runtime')
            runtime = Runtime.getRuntime()
            process = runtime.exec("which su")
            process.waitFor()
            self.has_root = (process.exitValue() == 0)
            print(f"ROOT: {self.has_root}")
        except:
            self.has_root = False
    
    def click(self, x, y):
        """Click at position"""
        try:
            from jnius import autoclass
            Runtime = autoclass('java.lang.Runtime')
            TimeUnit = autoclass('java.util.concurrent.TimeUnit')
            runtime = Runtime.getRuntime()
            
            # Method 1: input tap
            cmd = f"input tap {x} {y}"
            process = runtime.exec(cmd)
            process.waitFor(1, TimeUnit.SECONDS)
            
            if process.exitValue() == 0:
                print(f"[CLICK] Success: ({x}, {y})")
                return True
            
            # Method 2: ROOT
            if self.has_root:
                cmd = f"su -c input tap {x} {y}"
                process = runtime.exec(cmd)
                process.waitFor(1, TimeUnit.SECONDS)
                if process.exitValue() == 0:
                    print(f"[CLICK] ROOT success: ({x}, {y})")
                    return True
            
            print(f"[CLICK] Failed: ({x}, {y})")
            return False
        
        except Exception as e:
            print(f"[CLICK] Error: {e}")
            return False


class FloatingBallApp(App):
    """Main application with floating ball UI"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clicker = SimpleClicker()
        self.is_running = False
        self.floating_ball = None
        self.floating_menu = None
    
    def build(self):
        """Build the app"""
        # Set window size for floating window
        Window.size = (350, 400)
        Window.left = 50
        Window.top = 50
        
        # Try to make window always on top
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
                # Check if click is outside menu
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
        """Toggle menu visibility"""
        if self.floating_menu.opacity == 0:
            self._expand_menu()
        else:
            self._collapse_menu()
    
    def _expand_menu(self):
        """Expand menu"""
        ball = self.floating_ball
        menu = self.floating_menu
        
        # Position menu to the right of ball
        menu_x = ball.x + ball.width + 15
        menu_y = ball.center_y - menu.height / 2
        
        # Keep within window bounds
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
        """Start auto click flow"""
        print("[APP] Starting flow...")
        self.is_running = True
        self.floating_ball.ball_color = [0.2, 0.9, 0.3, 0.95]
        
        # Start clicker thread
        def run_flow():
            while self.is_running:
                # Test click
                self.clicker.click(640, 360)
                time.sleep(2)
        
        thread = threading.Thread(target=run_flow, daemon=True)
        thread.start()
    
    def stop_flow(self):
        """Stop auto click flow"""
        print("[APP] Stopping flow...")
        self.is_running = False
        self.floating_ball.ball_color = [0.2, 0.6, 0.9, 0.95]
    
    def test_click(self):
        """Test click"""
        print("[APP] Test click")
        self.clicker.click(640, 360)
    
    def exit_app(self):
        """Exit app"""
        print("[APP] Exiting...")
        self.stop_flow()
        App.get_running_app().stop()


if __name__ == '__main__':
    FloatingBallApp().run()
