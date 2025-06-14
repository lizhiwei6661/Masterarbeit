import sys
import os
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
        
        # Create main layout
        layout = QVBoxLayout(self)
        
        # 添加应用图标
        icon_label = QLabel()
        try:
            # 使用get_resource_path获取正确的图标路径
            icon_path = self.get_resource_path("app_icon.png")
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                # 缩放图标到合适大小
                scaled_pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(icon_label)
        except:
            pass
        
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
        Original Author & Supervisor: Marina Leontopoulos<br>
        Software Author: Zhiwei Li
        </p>
        <p style='text-align: center;'>
        &copy; 2025 All rights reserved.
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
    
    def get_resource_path(self, relative_path):
        """
        Get absolute path of resource file, suitable for development environment and PyInstaller packaging environment
        
        Parameters:
            relative_path: Relative path
            
        Returns:
            Absolute path
        """
        try:
            # PyInstaller creates temporary folder, stores path in _MEIPASS
            base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
            return os.path.join(base_path, relative_path)
        except Exception as e:
            print(f"Error getting resource path: {str(e)}")
            return relative_path 