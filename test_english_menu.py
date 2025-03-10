#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试纯英文菜单显示
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QMenu, QLabel, QVBoxLayout, QWidget
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

class TestEnglishMenuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test English Menu")
        self.resize(400, 300)
        
        # 创建中央控件
        central = QWidget()
        layout = QVBoxLayout(central)
        self.label = QLabel("Check the File menu for Settings option\n尝试不同的创建方式，点击菜单查看显示情况")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.setCentralWidget(central)
        
        # 创建菜单栏 - 使用全新的方法
        self.create_menus()
        
    def create_menus(self):
        """创建菜单栏和菜单项，尝试不同的方法"""
        # 方法1: 手动创建全新菜单
        print("创建全新菜单...")
        
        # 清除原有菜单栏
        menubar = self.menuBar()
        menubar.clear()
        
        # 创建3种不同的File菜单进行测试
        self.create_file_menu1()  # 方法1
        self.create_file_menu2()  # 方法2
        self.create_file_menu3()  # 方法3
        
        # 添加Edit菜单 - 普通方式
        edit_menu = QMenu("Edit", self)
        menubar.addMenu(edit_menu)
        
        # 添加Help菜单 - 普通方式
        help_menu = QMenu("Help", self)
        menubar.addMenu(help_menu)
        
        print(f"菜单创建完成，总共 {len(menubar.actions())} 个顶级菜单")
        for i, action in enumerate(menubar.actions()):
            print(f"菜单 {i+1}: {action.text()}")
        
    def create_file_menu1(self):
        """方法1：创建标准File菜单"""
        menubar = self.menuBar()
        
        # 创建File菜单
        file_menu = QMenu("File", self)
        menubar.addMenu(file_menu)
        
        # 添加菜单项
        action_import = QAction("Import...", self)
        action_export = QAction("Export...", self)
        action_plot = QAction("Plot...", self)
        
        file_menu.addAction(action_import)
        file_menu.addAction(action_export)
        file_menu.addAction(action_plot)
        
        # 添加分隔符
        file_menu.addSeparator()
        
        # 添加Settings菜单项
        settings_action = QAction("Settings...", self)
        settings_action.setShortcut("Ctrl+,")
        file_menu.addAction(settings_action)
        settings_action.triggered.connect(lambda: self.on_settings_clicked("方法1"))
        
        print("方法1: 创建了标准File菜单和Settings菜单项")
        
    def create_file_menu2(self):
        """方法2：创建带有Unicode字符的File菜单"""
        menubar = self.menuBar()
        
        # 创建File(2)菜单
        file_menu = QMenu("File(2)", self)
        menubar.addMenu(file_menu)
        
        # 添加菜单项
        action_import = QAction("Import...", self)
        action_export = QAction("Export...", self)
        
        file_menu.addAction(action_import)
        file_menu.addAction(action_export)
        file_menu.addSeparator()
        
        # 添加Settings菜单项 - 使用不同的文本形式
        settings_action = QAction("Settings\u2026", self)  # Unicode省略号
        settings_action.setShortcut("Ctrl+.")
        file_menu.addAction(settings_action)
        settings_action.triggered.connect(lambda: self.on_settings_clicked("方法2"))
        
        print("方法2: 创建了带Unicode字符的File菜单和Settings菜单项")
        
    def create_file_menu3(self):
        """方法3：创建特殊File菜单"""
        menubar = self.menuBar()
        
        # 创建File(3)菜单
        file_menu = QMenu("File(3)", self)
        menubar.addMenu(file_menu)
        
        # 添加菜单项
        action_import = QAction("Import", self)
        file_menu.addAction(action_import)
        
        # 特殊处理：先添加Separator再添加Settings
        file_menu.addSeparator()
        
        # 添加Settings菜单项 - 不带省略号
        settings_action = QAction("Settings", self)
        settings_action.setObjectName("actionSettings3")
        settings_action.setShortcut("Ctrl+S")
        file_menu.addAction(settings_action)
        settings_action.triggered.connect(lambda: self.on_settings_clicked("方法3"))
        
        print("方法3: 创建了特殊File菜单和Settings菜单项(不带省略号)")
        
    def on_settings_clicked(self, method):
        self.label.setText(f"Settings菜单项被点击了！\n使用的是{method}创建的")
        print(f"Settings菜单项被点击了！使用的是{method}创建的")

def main():
    app = QApplication(sys.argv)
    window = TestEnglishMenuWindow()
    window.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main() 