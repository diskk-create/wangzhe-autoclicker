#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
支持热更新配置，无需重新打包APK
"""

import json
import os


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置"""
        # 默认配置
        default_config = {
            'buttons': {
                'login': {'x': 641, 'y': 564, 'desc': '登录'},
                'login_popup': {'x': 1190, 'y': 112, 'desc': '关闭弹窗'},
                'game_lobby': {'x': 514, 'y': 544, 'desc': '游戏大厅'},
                'match_screen': {'x': 398, 'y': 539, 'desc': '匹配'},
                'ai_mode_screen': {'x': 730, 'y': 601, 'desc': 'AI模式'},
                'start_game_screen': {'x': 1057, 'y': 569, 'desc': '开始游戏'},
                'prepare_screen': {'x': 775, 'y': 660, 'desc': '准备游戏'},
                'ready_game': {'x': 640, 'y': 561, 'desc': '准备进入'},
                'game_over': {'x': 635, 'y': 664, 'desc': '游戏结束'},
                'settlement_hero': {'x': 645, 'y': 621, 'desc': '结算英雄'},
                'return_room': {'x': 739, 'y': 651, 'desc': '返回房间'}
            },
            'settings': {
                'wait_time': 3,
                'threshold': 0.7,
                'max_loops': 100,
                'adb_path': 'adb',
                'adb_device': '127.0.0.1:21503'
            },
            'templates': {
                'login': 'template_login.png',
                'login_popup': 'template_login_popup.png',
                'game_lobby': 'template_game_lobby.png',
                'match_screen': 'template_match.png',
                'ai_mode_screen': 'template_ai_mode.png',
                'start_game_screen': 'template_start_game.png',
                'prepare_screen': 'template_prepare.png',
                'ready_game': 'template_ready_game.png',
                'game_over': 'template_game_over.png',
                'settlement_hero': 'template_settlement_hero.png',
                'return_room': 'template_return_room.png'
            }
        }
        
        # 尝试加载现有配置
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并配置
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"加载配置失败: {e}")
        
        return default_config
    
    def save_config(self, config):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.config = config
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get_button_coord(self, button_name):
        """获取按钮坐标"""
        if button_name in self.config['buttons']:
            return self.config['buttons'][button_name]
        return None
    
    def set_button_coord(self, button_name, x, y, desc=''):
        """设置按钮坐标"""
        if button_name not in self.config['buttons']:
            self.config['buttons'][button_name] = {}
        
        self.config['buttons'][button_name].update({
            'x': x,
            'y': y,
            'desc': desc
        })
        self.save_config(self.config)
    
    def get_setting(self, key):
        """获取设置"""
        return self.config['settings'].get(key)
    
    def set_setting(self, key, value):
        """设置参数"""
        self.config['settings'][key] = value
        self.save_config(self.config)
    
    def get_template(self, step_name):
        """获取模板文件"""
        return self.config['templates'].get(step_name)
    
    def export_config(self, export_file='config_export.json'):
        """导出配置"""
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出配置失败: {e}")
            return False
    
    def import_config(self, import_file='config_import.json'):
        """导入配置"""
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
                self.config.update(imported_config)
                self.save_config(self.config)
            return True
        except Exception as e:
            print(f"导入配置失败: {e}")
            return False


# 测试代码
if __name__ == '__main__':
    manager = ConfigManager()
    
    print("当前配置:")
    print(json.dumps(manager.config, ensure_ascii=False, indent=2))
    
    # 测试设置
    manager.set_button_coord('test', 100, 200, '测试按钮')
    print(f"\n测试按钮坐标: {manager.get_button_coord('test')}")
    
    # 测试设置参数
    manager.set_setting('wait_time', 5)
    print(f"等待时间: {manager.get_setting('wait_time')}")