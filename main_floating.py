"""
WangZhe Auto Clicker - Floating Ball Version
A floating ball assistant with expandable menu
"""

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, RoundedRectangle
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import NumericProperty, BooleanProperty, ListProperty
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


class FloatingBall(Widget):
    """Floating ball widget"""
    
    ball_size = NumericProperty(60)
    is_expanded = BooleanProperty(False)
    ball_color = ListProperty([0.2, 0.6, 0.9, 0.9])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (60, 60)
        self.pos = (100, 100)
        
        # Touch tracking
        self.touch_start_pos = None
        self.is_dragging = False
        self.drag_threshold = 10
        
        # Draw ball
        self.bind(pos=self.update_ball, size=self.update_ball)
        
    def update_ball(self, *args):
        """Update ball position"""
        self.canvas.clear()
        with self.canvas:
            # Ball shadow
            Color(0, 0, 0, 0.3)
            Ellipse(pos=(self.x + 3, self.y - 3), size=self.size)
            
            # Ball
            Color(*self.ball_color)
            Ellipse(pos=self.pos, size=self.size)
            
            # Highlight
            Color(1, 1, 1, 0.3)
            Ellipse(pos=(self.x + 10, self.y + 20), size=(25, 15))


class FloatingMenu(BoxLayout):
    """Expandable menu panel"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (200, 300)
        self.opacity = 0
        self.pos = (0, 0)
        
        # Background
        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 0.95)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
        
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        # Add buttons
        self._build_menu()
    
    def update_bg(self, *args):
        """Update background position"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def _build_menu(self):
        """Build menu buttons"""
        # Title
        title = Label(
            text="[b]WangZhe Clicker[/b]",
            markup=True,
            size_hint_y=None,
            height=40,
            color=(0.9, 0.9, 0.9, 1)
        )
        self.add_widget(title)
        
        # Buttons
        buttons_data = [
            ("▶ Start", self._on_start, (0.2, 0.7, 0.3, 0.9)),
            ("⏸ Stop", self._on_stop, (0.8, 0.3, 0.3, 0.9)),
            ("🔄 Test", self._on_test, (0.3, 0.5, 0.8, 0.9)),
            ("ℹ Status", self._on_status, (0.5, 0.5, 0.5, 0.9)),
            ("✕ Exit", self._on_exit, (0.3, 0.3, 0.3, 0.9)),
        ]
        
        for text, callback, color in buttons_data:
            btn = Button(
                text=text,
                size_hint_y=None,
                height=45,
                background_color=color,
                background_normal='',
                font_size=14
            )
            btn.bind(on_press=callback)
            self.add_widget(btn)
    
    def _on_start(self, instance):
        """Start button pressed"""
        print("[MENU] Start pressed")
        if self.parent and hasattr(self.parent, 'start_flow'):
            self.parent.start_flow()
    
    def _on_stop(self, instance):
        """Stop button pressed"""
        print("[MENU] Stop pressed")
        if self.parent and hasattr(self.parent, 'stop_flow'):
            self.parent.stop_flow()
    
    def _on_test(self, instance):
        """Test button pressed"""
        print("[MENU] Test pressed")
        if self.parent and hasattr(self.parent, 'test_click'):
            self.parent.test_click()
    
    def _on_status(self, instance):
        """Status button pressed"""
        print("[MENU] Status pressed")
        if self.parent and hasattr(self.parent, 'show_status'):
            self.parent.show_status()
    
    def _on_exit(self, instance):
        """Exit button pressed"""
        print("[MENU] Exit pressed")
        if self.parent and hasattr(self.parent, 'exit_app'):
            self.parent.exit_app()
    
    def show(self, pos):
        """Show menu with animation"""
        self.pos = pos
        self.opacity = 0
        
        anim = Animation(opacity=1, duration=0.2)
        anim.start(self)
    
    def hide(self):
        """Hide menu with animation"""
        anim = Animation(opacity=0, duration=0.15)
        anim.bind(on_complete=lambda *args: setattr(self, 'pos', (-1000, -1000)))
        anim.start(self)


