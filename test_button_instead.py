#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用按钮替代菜单测试 - 不依赖菜单栏，直接使用按钮打开设置
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, 
    QWidget, QPushButton, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt

class SettingsDialog(QDialog):
    """简单的设置对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 添加一些示例设置
        label = QLabel("这是一个设置对话框。\n在实际应用中，这里会有各种设置选项。")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # 添加按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

class ButtonTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Button Instead of Menu Test")
        self.resize(600, 400)
        
        # 创建中央控件
        central = QWidget()
        layout = QVBoxLayout(central)
        
        # 添加说明标签
        self.label = QLabel("我们使用按钮代替菜单栏。\n请点击下方的Settings按钮打开设置对话框。")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 添加常用按钮
        import_button = QPushButton("Import...")
        export_button = QPushButton("Export...")
        plot_button = QPushButton("Plot...")
        settings_button = QPushButton("Settings")
        
        # 设置按钮样式，使其更明显
        settings_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #0D8FE8;
            }
        """)
        
        # 连接Settings按钮的点击事件
        settings_button.clicked.connect(self.open_settings)
        
        # 添加按钮到布局
        button_layout.addWidget(import_button)
        button_layout.addWidget(export_button)
        button_layout.addWidget(plot_button)
        button_layout.addWidget(settings_button)
        
        # 将按钮布局添加到主布局
        layout.addLayout(button_layout)
        
        # 添加状态标签
        self.status_label = QLabel("状态: 就绪")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.setCentralWidget(central)
        
        print("创建了带有Settings按钮的窗口")
        
    def open_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self)
        self.status_label.setText("状态: 打开设置对话框...")
        
        # 显示对话框
        result = dialog.exec()
        
        # 根据结果更新状态
        if result == QDialog.DialogCode.Accepted:
            self.status_label.setText("状态: 设置已保存")
            print("设置已保存")
        else:
            self.status_label.setText("状态: 设置已取消")
            print("设置已取消")

def main():
    app = QApplication(sys.argv)
    window = ButtonTest()
    window.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main() 