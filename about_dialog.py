import sys
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, 
    QHBoxLayout, QWidget, QTextBrowser
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.resize(500, 400)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 添加标题
        title_label = QLabel("Aleksameter App")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 添加版本信息
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # 添加描述
        description = QTextBrowser()
        description.setOpenExternalLinks(True)
        description.setHtml("""
        <p style='text-align: center;'>
        This application calculates color coordinates (CIE x,y), sRGB values (linear and gamma corrected), 
        and reflectance from spectral data.
        </p>
        <p style='text-align: center;'>
        Developed as part of a Master's thesis project to migrate from MATLAB to Python.
        </p>
        <p style='text-align: center;'>
        &copy; 2023 All rights reserved.
        </p>
        """)
        layout.addWidget(description)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        button_container = QWidget()
        button_container.setLayout(button_layout)
        layout.addWidget(button_container) 