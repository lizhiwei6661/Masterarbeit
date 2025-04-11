#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Settings对话框title文本框的宽度
"""

import sys
from PySide6.QtWidgets import QApplication, QDialog
from ui_Settings import Ui_Dialog_settings

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog_settings()
        self.ui.setupUi(self)
        
        # 设置标题文本以测试文本框宽度
        self.ui.lineEdit_Plot_Reflectance_Title.setText("Reflectance Spectrum")
        self.ui.lineEdit_Plot_CIExy_Title.setText("CIE 1931 Chromaticity")
        
        # 默认显示Plot标签页
        self.ui.tabWidget_Settings.setCurrentIndex(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.show()
    sys.exit(app.exec()) 