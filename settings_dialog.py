import sys
import os
import json
from PySide6.QtWidgets import (
    QDialog, QTabWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QCheckBox, QLineEdit, 
    QPushButton, QFileDialog, QGroupBox, QFormLayout,
    QDialogButtonBox, QMessageBox, QWidget, QColorDialog
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QColor
from PySide6 import QtWidgets, QtCore
from ui_Settings import Ui_Dialog_settings  # 导入新生成的UI类


class SettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        
        # 使用生成的UI类
        self.ui = Ui_Dialog_settings()
        self.ui.setupUi(self)
        
        # 设置窗口标题
        self.setWindowTitle("Settings")
        
        # 如果提供了设置，使用它们
        self.settings = settings if settings else self.get_default_settings()
        
        # 连接按钮信号
        self.ui.buttonBox_Settings.accepted.connect(self.accept)
        self.ui.buttonBox_Settings.rejected.connect(self.reject)
        self.ui.pushButton_Restore_Default.clicked.connect(self.restore_defaults)
        
        # 添加颜色选择功能 - 由于UI文件中没有颜色按钮，我们需要手动添加或处理
        
        # 初始化UI
        self.load_settings_to_ui()
        
    def load_settings_to_ui(self):
        """将设置加载到UI控件"""
        # General页
        self.ui.lineEdit_Gen_pho.setText(str(self.settings['general']['rho_lambda']))
        
        # 设置标准色域下拉框
        gamut_index = self.ui.comboBox_Gen_Gamut.findText(self.settings['general']['gamut'])
        if gamut_index >= 0:
            self.ui.comboBox_Gen_Gamut.setCurrentIndex(gamut_index)
        
        # 设置标准光源下拉框
        illum_index = self.ui.comboBox_Gen_illuminant.findText(self.settings['general']['illuminant'])
        if illum_index >= 0:
            self.ui.comboBox_Gen_illuminant.setCurrentIndex(illum_index)
        
        # 设置RGB值格式
        rgb_index = self.ui.comboBox_Gen_RGB.findText(self.settings['general']['rgb_values'])
        if rgb_index >= 0:
            self.ui.comboBox_Gen_RGB.setCurrentIndex(rgb_index)
        
        # Plot页
        if 'plot' in self.settings:
            # 分辨率
            if self.ui.comboBox_Plot_Resolution.count() == 0:
                for dpi in ["72", "150", "300", "600"]:
                    self.ui.comboBox_Plot_Resolution.addItem(dpi)
            
            res_index = self.ui.comboBox_Plot_Resolution.findText(str(self.settings['plot']['dpi']))
            if res_index >= 0:
                self.ui.comboBox_Plot_Resolution.setCurrentIndex(res_index)
            
            # 设置Plot宽度和高度
            self.ui.lineEdit_Plot_Reflectance_Width.setText(str(self.settings['plot']['reflectance_width']))
            self.ui.lineEdit_Plot_Reflectance_Height.setText(str(self.settings['plot']['reflectance_height']))
            self.ui.lineEdit_Plot_CIExy_Width.setText(str(self.settings['plot']['cie_width']))
            self.ui.lineEdit_Plot_CIExy_Height.setText(str(self.settings['plot']['cie_height']))
            
            # 设置Plot标题
            self.ui.lineEdit_Plot_Reflectance_Title.setText(self.settings['plot']['reflectance_title'])
            self.ui.lineEdit_Plot_CIExy_Title.setText(self.settings['plot']['cie_title'])
        
        # Export页
        if 'export' in self.settings:
            # 设置分隔符
            sep_index = self.ui.comboBox_Export_Separator.findText(self.settings['export']['separator'])
            if sep_index >= 0:
                self.ui.comboBox_Export_Separator.setCurrentIndex(sep_index)
            
            # 设置是否拷贝标题
            header_index = self.ui.comboBox_Copy_Header.findText(self.settings['export']['copy_header'])
            if header_index >= 0:
                self.ui.comboBox_Copy_Header.setCurrentIndex(header_index)
                
    def get_settings(self):
        """获取UI上的设置"""
        return {
            'general': {
                'rho_lambda': float(self.ui.lineEdit_Gen_pho.text() or "1.0"),
                'gamut': self.ui.comboBox_Gen_Gamut.currentText(),
                'illuminant': self.ui.comboBox_Gen_illuminant.currentText(),
                'rgb_values': self.ui.comboBox_Gen_RGB.currentText()
            },
            'plot': {
                'dpi': int(self.ui.comboBox_Plot_Resolution.currentText()),
                'reflectance_width': int(self.ui.lineEdit_Plot_Reflectance_Width.text() or "800"),
                'reflectance_height': int(self.ui.lineEdit_Plot_Reflectance_Height.text() or "600"),
                'cie_width': int(self.ui.lineEdit_Plot_CIExy_Width.text() or "600"),
                'cie_height': int(self.ui.lineEdit_Plot_CIExy_Height.text() or "600"),
                'reflectance_title': self.ui.lineEdit_Plot_Reflectance_Title.text(),
                'cie_title': self.ui.lineEdit_Plot_CIExy_Title.text(),
                'reflectance_show_title': True,  # 固定值
                'cie_show_title': True,  # 固定值
                'reflectance_show_legend': True,  # 固定值
                'cie_show_legend': True,  # 固定值
                'reflectance_color': '#1f77b4'  # 默认蓝色
            },
            'export': {
                'separator': self.ui.comboBox_Export_Separator.currentText(),
                'copy_header': self.ui.comboBox_Copy_Header.currentText(),
                'default_directory': os.path.expanduser('~'),  # 默认值
                'default_format': 'xlsx',  # 默认值
                'include_header': True,  # 默认值
                'decimal_places': 6  # 默认值
            }
        }
        
    def get_default_settings(self):
        """获取默认设置"""
        return {
            'general': {
                'rho_lambda': 0.989,  # 默认值为0.989，与MATLAB一致
                'gamut': 'sRGB',
                'illuminant': 'D65',
                'rgb_values': '0 ... 255'
            },
            'plot': {
                'dpi': 300,
                'reflectance_width': 800,
                'reflectance_height': 600,
                'cie_width': 600,
                'cie_height': 600,
                'reflectance_title': 'Reflectance',
                'cie_title': 'CIE 1931 Chromaticity Diagram',
                'reflectance_show_title': True,
                'cie_show_title': True,
                'reflectance_show_legend': True,
                'cie_show_legend': True,
                'reflectance_color': '#1f77b4'  # 默认蓝色
            },
            'export': {
                'separator': 'Comma',
                'copy_header': 'Yes',
                'default_directory': os.path.expanduser('~'),
                'default_format': 'xlsx',
                'include_header': True,
                'decimal_places': 6
            }
        }
        
    def restore_defaults(self):
        """恢复默认设置"""
        self.settings = self.get_default_settings()
        self.load_settings_to_ui()
        
    def accept(self):
        """点击确定按钮时的处理"""
        # 验证rho_lambda输入是否为有效的浮点数
        try:
            rho_lambda = float(self.ui.lineEdit_Gen_pho.text())
            if rho_lambda <= 0:
                raise ValueError("rho_lambda必须是正数")
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的rho_lambda值（正浮点数）")
            self.ui.lineEdit_Gen_pho.setFocus()
            return
            
        self.settings = self.get_settings()
        super().accept()
    
    def choose_reflectance_color(self):
        """选择反射率图表的颜色"""
        current_color = QColor(self.settings['plot']['reflectance_color'])
        color = QColorDialog.getColor(current_color, self, "Choose Reflectance Color")
        if color.isValid():
            self.settings['plot']['reflectance_color'] = color.name()
            # 由于UI中没有颜色按钮，我们只更新内部设置 