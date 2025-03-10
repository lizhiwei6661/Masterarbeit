#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Settings对话框
"""

import sys
import os
import json
from PySide6.QtWidgets import QApplication
from settings_dialog import SettingsDialog

def get_default_settings():
    """获取合并了两个组件需要的所有设置项的默认设置"""
    return {
        'general': {
            'rho_lambda': 1.0,          # Settings对话框需要
            'gamut': 'sRGB',           # 共同需要
            'illuminant': 'D65',       # 共同需要
            'rgb_values': '0 ... 255',  # Settings对话框需要
            'language': 'English'      # MainWindow需要
        },
        'import': {
            'default_directory': os.path.expanduser('~'),
            'auto_preview': True,
            'max_preview_files': 5
        },
        'plot': {
            'reflectance_color': '#1f77b4',
            'grid': True,
            'legend': True,
            'dpi': 300,
            'reflectance_width': 800,   # Settings对话框需要
            'reflectance_height': 600,  # Settings对话框需要
            'cie_width': 600,           # Settings对话框需要
            'cie_height': 600,          # Settings对话框需要
            'reflectance_title': 'Reflectance',  # Settings对话框需要
            'cie_title': 'CIE 1931 Chromaticity Diagram',  # Settings对话框需要
            'reflectance_show_title': True,  # Settings对话框需要
            'cie_show_title': True,         # Settings对话框需要
            'reflectance_show_legend': True, # Settings对话框需要
            'cie_show_legend': True         # Settings对话框需要
        },
        'export': {
            'default_directory': os.path.expanduser('~'),
            'default_format': 'xlsx',
            'include_header': True,
            'decimal_places': 6,
            'separator': 'Comma',      # Settings对话框需要
            'copy_header': 'Yes'       # Settings对话框需要
        }
    }

def main():
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 获取默认设置
    settings = get_default_settings()
    
    # 读取设置文件（如果存在）
    settings_file = "app_settings.json"
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                loaded_settings = json.loads(f.read())
                
            # 合并设置，保留所有必要的键
            for category in loaded_settings:
                if category in settings:
                    settings[category].update(loaded_settings[category])
                    
            print(f"从 {settings_file} 加载设置并合并")
        except Exception as e:
            print(f"加载设置时出错: {str(e)}")
    
    # 创建设置对话框
    dialog = SettingsDialog(settings=settings)
    
    # 显示对话框并等待用户操作
    if dialog.exec():
        # 如果用户点击了"确定"，获取设置并保存
        new_settings = dialog.get_settings()
        print("获取到新的设置:")
        print(json.dumps(new_settings, indent=4))
        
        # 保存设置
        try:
            with open(settings_file, 'w') as f:
                f.write(json.dumps(new_settings, indent=4))
            print(f"设置已保存到 {settings_file}")
        except Exception as e:
            print(f"保存设置时出错: {str(e)}")
    else:
        print("用户取消了操作")
    
    # 退出应用程序
    sys.exit()

if __name__ == "__main__":
    main() 