class FloatingBallApp(App):
    """Main app with floating ball"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_running = False
        self.clicker = None
        self.floating_ball = None
        self.floating_menu = None
        
    def build(self):
        """Build the app"""
        # Set window properties for floating window
        Window.size = (300, 300)
        Window.left = 100
        Window.top = 100
        
        # Make window always on top and transparent
        try:
            Window.always_on_top = True
        except:
            pass
        
        # Main layout
        layout = FloatLayout()
        
        # Create floating ball
        self.floating_ball = FloatingBall()
        self.floating_ball.pos = (120, 120)
        layout.add_widget(self.floating_ball)
        
        # Create menu (hidden initially)
        self.floating_menu = FloatingMenu()
        self.floating_menu.pos = (-1000, -1000)
        layout.add_widget(self.floating_menu)
        
        # Bind touch events
        layout.bind(on_touch_down=self.on_touch_down)
        layout.bind(on_touch_up=self.on_touch_up)
        layout.bind(on_touch_move=self.on_touch_move)
        
        # Initialize clicker
        Clock.schedule_once(self._init_clicker, 0.5)
        
        return layout
    
    def on_touch_down(self, instance, touch):
        """Handle touch down"""
        if self.floating_ball.collide_point(*touch.pos):
            self.floating_ball.touch_start_pos = touch.pos
            self.floating_ball.is_dragging = False
            return True
        return False
    
    def on_touch_move(self, instance, touch):
        """Handle touch move"""
        if self.floating_ball.touch_start_pos:
            # Calculate distance moved
            dx = touch.pos[0] - self.floating_ball.touch_start_pos[0]
            dy = touch.pos[1] - self.floating_ball.touch_start_pos[1]
            distance = (dx**2 + dy**2) ** 0.5
            
            if distance > self.floating_ball.drag_threshold:
                self.floating_ball.is_dragging = True
                # Move ball
                new_x = touch.pos[0] - self.floating_ball.width / 2
                new_y = touch.pos[1] - self.floating_ball.height / 2
                
                # Keep within window bounds
                new_x = max(0, min(new_x, Window.width - self.floating_ball.width))
                new_y = max(0, min(new_y, Window.height - self.floating_ball.height))
                
                self.floating_ball.pos = (new_x, new_y)
            return True
        return False
    
    def on_touch_up(self, instance, touch):
        """Handle touch up"""
        if self.floating_ball.touch_start_pos:
            if not self.floating_ball.is_dragging:
                # It's a click, not a drag
                self.toggle_menu()
            
            self.floating_ball.touch_start_pos = None
            self.floating_ball.is_dragging = False
            return True
        return False
    
    def toggle_menu(self):
        """Toggle menu visibility"""
        if self.floating_menu.opacity == 0:
            # Show menu
            menu_x = self.floating_ball.x + self.floating_ball.width + 10
            menu_y = self.floating_ball.y - self.floating_menu.height / 2 + self.floating_ball.height / 2
            
            # Keep within window bounds
            menu_x = min(menu_x, Window.width - self.floating_menu.width - 10)
            menu_y = max(10, min(menu_y, Window.height - self.floating_menu.height - 10))
            
            self.floating_menu.show((menu_x, menu_y))
            self.floating_ball.is_expanded = True
            self.floating_ball.ball_color = [0.3, 0.8, 0.3, 0.9]
        else:
            # Hide menu
            self.floating_menu.hide()
            self.floating_ball.is_expanded = False
            self.floating_ball.ball_color = [0.2, 0.6, 0.9, 0.9]
    
    def _init_clicker(self, dt):
        """Initialize clicker"""
        global ANDROID_API_AVAILABLE, mActivity
        
        try:
            if PYJNIUS_AVAILABLE:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                mActivity = PythonActivity.mActivity
                ANDROID_API_AVAILABLE = True
                print("Android API initialized")
        except Exception as e:
            print(f"Android API init failed: {e}")
    
    def start_flow(self):
        """Start auto click flow"""
        print("[APP] Starting flow...")
        self.is_running = True
        self.floating_ball.ball_color = [0.3, 0.8, 0.3, 0.9]
    
    def stop_flow(self):
        """Stop auto click flow"""
        print("[APP] Stopping flow...")
        self.is_running = False
        self.floating_ball.ball_color = [0.2, 0.6, 0.9, 0.9]
    
    def test_click(self):
        """Test click"""
        print("[APP] Test click")
        if ANDROID_API_AVAILABLE:
            try:
                from jnius import autoclass
                Runtime = autoclass('java.lang.Runtime')
                runtime = Runtime.getRuntime()
                process = runtime.exec("input tap 640 360")
                process.waitFor()
                print("[APP] Test click success")
            except Exception as e:
                print(f"[APP] Test click failed: {e}")
    
    def show_status(self):
        """Show status"""
        status = "Running" if self.is_running else "Stopped"
        api = "OK" if ANDROID_API_AVAILABLE else "N/A"
        print(f"[APP] Status: {status}, API: {api}")
    
    def exit_app(self):
        """Exit app"""
        print("[APP] Exiting...")
        App.get_running_app().stop()


if __name__ == '__main__':
    FloatingBallApp().run()
