#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试菜单显示
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QMenu, QLabel, QVBoxLayout, QWidget
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QTimer

class TestMenuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("测试菜单")
        self.resize(400, 300)
        
        # 创建中央控件
        central = QWidget()
        layout = QVBoxLayout(central)
        self.label = QLabel("检查File菜单中的Settings选项\n如果找不到，点击菜单栏的任意位置")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.setCentralWidget(central)
        
        # 创建菜单栏
        menubar = self.menuBar()
        
        # 创建File菜单
        menu_file = QMenu("File")
        menubar.addMenu(menu_file)
        
        # 添加菜单项
        action_import = QAction("Import...", self)
        action_export = QAction("Export...", self)
        action_plot = QAction("Plot...", self)
        
        menu_file.addAction(action_import)
        menu_file.addAction(action_export)
        menu_file.addAction(action_plot)
        
        # 添加分隔符
        menu_file.addSeparator()
        
        # 添加Settings菜单项
        self.action_settings = QAction("Settings...", self)
        self.action_settings.setShortcut("Ctrl+.")
        menu_file.addAction(self.action_settings)
        self.action_settings.triggered.connect(self.on_settings_clicked)
        
        # 创建计时器，每1秒更新菜单项文本
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_settings_text)
        self.timer.start(1000)
        self.counter = 0
        
    def on_settings_clicked(self):
        self.label.setText("Settings菜单项被点击了！")
        
    def update_settings_text(self):
        self.counter += 1
        if self.counter % 2 == 0:
            self.action_settings.setText("设置...")
        else:
            self.action_settings.setText("Settings...")
        
        # 强制更新菜单
        self.menuBar().update()
        
def main():
    app = QApplication(sys.argv)
    window = TestMenuWindow()
    window.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main() 