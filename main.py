#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最简单的Kivy应用 - 确保构建成功
"""

from kivy.app import App
from kivy.uix.label import Label


class SimpleApp(App):
    """最简单的应用"""
    
    title = "王者荣耀自动点击器"
    
    def build(self):
        """构建界面"""
        return Label(text="王者荣耀自动点击器 v3.0")


if __name__ == '__main__':
    SimpleApp().run()
