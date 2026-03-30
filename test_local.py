#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WangZhe Auto Clicker - Local Test Script
Test core functionality without Kivy UI
"""

import subprocess
import time
import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class LocalClicker:
    """Local clicker for testing via ADB"""

    def __init__(self, device_id="127.0.0.1:21503"):
        self.device_id = device_id
        self.screen_width = 1280
        self.screen_height = 720
        self.has_root = False
        self.test_mode = True

        print("=" * 60)
        print("WangZhe Auto Clicker - Local Test Mode")
        print("=" * 60)
        print(f"Device: {device_id}")
        print()

    def adb_command(self, cmd):
        """Execute ADB command"""
        full_cmd = f"adb -s {self.device_id} {cmd}"
        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode, result.stdout, result.stderr

    def test_connection(self):
        """Test ADB connection"""
        print("[TEST] Testing ADB connection...")
        code, stdout, stderr = self.adb_command("shell echo 'Connected'")

        if code == 0 and "Connected" in stdout:
            print("[TEST] ✓ ADB connection OK")
            return True
        else:
            print(f"[TEST] ✗ ADB connection failed: {stderr}")
            return False

    def test_root(self):
        """Test ROOT access"""
        print("[TEST] Testing ROOT access...")
        code, stdout, stderr = self.adb_command("shell which su")

        if code == 0 and stdout.strip():
            print("[TEST] ✓ ROOT available")
            self.has_root = True
            return True
        else:
            print("[TEST] ✗ ROOT not available (will use normal mode)")
            self.has_root = False
            return False

    def get_screen_size(self):
        """Get screen size"""
        print("[TEST] Getting screen size...")
        code, stdout, stderr = self.adb_command("shell wm size")

        if code == 0:
            # Parse: Physical size: 1280x720
            if "x" in stdout:
                size = stdout.split(":")[-1].strip()
                w, h = size.split("x")
                self.screen_width = int(w)
                self.screen_height = int(h)
                print(f"[TEST] ✓ Screen size: {self.screen_width}x{self.screen_height}")
                return True

        print(f"[TEST] ✗ Failed to get screen size, using default: {self.screen_width}x{self.screen_height}")
        return False

    def click(self, x, y):
        """Click at position"""
        # Scale coordinates
        scale_x = x / 1280 * self.screen_width
        scale_y = y / 720 * self.screen_height

        scaled_x = int(scale_x)
        scaled_y = int(scale_y)

        print(f"[CLICK] Clicking at ({scaled_x}, {scaled_y})...")

        # Method 1: input tap
        code, stdout, stderr = self.adb_command(f"shell input tap {scaled_x} {scaled_y}")

        if code == 0:
            print(f"[CLICK] ✓ Success (input tap)")
            return True

        # Method 2: ROOT
        if self.has_root:
            code, stdout, stderr = self.adb_command(f"shell su -c input tap {scaled_x} {scaled_y}")
            if code == 0:
                print(f"[CLICK] ✓ Success (ROOT)")
                return True

        print(f"[CLICK] ✗ Failed")
        return False

    def capture_screen(self, save_path="screen.png"):
        """Capture screen"""
        print("[CAPTURE] Capturing screen...")
        code, stdout, stderr = self.adb_command(f"shell screencap -p /sdcard/{save_path}")

        if code != 0:
            print(f"[CAPTURE] ✗ Failed to capture: {stderr}")
            return False

        # Pull to local
        local_path = os.path.join(os.path.dirname(__file__), save_path)
        code, stdout, stderr = self.adb_command(f"pull /sdcard/{save_path} {local_path}")

        if code == 0:
            print(f"[CAPTURE] ✓ Screen saved to {local_path}")
            return True
        else:
            print(f"[CAPTURE] ✗ Failed to pull: {stderr}")
            return False

    def test_click_flow(self):
        """Test click flow"""
        print("\n" + "=" * 60)
        print("Testing Click Flow")
        print("=" * 60)

        test_points = [
            (640, 360, "Center"),
            (100, 100, "Top-left"),
            (1180, 620, "Bottom-right"),
        ]

        for x, y, name in test_points:
            print(f"\n[TEST] Testing {name} ({x}, {y})")
            self.click(x, y)
            time.sleep(1)

    def run_interactive(self):
        """Run interactive test mode"""
        print("\n" + "=" * 60)
        print("Interactive Test Mode")
        print("=" * 60)
        print("Commands:")
        print("  click <x> <y>  - Click at position")
        print("  capture         - Capture screen")
        print("  test            - Run test clicks")
        print("  size            - Get screen size")
        print("  quit            - Exit")
        print()

        while True:
            try:
                cmd = input(">>> ").strip().lower()

                if not cmd:
                    continue

                if cmd == "quit" or cmd == "exit":
                    print("Goodbye!")
                    break

                elif cmd == "test":
                    self.test_click_flow()

                elif cmd == "capture":
                    self.capture_screen()

                elif cmd == "size":
                    self.get_screen_size()
                    print(f"Screen: {self.screen_width}x{self.screen_height}")

                elif cmd.startswith("click "):
                    parts = cmd.split()
                    if len(parts) == 3:
                        x, y = int(parts[1]), int(parts[2])
                        self.click(x, y)
                    else:
                        print("Usage: click <x> <y>")

                else:
                    print(f"Unknown command: {cmd}")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main entry point"""
    clicker = LocalClicker()

    # Test connection
    if not clicker.test_connection():
        print("\n[ERROR] Cannot connect to device. Make sure ADB is running.")
        print("Run: adb connect 127.0.0.1:21503")
        return

    # Test ROOT
    clicker.test_root()

    # Get screen size
    clicker.get_screen_size()

    # Run interactive mode
    clicker.run_interactive()


if __name__ == "__main__":
    main()
