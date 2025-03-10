#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
极简菜单测试 - 只有一个File菜单和一个Settings菜单项
强制菜单栏显示在窗口内部
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QLabel, QVBoxLayout, QWidget, QMenuBar
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

class SimpleMenuTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Menu Test")
        self.resize(600, 400)
        
        # 强制menuBar显示在窗口内部而不是屏幕顶部 (macOS特性)
        self.setUnifiedTitleAndToolBarOnMac(False)
        
        # 创建中央控件
        central = QWidget()
        layout = QVBoxLayout(central)
        
        # 添加说明标签
        self.label = QLabel("请查看窗口顶部的File菜单 - 应该有一个Settings选项\n如果看不到菜单，请尝试点击窗口顶部区域")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        # 添加状态标签
        self.status_label = QLabel("菜单状态: 未初始化")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.setCentralWidget(central)
        
        # 创建简单菜单 - 只有File和一个Settings选项
        self.create_simple_menu()
        
        # 输出菜单栏状态
        self.print_menubar_status()
        
    def create_simple_menu(self):
        """创建一个简单的File菜单，里面只有一个Settings选项"""
        # 获取菜单栏
        menubar = self.menuBar()
        
        # 确保menuBar存在
        if menubar is None:
            print("错误: menuBar为空，创建新的menuBar")
            menubar = QMenuBar(self)
            self.setMenuBar(menubar)
        
        # 先清除所有已有菜单
        menubar.clear()
        
        # 创建File菜单
        file_menu = QMenu("File", self)
        menubar.addMenu(file_menu)
        
        # 创建Settings菜单项
        settings_action = QAction("Settings", self)
        settings_action.setShortcut("Ctrl+S")
        settings_action.triggered.connect(self.on_settings_clicked)
        file_menu.addAction(settings_action)
        
        # 更新状态
        self.status_label.setText(f"菜单状态: 已创建File菜单和Settings菜单项")
        print("创建了简单菜单：File > Settings")
        
    def print_menubar_status(self):
        """输出菜单栏状态信息"""
        menubar = self.menuBar()
        print(f"菜单栏存在: {menubar is not None}")
        
        if menubar:
            print(f"菜单栏可见性: {menubar.isVisible()}")
            print(f"菜单栏包含的菜单数量: {len(menubar.actions())}")
            
            for i, action in enumerate(menubar.actions()):
                print(f"菜单 {i+1}: {action.text()}")
                menu = action.menu()
                if menu:
                    print(f"  子菜单项数量: {len(menu.actions())}")
                    for j, sub_action in enumerate(menu.actions()):
                        print(f"    项目 {j+1}: {sub_action.text()}")
        
    def on_settings_clicked(self):
        self.label.setText("Settings菜单项被点击了！")
        print("Settings菜单项被点击了！")

def main():
    app = QApplication(sys.argv)
    window = SimpleMenuTest()
    window.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main() 