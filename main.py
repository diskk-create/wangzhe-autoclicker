#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
王者荣耀自动点击器 - 最简测试版
只显示UI，测试能否启动
"""

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

class TestApp(App):
    """最简单的测试应用"""

    title = "测试应用"

    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # 标题
        label = Label(
            text="如果你看到这个\n说明应用启动成功！",
            font_size='24sp',
            size_hint_y=None,
            height=200
        )
        layout.add_widget(label)

        # 测试按钮
        btn = Button(
            text="测试按钮",
            size_hint_y=None,
            height=100
        )
        btn.bind(on_press=self._on_button_press)
        layout.add_widget(btn)

        return layout

    def _on_button_press(self, instance):
        instance.text = "按钮被点击了！"


if __name__ == '__main__':
    TestApp().run()
