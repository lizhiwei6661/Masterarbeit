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
        
        # 设置窗口自动缩放
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
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
            # 设置DPI - 分别设置reflectance和cie的DPI
            reflectance_dpi = self.settings['plot'].get('reflectance_dpi', 300)
            cie_dpi = self.settings['plot'].get('cie_dpi', 300)
            
            # 设置Reflectance DPI
            if reflectance_dpi == 150:
                self.ui.comboBox_Plot_Reflectance_DPI.setCurrentIndex(0)
            elif reflectance_dpi == 600:
                self.ui.comboBox_Plot_Reflectance_DPI.setCurrentIndex(2)
            else:  # 默认300
                self.ui.comboBox_Plot_Reflectance_DPI.setCurrentIndex(1)
            
            # 设置CIE DPI
            if cie_dpi == 150:
                self.ui.comboBox_Plot_CIExy_DPI.setCurrentIndex(0)
            elif cie_dpi == 600:
                self.ui.comboBox_Plot_CIExy_DPI.setCurrentIndex(2)
            else:  # 默认300
                self.ui.comboBox_Plot_CIExy_DPI.setCurrentIndex(1)
                
            # 设置Plot宽度和高度
            self.ui.lineEdit_Plot_Reflectance_Width.setText(str(self.settings['plot']['reflectance_width']))
            self.ui.lineEdit_Plot_Reflectance_Height.setText(str(self.settings['plot']['reflectance_height']))
            self.ui.lineEdit_Plot_CIExy_Width.setText(str(self.settings['plot']['cie_width']))
            self.ui.lineEdit_Plot_CIExy_Height.setText(str(self.settings['plot']['cie_height']))
            
            # 设置Plot标题
            self.ui.lineEdit_Plot_Reflectance_Title.setText(self.settings['plot']['reflectance_title'])
            self.ui.lineEdit_Plot_CIExy_Title.setText(self.settings['plot']['cie_title'])
            
            # 设置是否显示标题和图例
            self.ui.comboBox_Plot_Reflectance_Insert_Title.setCurrentIndex(1 if self.settings['plot']['reflectance_show_title'] else 0)
            self.ui.comboBox_Plot_CIExy_Insert_Title.setCurrentIndex(1 if self.settings['plot']['cie_show_title'] else 0)
            self.ui.comboBox_Plot_Reflectance_Insert_Legend.setCurrentIndex(0 if self.settings['plot']['reflectance_show_legend'] else 1)
            self.ui.comboBox_Plot_CIExy_Insert_Legend.setCurrentIndex(0 if self.settings['plot']['cie_show_legend'] else 1)
            
            # 设置字体大小
            # 获取反射率图表字体大小设置
            font_size = self.settings['plot'].get('reflectance_font_size', 'Medium')
            if font_size == 'Small':
                self.ui.comboBox_Plot_Reflectance_Font_Size.setCurrentIndex(0)
            elif font_size == 'Large':
                self.ui.comboBox_Plot_Reflectance_Font_Size.setCurrentIndex(2)
            else:  # Medium为默认值
                self.ui.comboBox_Plot_Reflectance_Font_Size.setCurrentIndex(1)
                
            # 获取CIE图表字体大小设置
            font_size = self.settings['plot'].get('cie_font_size', 'Medium')
            if font_size == 'Small':
                self.ui.comboBox_Plot_CIExy_Font_Size.setCurrentIndex(0)
            elif font_size == 'Large':
                self.ui.comboBox_Plot_CIExy_Font_Size.setCurrentIndex(2)
            else:  # Medium为默认值
                self.ui.comboBox_Plot_CIExy_Font_Size.setCurrentIndex(1)
        
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
        # 获取反射率图表字体大小
        reflectance_font_size_index = self.ui.comboBox_Plot_Reflectance_Font_Size.currentIndex()
        if reflectance_font_size_index == 0:
            reflectance_font_size = 'Small'
        elif reflectance_font_size_index == 2:
            reflectance_font_size = 'Large'
        else:
            reflectance_font_size = 'Medium'
            
        # 获取CIE图表字体大小
        cie_font_size_index = self.ui.comboBox_Plot_CIExy_Font_Size.currentIndex()
        if cie_font_size_index == 0:
            cie_font_size = 'Small'
        elif cie_font_size_index == 2:
            cie_font_size = 'Large'
        else:
            cie_font_size = 'Medium'
            
        # 获取Reflectance DPI设置
        reflectance_dpi_index = self.ui.comboBox_Plot_Reflectance_DPI.currentIndex()
        if reflectance_dpi_index == 0:
            reflectance_dpi = 150
        elif reflectance_dpi_index == 2:
            reflectance_dpi = 600
        else:
            reflectance_dpi = 300
            
        # 获取CIE DPI设置
        cie_dpi_index = self.ui.comboBox_Plot_CIExy_DPI.currentIndex()
        if cie_dpi_index == 0:
            cie_dpi = 150
        elif cie_dpi_index == 2:
            cie_dpi = 600
        else:
            cie_dpi = 300
            
        # 创建一个新的设置字典，保留原始设置中不在UI中显示的部分
        new_settings = {}
        
        # 复制当前所有设置
        if hasattr(self, 'settings') and self.settings:
            for category in self.settings:
                new_settings[category] = self.settings[category].copy() if isinstance(self.settings[category], dict) else self.settings[category]
        
        # 更新UI控件中的设置，覆盖相应的值
        if 'general' not in new_settings:
            new_settings['general'] = {}
        
        # 更新general设置
        new_settings['general'].update({
                'rho_lambda': float(self.ui.lineEdit_Gen_pho.text() or "1.0"),
                'gamut': self.ui.comboBox_Gen_Gamut.currentText(),
                'illuminant': self.ui.comboBox_Gen_illuminant.currentText(),
                'rgb_values': self.ui.comboBox_Gen_RGB.currentText()
        })
        
        # 更新plot设置
        if 'plot' not in new_settings:
            new_settings['plot'] = {}
            
        new_settings['plot'].update({
            'reflectance_dpi': reflectance_dpi,  # 使用单独的reflectance_dpi
            'cie_dpi': cie_dpi,  # 使用单独的cie_dpi
                'reflectance_width': int(self.ui.lineEdit_Plot_Reflectance_Width.text() or "800"),
                'reflectance_height': int(self.ui.lineEdit_Plot_Reflectance_Height.text() or "600"),
                'cie_width': int(self.ui.lineEdit_Plot_CIExy_Width.text() or "600"),
                'cie_height': int(self.ui.lineEdit_Plot_CIExy_Height.text() or "600"),
                'reflectance_title': self.ui.lineEdit_Plot_Reflectance_Title.text(),
                'cie_title': self.ui.lineEdit_Plot_CIExy_Title.text(),
                'reflectance_show_title': self.ui.comboBox_Plot_Reflectance_Insert_Title.currentIndex() == 1,
                'cie_show_title': self.ui.comboBox_Plot_CIExy_Insert_Title.currentIndex() == 1,
                'reflectance_show_legend': self.ui.comboBox_Plot_Reflectance_Insert_Legend.currentIndex() == 0,
                'cie_show_legend': self.ui.comboBox_Plot_CIExy_Insert_Legend.currentIndex() == 0,
                'reflectance_font_size': reflectance_font_size,
                'cie_font_size': cie_font_size
        })
        
        # 如果plot设置中已有reflectance_color，保留它，否则设为默认值
        if 'reflectance_color' not in new_settings['plot']:
            new_settings['plot']['reflectance_color'] = '#1f77b4'  # 默认蓝色
        
        # 更新export设置
        if 'export' not in new_settings:
            new_settings['export'] = {}
            
        # 保留原有的目录和格式设置
        export_defaults = {
            'default_directory': os.path.expanduser('~'),
            'default_format': 'xlsx',
            'include_header': True,
            'decimal_places': 6
        }
        
        # 应用默认值（如果没有已存在的值）
        for key, value in export_defaults.items():
            if key not in new_settings['export']:
                new_settings['export'][key] = value
        
        # 更新UI中设置的值
        new_settings['export'].update({
            'separator': self.ui.comboBox_Export_Separator.currentText(),
            'copy_header': self.ui.comboBox_Copy_Header.currentText()
        })
                
        return new_settings
        
    def get_default_settings(self):
        """获取默认设置"""
        return {
            'general': {
                'rho_lambda': 0.989,  # 默认值为0.989，与MATLAB一致
                'gamut': 'None',  # 改为None
                'illuminant': 'D65',
                'rgb_values': '0 ... 1'  # 改为0 ... 1
            },
            'plot': {
                'reflectance_dpi': 300,  # 反射率图表DPI
                'cie_dpi': 300,  # CIE图表DPI
                'reflectance_width': 1600,  # 设置宽度为1600
                'reflectance_height': 800,  # 保持高度为800
                'cie_width': 900,  # 增加宽度从600到900
                'cie_height': 900,  # 增加高度从600到900
                'reflectance_title': 'Reflectance Spectra of Measured Samples',  # 更新默认标题
                'cie_title': 'CIE Chromaticity Diagram',  # 更新默认标题
                'reflectance_show_title': True,
                'cie_show_title': True,
                'reflectance_show_legend': True,
                'cie_show_legend': True,
                'reflectance_color': '#1f77b4',  # 默认蓝色
                'reflectance_font_size': 'Medium',  # 默认中等字体大小
                'cie_font_size': 'Medium'  # 默认中等字体大小
            },
            'export': {
                'separator': 'Point',  # 改为Point
                'copy_header': 'Yes',
                'default_directory': os.path.expanduser('~'),
                'default_format': 'xlsx',
                'include_header': True,
                'decimal_places': 6
            }
        }
        
    def restore_defaults(self):
        """恢复当前标签页的默认设置"""
        # 获取当前选中的标签页索引
        current_tab_index = self.ui.tabWidget_Settings.currentIndex()
        
        # 获取默认设置
        default_settings = self.get_default_settings()
        
        # 根据当前标签页索引恢复对应的默认设置
        if current_tab_index == 0:  # General标签页
            # 只更新general类别，保留其他类别的设置
            if 'general' not in self.settings:
                self.settings['general'] = {}
                
            # 更新general设置为默认值
            self.settings['general'].update(default_settings['general'])
            
            # 更新UI中的General设置
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
                
            print("Default settings for General tab restored")
            
        elif current_tab_index == 1:  # Plot标签页
            # 只更新plot类别，保留其他类别的设置
            if 'plot' not in self.settings:
                self.settings['plot'] = {}
                
            # 更新plot设置为默认值
            self.settings['plot'].update(default_settings['plot'])
            
            # 更新UI中的Plot设置
            # 设置Reflectance DPI
            reflectance_dpi = self.settings['plot'].get('reflectance_dpi', 300)
            if reflectance_dpi == 150:
                self.ui.comboBox_Plot_Reflectance_DPI.setCurrentIndex(0)
            elif reflectance_dpi == 600:
                self.ui.comboBox_Plot_Reflectance_DPI.setCurrentIndex(2)
            else:  # 默认300
                self.ui.comboBox_Plot_Reflectance_DPI.setCurrentIndex(1)
                
            # 设置CIE DPI
            cie_dpi = self.settings['plot'].get('cie_dpi', 300)
            if cie_dpi == 150:
                self.ui.comboBox_Plot_CIExy_DPI.setCurrentIndex(0)
            elif cie_dpi == 600:
                self.ui.comboBox_Plot_CIExy_DPI.setCurrentIndex(2)
            else:  # 默认300
                self.ui.comboBox_Plot_CIExy_DPI.setCurrentIndex(1)
            
            self.ui.lineEdit_Plot_Reflectance_Width.setText(str(self.settings['plot']['reflectance_width']))
            self.ui.lineEdit_Plot_Reflectance_Height.setText(str(self.settings['plot']['reflectance_height']))
            self.ui.lineEdit_Plot_CIExy_Width.setText(str(self.settings['plot']['cie_width']))
            self.ui.lineEdit_Plot_CIExy_Height.setText(str(self.settings['plot']['cie_height']))
            
            # 设置Plot标题
            self.ui.lineEdit_Plot_Reflectance_Title.setText(self.settings['plot']['reflectance_title'])
            self.ui.lineEdit_Plot_CIExy_Title.setText(self.settings['plot']['cie_title'])
            
            # 设置是否显示标题和图例
            self.ui.comboBox_Plot_Reflectance_Insert_Title.setCurrentIndex(1 if self.settings['plot']['reflectance_show_title'] else 0)
            self.ui.comboBox_Plot_CIExy_Insert_Title.setCurrentIndex(1 if self.settings['plot']['cie_show_title'] else 0)
            self.ui.comboBox_Plot_Reflectance_Insert_Legend.setCurrentIndex(0 if self.settings['plot']['reflectance_show_legend'] else 1)
            self.ui.comboBox_Plot_CIExy_Insert_Legend.setCurrentIndex(0 if self.settings['plot']['cie_show_legend'] else 1)
            
            # 设置字体大小
            # 获取反射率图表字体大小设置
            font_size = self.settings['plot'].get('reflectance_font_size', 'Medium')
            if font_size == 'Small':
                self.ui.comboBox_Plot_Reflectance_Font_Size.setCurrentIndex(0)
            elif font_size == 'Large':
                self.ui.comboBox_Plot_Reflectance_Font_Size.setCurrentIndex(2)
            else:  # Medium为默认值
                self.ui.comboBox_Plot_Reflectance_Font_Size.setCurrentIndex(1)
                
            # 获取CIE图表字体大小设置
            font_size = self.settings['plot'].get('cie_font_size', 'Medium')
            if font_size == 'Small':
                self.ui.comboBox_Plot_CIExy_Font_Size.setCurrentIndex(0)
            elif font_size == 'Large':
                self.ui.comboBox_Plot_CIExy_Font_Size.setCurrentIndex(2)
            else:  # Medium为默认值
                self.ui.comboBox_Plot_CIExy_Font_Size.setCurrentIndex(1)
            
            print("Default settings for Plot tab restored")
            
        elif current_tab_index == 2:  # Export标签页
            # 只更新export类别，保留其他类别的设置
            if 'export' not in self.settings:
                self.settings['export'] = {}
                
            # 备份当前的目录和格式设置
            backup_settings = {}
            for key in ['default_directory', 'default_format', 'last_directory', 'last_plot_directory']:
                if key in self.settings['export']:
                    backup_settings[key] = self.settings['export'][key]
            
            # 更新export设置为默认值
            self.settings['export'].update(default_settings['export'])
            
            # 恢复备份的目录和格式设置
            for key, value in backup_settings.items():
                self.settings['export'][key] = value
            
            # 更新UI中的Export设置
            # 设置分隔符
            sep_index = self.ui.comboBox_Export_Separator.findText(self.settings['export']['separator'])
            if sep_index >= 0:
                self.ui.comboBox_Export_Separator.setCurrentIndex(sep_index)
            
            # 设置是否拷贝标题
            header_index = self.ui.comboBox_Copy_Header.findText(self.settings['export']['copy_header'])
            if header_index >= 0:
                self.ui.comboBox_Copy_Header.setCurrentIndex(header_index)
                
            print("Default settings for Export tab restored")
            
        # 显示提示消息
        QMessageBox.information(self, "Restore Default", "Default settings for current tab have been restored")
        
    def accept(self):
        """点击确定按钮时的处理"""
        # 验证rho_lambda输入是否为有效的浮点数
        try:
            rho_lambda = float(self.ui.lineEdit_Gen_pho.text())
            if rho_lambda <= 0:
                raise ValueError("rho_lambda must be a positive number")
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid rho_lambda value (positive float)")
            self.ui.lineEdit_Gen_pho.setFocus()
            return
            
        # 获取新的设置（已经包含了保留原始设置的逻辑）
        self.settings = self.get_settings()
        super().accept()
    
    def choose_reflectance_color(self):
        """选择反射率图表的颜色"""
        current_color = QColor(self.settings['plot']['reflectance_color'])
        color = QColorDialog.getColor(current_color, self, "Choose Reflectance Color")
        if color.isValid():
            self.settings['plot']['reflectance_color'] = color.name()
            # 由于UI中没有颜色按钮，我们只更新内部设置 