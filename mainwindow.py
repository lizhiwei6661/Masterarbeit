import os
import sys
import numpy as np
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QTableWidgetItem,
    QHeaderView, QFileDialog, QMenu, QColorDialog, QVBoxLayout, QDialog, QPushButton, QWidget, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QAction, QColor, QPixmap, QIcon, QClipboard, QScreen
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.patches as patches
import scipy.interpolate as interp
import json
import matplotlib.ticker as ticker
import warnings
import colour
from colour.plotting.diagrams import plot_chromaticity_diagram_colours
from colour.plotting import plot_RGB_colourspaces_in_chromaticity_diagram_CIE1931

from ui_form import Ui_MainWindow
from import_dialog import ImportDialog
from export_dialog import ExportDialog
from plot_dialog import PlotDialog
from settings_dialog import SettingsDialog
from about_dialog import AboutDialog
from reflectance_data_dialog import ReflectanceDataDialog
from color_calculator import ColorCalculator
from cie_data_dialog import CIEDataDialog


class MainWindow(QMainWindow):
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 初始化ui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # 设置窗口标题
        self.setWindowTitle("Aleksameter App")
        
        # 设置初始窗口大小
        self.resize(833, 660)  # 设置为833*660的大小
        
        # 初始化默认设置
        self.settings = self.get_default_settings()
        
        # 从配置文件加载设置（会覆盖默认设置）
        self.load_settings()
        
        # 初始化颜色计算器
        self.color_calculator = ColorCalculator()
        
        # 设置rho_lambda值
        self.color_calculator.set_rho_lambda(self.settings['general']['rho_lambda'])
        
        # 设置光源类型
        self.color_calculator.set_illuminant(self.settings['general']['illuminant'])
        
        # 初始化数据
        self.reset_data()
        
        # 设置界面
        self.setup_ui()
        
        # 创建菜单动作
        self.connect_menu_actions()
        
        # 连接按钮动作
        self.connect_button_actions()
        
        # 初始化导入数据目录
        self.import_directory = self.settings['import'].get('default_directory', None)
        
        # 将窗口放置在屏幕中心
        center_point = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        fg = self.frameGeometry()
        fg.moveCenter(center_point)
        self.move(fg.topLeft())
        
        # 初始化对话框引用为None
        self.reflectance_dialog = None
        self.cie_dialog = None
        
        # 初始禁用Export和Plot菜单选项
        self.update_menu_state(False)
    
    def reset_data(self):
        """重置数据存储"""
        self.data = {
            'wavelengths': self.color_calculator.wavelengths,
            'original_wavelengths': None,  # 用于存储原始测量的波长数据（通常是1nm间隔）
            'reflectance': {},
            'results': [],
            'file_names': [],
            # 添加新字段用于存储原始测量数据
            'raw_measurements': {}  # 格式: {'file_name': {'values': 原始值, 'wavelengths': 波长}}
        }
        
        # 重置图表
        if hasattr(self, 'reflectance_canvas'):
            self.update_reflectance_plot()
        if hasattr(self, 'cie_canvas'):
            self.update_cie_plot()
        
        # 清空结果表格
        if hasattr(self, 'ui') and hasattr(self.ui, 'table_results'):
            self.ui.table_results.setRowCount(0)
            
        # 禁用Export和Plot菜单选项
        self.update_menu_state(False)
    
    def setup_ui(self):
        """设置UI组件"""
        # 设置反射率图表
        self.setup_reflectance_plot()
        
        # 设置CIE图表
        self.setup_cie_plot()
        
        # 设置结果表格
        self.setup_results_table()
    
    def setup_reflectance_plot(self):
        """设置反射率图表"""
        # 创建图表 - 使用更宽的宽高比
        self.reflectance_figure = Figure(figsize=(6.5, 3.5), dpi=100)
        self.reflectance_canvas = FigureCanvas(self.reflectance_figure)
        # 移除工具栏，用户不需要这个功能
        # self.reflectance_toolbar = NavigationToolbar(self.reflectance_canvas, self)
        
        # 为X轴标签预留足够空间，减少左右边距使图表更宽
        self.reflectance_figure.subplots_adjust(bottom=0.17, left=0.07, right=0.95, top=0.88)
        
        # 创建布局并添加到view_Reflections，使其占满整个widget
        self.reflectance_layout = QVBoxLayout(self.ui.view_Reflections)
        self.reflectance_layout.setContentsMargins(0, 0, 0, 0)  # 移除布局边距
        self.reflectance_layout.setSpacing(0)  # 移除元素间距
        # 不再添加工具栏
        # self.reflectance_layout.addWidget(self.reflectance_toolbar)
        self.reflectance_layout.addWidget(self.reflectance_canvas)
        
        # 设置画布的尺寸策略，使其扩展填充可用空间
        self.reflectance_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 连接画布大小变化事件，确保图表随容器自适应
        self.reflectance_canvas.mpl_connect('resize_event', self._on_reflectance_resize)
        
        # 初始绘图
        self.update_reflectance_plot()
    
    def _on_reflectance_resize(self, event):
        """处理反射率图表大小变化事件"""
        # 获取当前标题显示状态
        show_title = self.settings['plot'].get('reflectance_show_title', True)
        
        # 根据标题显示状态调整顶部边距
        if show_title:
            self.reflectance_figure.subplots_adjust(bottom=0.2, top=0.85)
        else:
            self.reflectance_figure.subplots_adjust(bottom=0.2, top=0.92)
            
        # 调整图表布局，确保标签可见
        self.reflectance_figure.tight_layout(pad=0.4)
        
        # 重新绘制
        self.reflectance_canvas.draw_idle()
    
    def setup_cie_plot(self):
        """设置CIE图表"""
        # 创建图表 - 使用更小的尺寸
        self.cie_figure = Figure(figsize=(3.0, 3.0), dpi=100)
        self.cie_canvas = FigureCanvas(self.cie_figure)
        # 移除导航工具栏
        # self.cie_toolbar = NavigationToolbar(self.cie_canvas, self)
        
        # 创建布局并添加到view_colorSpace - 移除边距以更好地利用空间
        self.cie_layout = QVBoxLayout(self.ui.view_colorSpace)
        self.cie_layout.setContentsMargins(0, 0, 0, 0)  # 设置边距为0
        self.cie_layout.setSpacing(0)  # 设置组件间距为0
        # self.cie_layout.addWidget(self.cie_toolbar)  # 不再添加导航工具栏
        self.cie_layout.addWidget(self.cie_canvas)
        
        # 修改为自适应尺寸策略，允许图表随容器缩放
        self.cie_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 初始绘图
        self.update_cie_plot()
        
        # 监听尺寸变化事件，用于调整图表
        self.cie_canvas.mpl_connect('resize_event', self._on_cie_resize)
    
    def _on_cie_resize(self, event):
        """处理CIE图表大小变化事件"""
        # 调整图表布局，确保标签可见
        self.cie_figure.tight_layout(pad=0.4)
        # 重新绘制
        self.cie_canvas.draw_idle()
    
    def setup_results_table(self):
        """设置结果表格"""
        # 设置表头
        self.ui.table_results.setColumnCount(6)  # 增加到6列，添加颜色列
        self.ui.table_results.setHorizontalHeaderLabels([
            "CLR", "File Name", "x", "y", "sRGB Linear", "sRGB Gamma"
        ])
        
        # 获取表头
        header = self.ui.table_results.horizontalHeader()
        
        # 设置列的调整模式
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # 颜色列可调整
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)  # 文件名列可调整
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)  # x列
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)  # y列
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)  # sRGB Linear列
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)  # sRGB Gamma列
        
        # 设置初始列宽 - 适应更大的字体
        self.ui.table_results.setColumnWidth(0, 30)   # 颜色列宽度减小
        self.ui.table_results.setColumnWidth(1, 120)  # 文件名列宽度减小
        self.ui.table_results.setColumnWidth(2, 65)   # x列宽度减小
        self.ui.table_results.setColumnWidth(3, 65)   # y列宽度减小
        self.ui.table_results.setColumnWidth(4, 140)  # sRGB Linear列宽度减小
        self.ui.table_results.setColumnWidth(5, 140)  # sRGB Gamma列宽度减小
        
        # 设置行高
        self.ui.table_results.verticalHeader().setDefaultSectionSize(20)  # 调整行高为20像素（更紧凑）
        self.ui.table_results.verticalHeader().setVisible(False)  # 隐藏垂直表头
        
        # 设置表格样式
        self.ui.table_results.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                font-size: 9pt;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 2px;
                font-size: 9pt;
                border: 1px solid #d0d0d0;
            }
            QTableWidget::item {
                padding: 2px;
            }
        """)
        
        # 设置表格属性
        self.ui.table_results.setAlternatingRowColors(True)
        self.ui.table_results.setSortingEnabled(True)
        self.ui.table_results.setSelectionBehavior(self.ui.table_results.SelectionBehavior.SelectRows)
        
        # 设置初始列宽调整
        QTimer.singleShot(100, self.adjust_table_columns)
    
    def connect_menu_actions(self):
        """连接菜单动作"""
        # File菜单
        self.ui.actionImport.triggered.connect(self.open_import_dialog)
        self.ui.actionExport.triggered.connect(self.open_export_dialog)
        self.ui.actionPlot.triggered.connect(self.open_plot_dialog)
        self.ui.actionSettings.triggered.connect(self.open_settings_dialog)
        
        # 确保在macOS下正确显示Settings菜单项
        self.ui.actionSettings.setMenuRole(QAction.MenuRole.NoRole)
        
        # Edit菜单
        self.ui.actionCopy_all_data.triggered.connect(self.copy_all_data)
        self.ui.actionClear.triggered.connect(self.clear_data)
        
        # 创建光源子菜单
        illuminant_menu = QMenu("Illuminant", self)
        self.ui.menu_edit.addMenu(illuminant_menu)
        
        # 添加光源选项
        self.illuminant_actions = {}
        for illuminant in ['D65', 'D50', 'A', 'E']:  # 添加 'E' 光源
            action = QAction(illuminant, self)
            action.setCheckable(True)
            action.setData(illuminant)
            if illuminant == self.settings['general']['illuminant']:
                action.setChecked(True)
            action.triggered.connect(self.change_illuminant)
            illuminant_menu.addAction(action)
            self.illuminant_actions[illuminant] = action
        
        # 创建Gamut子菜单
        gamut_menu = QMenu("Gamut", self)
        self.ui.menu_edit.addMenu(gamut_menu)
        
        # 添加Gamut选项
        self.gamut_actions = {}
        for gamut in ['None', 'sRGB', 'Adobe RGB', 'HTC VIVE Pro Eye', 'Meta Oculus Quest 1', 'Meta Oculus Quest 2', 'Meta Oculus Rift']:
            action = QAction(gamut, self)
            action.setCheckable(True)
            action.setData(gamut)
            if gamut == self.settings['general']['gamut']:
                action.setChecked(True)
            action.triggered.connect(self.change_gamut)
            gamut_menu.addAction(action)
            self.gamut_actions[gamut] = action
        
        # Help菜单
        self.ui.actionAbout.triggered.connect(self.open_about_dialog)
        self.ui.actionManual.triggered.connect(self.open_manual)
    
    def connect_button_actions(self):
        """连接按钮事件"""
        self.ui.pushButton_show_Reflections_Data.clicked.connect(self.show_reflectance_data)
        self.ui.pushButton_copydata.clicked.connect(self.copy_table_data)
        self.ui.pushButton_show_CIE_Data.clicked.connect(self.show_cie_data)
        # 修改按钮文本
        self.ui.pushButton_show_CIE_Data.setText("Show CIE Diagram")
    
    def get_settings_file_path(self):
        """获取设置文件的绝对路径（使用用户数据目录）"""
        # 获取用户数据目录
        if sys.platform == 'darwin':  # macOS
            user_data_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'Aleksameter')
        elif sys.platform == 'win32':  # Windows
            user_data_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'Aleksameter')
        else:  # Linux和其他平台
            user_data_dir = os.path.join(os.path.expanduser('~'), '.aleksameter')
        
        # 确保目录存在
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
        
        # 设置文件完整路径
        settings_file = os.path.join(user_data_dir, "app_settings.json")
        print(f"设置文件路径: {settings_file}")
        return settings_file
    
    def load_settings(self):
        """加载设置"""
        try:
            settings_file = self.get_settings_file_path()
            
            # 检查文件是否存在且不为空
            if os.path.exists(settings_file) and os.path.getsize(settings_file) > 0:
                with open(settings_file, 'r') as f:
                    loaded_settings = json.loads(f.read())
                
                # 获取默认设置作为基础
                default_settings = self.get_default_settings()
                
                # 创建一个新的设置字典，从默认设置开始
                complete_settings = default_settings.copy()
                
                # 用加载的设置覆盖默认设置
                for category in loaded_settings:
                    if category in complete_settings:
                        complete_settings[category].update(loaded_settings[category])
                    else:
                        complete_settings[category] = loaded_settings[category]
                
                # 应用完整的设置
                self.settings = complete_settings
                print(f"设置已从 {settings_file} 加载")
            else:
                print(f"设置文件 {settings_file} 不存在或为空，使用默认设置")
                # 使用默认设置
                self.settings = self.get_default_settings()
                # 创建默认设置文件
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {str(e)}")
            import traceback
            traceback.print_exc()
            # 使用默认设置并创建设置文件
            self.settings = self.get_default_settings()
            self.save_settings()
    
    def save_settings(self):
        """保存设置"""
        try:
            settings_file = self.get_settings_file_path()
            
            # 确保目录存在
            settings_dir = os.path.dirname(settings_file)
            if not os.path.exists(settings_dir):
                os.makedirs(settings_dir)
                
            with open(settings_file, 'w') as f:
                f.write(json.dumps(self.settings, indent=4))
            print(f"设置已保存到 {settings_file}")
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def get_default_settings(self):
        """获取默认设置"""
        return {
            'general': {
                'illuminant': 'D65',  # D65是默认光源
                'rgb_values': '0 ... 1',  # RGB值默认显示为0-1的小数
                'rho_lambda': 0.989,  # rho_lambda默认为0.989
                'gamut': 'None'  # 默认不显示色域
            },
            'plot': {
                'reflectance_width': 1600,  # 设置宽度为1600
                'reflectance_height': 800,  # 设置高度为800
                'cie_width': 900,  # 设置宽度为900
                'cie_height': 900,  # 设置高度为900
                'reflectance_title': 'Reflectance Spectra of Measured Samples',
                'cie_title': 'CIE Chromaticity Diagram',
                'reflectance_show_title': True,
                'cie_show_title': True,
                'reflectance_show_legend': True,
                'cie_show_legend': True,
                'reflectance_color': '#1f77b4',  # 默认蓝色
                
                # 添加字体大小设置
                'reflectance_font_size': 'Medium',  # 默认中等字体大小
                'cie_font_size': 'Medium',  # 默认中等字体大小
                
                # 导出图表的字体设置
                'export_font_family': 'Arial',
                'export_title_size': 12,
                'export_axis_label_size': 10,
                'export_tick_label_size': 8,
                'export_legend_size': 9,
                
                # 不同DPI下的字体缩放比例
                'export_dpi_scaling': {
                    '150': 1.0,  # 150DPI时不缩放
                    '300': 0.9,  # 300DPI时缩小10%
                    '600': 0.8   # 600DPI时缩小20%
                }
            },
            'export': {
                'separator': 'Point',
                'copy_header': 'Yes',
                'default_directory': os.path.expanduser('~'),
                'default_format': 'xlsx',
                'include_header': True,
                'decimal_places': 6,
                'last_directory': os.path.expanduser('~'),
                'last_plot_directory': os.path.expanduser('~')
            },
            'import': {
                'default_directory': os.path.expanduser('~'),
                'black_reference_directory': os.path.expanduser('~'),
                'white_reference_directory': os.path.expanduser('~'),
                'measurement_directory': os.path.expanduser('~')
            },
            'plot_export': {
                'dpi_index': 1,  # 默认300 DPI (index 1)
                'format_index': 0,  # 默认PNG格式 (index 0)
                'export_reflectance': True,
                'export_cie': True
            },
            'export_dialog': {
                'format_index': 0,  # 默认Excel格式 (index 0)
                'export_rho': True,
                'export_color': True
            }
        }
    
    def open_import_dialog(self):
        """打开导入对话框"""
        dialog = ImportDialog(self)
        result = dialog.exec()
        
        print(f"Import dialog result: {result}")
        
        # 在PySide6中，QDialog.Accepted值为1
        if result == 1:  # QDialog.Accepted
            # 获取导入数据
            import_data = dialog.get_selected_data()
            
            # 处理数据
            self.process_imported_data(import_data)
            
            # 显示日志消息
            print(f"Import dialog accepted, processing data...")
        else:
            print("Import dialog cancelled")
            
    def process_imported_data(self, import_data):
        """处理导入的数据"""
        if not import_data or not 'mode' in import_data:
            print("导入数据无效，未包含处理模式")
            QMessageBox.warning(self, "Warning", "Invalid import data. Please try again.")
            return
        
        mode = import_data['mode']
        black_reference_path = import_data.get('black_reference', '')
        white_reference_path = import_data.get('white_reference', '')
        measurement_paths = import_data.get('measurements', [])
        
        print(f"\n====== 处理导入数据 ======")
        print(f"模式: {mode}")
        print(f"黑参考文件: {black_reference_path}")
        print(f"白参考文件: {white_reference_path}")
        print(f"测量文件数量: {len(measurement_paths)}")
        
        if not measurement_paths:
            QMessageBox.warning(self, "Warning", "No measurement files selected.")
            return
        
        # 重置数据
        self.reset_data()
        
        # 设置rho_lambda值从settings中获取
        rho_lambda = self.settings['general']['rho_lambda']
        self.color_calculator.set_rho_lambda(rho_lambda)
        print(f"设置rho_lambda值为: {rho_lambda}")
        
        # 设置光源类型从settings中获取
        illuminant = self.settings['general']['illuminant']
        self.color_calculator.set_illuminant(illuminant)
        print(f"设置光源类型为: {illuminant}")
        
        # 设置校准模式
        if mode == "Aleksameter" and black_reference_path and white_reference_path:
            print(f"Aleksameter模式: 使用黑白参考校准")
            
            # 加载黑白参考数据
            black_ref = self.load_data_from_file(black_reference_path)
            white_ref = self.load_data_from_file(white_reference_path)
            
            if black_ref is None or white_ref is None:
                error_msg = "Cannot load reference files."
                print(f"错误: {error_msg}")
                QMessageBox.warning(self, "Warning", error_msg)
                return
                
            # 检查参考数据是否有效
            if 'wavelengths' not in black_ref or 'values' not in black_ref or 'wavelengths' not in white_ref or 'values' not in white_ref:
                error_msg = "Invalid reference file format."
                print(f"错误: {error_msg}")
                QMessageBox.warning(self, "Warning", error_msg)
                return
                
            # 设置校准模式
            print("设置校准模式...")
            self.color_calculator.set_calibration_mode(True, black_ref['values'], white_ref['values'])
            
            # 保存黑白参考数据用于后续重新计算
            self.data['black_reference'] = black_ref
            self.data['white_reference'] = white_ref
        else:
            # Generic模式，不使用校准
            print(f"Generic模式: 不使用校准")
            self.color_calculator.set_calibration_mode(False)
        
        # 加载测量数据
        measurements = []
        self.data['file_names'] = []  # 清空文件名列表
        
        for path in measurement_paths:
            try:
                print(f"加载测量文件: {os.path.basename(path)}")
                # 从文件加载数据
                data = self.load_data_from_file(path)
                
                if data is None:
                    print(f"  错误: 无法加载文件 {path}")
                    continue
                    
                if 'wavelengths' not in data or 'values' not in data:
                    print(f"  错误: 文件格式无效 {path}")
                    continue
                
                print(f"  成功加载: {len(data['wavelengths'])}个数据点, 范围: {min(data['wavelengths']):.1f}-{max(data['wavelengths']):.1f} nm")
                measurements.append(data)
                self.data['file_names'].append(os.path.basename(path))
                
                # 保存原始测量数据
                file_name = os.path.basename(path)
                self.data['raw_measurements'][file_name] = {
                    'values': data['values'].copy(),
                    'wavelengths': data['wavelengths'].copy()
                }
            except Exception as e:
                error_msg = f"Error loading file {path}: {str(e)}"
                print(f"错误: {error_msg}")
                QMessageBox.warning(self, "Warning", error_msg)
        
        if not measurements:
            QMessageBox.warning(self, "Warning", "No valid measurement files.")
            return
        
        print(f"处理 {len(measurements)} 个测量文件...")
        
        # 处理每个测量数据
        for i, measurement in enumerate(measurements):
            try:
                file_name = self.data['file_names'][i]
                wavelengths = measurement['wavelengths']
                values = measurement['values']
                
                # 保存第一个测量的原始波长数据
                if i == 0 and wavelengths is not None and len(wavelengths) > 0:
                    self.data['original_wavelengths'] = np.array(wavelengths)
                    print(f"保存原始波长数据: 范围={min(wavelengths):.1f}-{max(wavelengths):.1f} nm, "
                          f"点数={len(wavelengths)}, 步长={wavelengths[1]-wavelengths[0]:.1f}nm")
                
                print(f"\n处理第 {i+1}/{len(measurements)} 个测量: {file_name}")
                print(f"  波长范围: {min(wavelengths):.1f}-{max(wavelengths):.1f} nm")
                print(f"  数据点数: {len(wavelengths)}")
                
                # 计算颜色参数
                result = self.color_calculator.process_measurement(values, wavelengths)
                
                if result is None:
                    print(f"  错误: 处理失败，未返回结果")
                    continue
                
                # 存储反射率数据
                if 'reflectance' in result:
                    # 保存完整的结果字典，包含原始步长和1nm步长的数据
                    self.data['reflectance'][file_name] = result
                else:
                    print(f"  警告: 结果中未包含反射率数据")
                
                # 存储结果
                if 'xy' in result and 'rgb_linear' in result and 'rgb_gamma' in result and 'hex_color' in result:
                    self.data['results'].append({
                        'file_name': file_name,
                        'x': result['xy'][0],
                        'y': result['xy'][1],
                        'rgb_linear': result['rgb_linear'],
                        'rgb_gamma': result['rgb_gamma'],
                        'hex_color': result['hex_color']
                    })
                    
                    print(f"  计算结果: xy坐标=({result['xy'][0]:.4f}, {result['xy'][1]:.4f}), 颜色={result['hex_color']}")
                else:
                    print(f"  警告: 结果中缺少必要的颜色数据")
            
            except Exception as e:
                error_msg = f"处理文件 {file_name} 时出错: {str(e)}"
                print(f"错误: {error_msg}")
                import traceback
                traceback.print_exc()
                QMessageBox.warning(self, "错误", error_msg)
        
        if not self.data['results']:
            QMessageBox.warning(self, "警告", "无法计算任何结果。")
            return
            
        # 更新界面
        print("更新界面...")
        try:
            self.update_reflectance_plot()
            self.update_cie_plot()
            self.update_results_table()
            
            # 更新扩展CIE图表窗口（如果已打开）
            if self.cie_dialog is not None and self.cie_dialog.isVisible():
                print("更新扩展CIE图表窗口...")
                self.update_expanded_cie_plot()
            
            # 显示成功消息
            QMessageBox.information(self, "Import Complete", 
                                f"Successfully processed {len(self.data['results'])}/{len(measurements)} measurement files.")
                                
            # 启用Export和Plot菜单选项
            self.update_menu_state(True)
            
            # 如果反射率数据对话框已打开，更新其内容
            if self.reflectance_dialog is not None and self.reflectance_dialog.isVisible():
                try:
                    displayed_wavelengths = self.data['original_wavelengths'] if self.data['original_wavelengths'] is not None else self.data['wavelengths']
                    
                    # 准备数据集字典，正确提取反射率数据
                    processed_datasets = {}
                    for name, reflectance_data in self.data['reflectance'].items():
                        # 检查数据格式
                        if isinstance(reflectance_data, dict):
                            # 优先使用1nm步长的数据
                            if 'reflectance_1nm' in reflectance_data and len(reflectance_data['reflectance_1nm']) > 0:
                                processed_datasets[name] = reflectance_data['reflectance_1nm']
                            # 其次使用原始反射率数据
                            elif 'reflectance' in reflectance_data:
                                processed_datasets[name] = reflectance_data['reflectance']
                        else:
                            # 旧格式：直接是数据数组
                            processed_datasets[name] = reflectance_data
                    
                    # 更新对话框
                    self.reflectance_dialog.update_data(displayed_wavelengths, processed_datasets)
                    print("反射率数据对话框已更新")
                except Exception as e:
                    print(f"更新反射率数据对话框时出错: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
        except Exception as e:
            error_msg = f"更新界面时出错: {str(e)}"
            print(f"错误: {error_msg}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "错误", error_msg)
    
    def load_data_from_file(self, file_path):
        """从文件加载数据"""
        try:
            # 根据文件扩展名选择不同的加载方法
            ext = os.path.splitext(file_path)[1].lower()
            
            # 处理CSV文件（专门针对示例中的格式）
            if ext == '.csv':
                print(f"正在加载CSV文件: {file_path}")
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                # 查找数据部分开始的位置
                data_start_index = -1
                for i, line in enumerate(lines):
                    if line.startswith("Wavelength [nm],"):
                        data_start_index = i + 1
                        break
                
                if data_start_index >= 0:
                    print(f"在第{data_start_index}行找到数据部分")
                    # 提取数据
                    wavelengths = []
                    values = []
                    for line in lines[data_start_index:]:
                        parts = line.strip().split(',')
                        if len(parts) >= 2 and parts[0] and parts[1]:
                            try:
                                wavelength = float(parts[0])
                                value = float(parts[1])
                                wavelengths.append(wavelength)
                                values.append(value)
                            except ValueError:
                                continue
                    
                    if wavelengths and values:
                        wavelengths_np = np.array(wavelengths)
                        values_np = np.array(values)
                        
                        # 打印波长信息
                        if len(wavelengths) > 1:
                            step = wavelengths[1] - wavelengths[0]
                            print(f"提取了{len(wavelengths)}个数据点")
                            print(f"波长范围: {wavelengths[0]}-{wavelengths[-1]}nm, 步长: {step}nm")
                            
                            # 检查波长是否均匀
                            diff = np.diff(wavelengths_np)
                            if not np.allclose(diff, step, rtol=1e-3):
                                print("警告: 波长步长不均匀！")
                                print(f"最小步长: {np.min(diff)}nm, 最大步长: {np.max(diff)}nm")
                            
                            # 检查数值范围
                            print(f"数值范围: {np.min(values_np)}-{np.max(values_np)}")
                        
                        return {
                            'wavelengths': wavelengths_np,
                            'values': values_np
                        }
                
                # 如果上述解析失败，尝试常规CSV解析
                print("尝试常规CSV解析方法...")
                try:
                    data = np.genfromtxt(file_path, delimiter=',', skip_header=1, names=True)
                    if data.size > 0:
                        # 尝试找到波长和值的列
                        col_names = data.dtype.names
                        wavelength_col = None
                        value_col = None
                        
                        # 尝试匹配列名
                        for col in col_names:
                            col_lower = col.lower()
                            if 'wave' in col_lower or 'lambda' in col_lower or 'nm' in col_lower:
                                wavelength_col = col
                            elif 'value' in col_lower or 'reflectance' in col_lower or 'intensity' in col_lower:
                                value_col = col
                        
                        # 如果找不到合适的列名，使用前两列
                        if wavelength_col is None and len(col_names) > 0:
                            wavelength_col = col_names[0]
                        if value_col is None and len(col_names) > 1:
                            value_col = col_names[1]
                        
                        if wavelength_col and value_col:
                            wavelengths_np = data[wavelength_col]
                            values_np = data[value_col]
                            
                            # 打印波长信息
                            if len(wavelengths_np) > 1:
                                step = wavelengths_np[1] - wavelengths_np[0]
                                print(f"使用列 '{wavelength_col}' 和 '{value_col}'")
                                print(f"波长范围: {wavelengths_np[0]}-{wavelengths_np[-1]}nm, 步长: {step}nm")
                                print(f"数值范围: {np.min(values_np)}-{np.max(values_np)}")
                            
                            return {
                                'wavelengths': wavelengths_np,
                                'values': values_np
                            }
                except Exception as e:
                    print(f"常规CSV解析失败: {e}")
            
            # 如果是其他文件类型，或CSV解析失败
            print(f"不支持的文件类型: {ext}")
            return None
            
        except Exception as e:
            print(f"加载文件时出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def update_reflectance_plot(self):
        """更新反射率图表"""
        # 清除图表
        self.reflectance_figure.clear()
        
        # 创建子图
        ax = self.reflectance_figure.add_subplot(111)
        
        # 设置标题（根据设置决定是否显示）
        show_title = self.settings['plot'].get('reflectance_show_title', True)
        title_text = self.settings['plot'].get('reflectance_title', "Reflectance Spectra of Measured Samples")
        
        # 只有当设置为显示标题时才显示
        if show_title:
            ax.set_title(title_text, fontsize=10)
        
        # 设置其他基本属性
        ax.set_xlabel("Wavelength (nm)", fontsize=8)  # 恢复为原来的大小
        ax.set_ylabel("$\\rho$", fontsize=8)  # 恢复为原来的大小
        ax.tick_params(axis='both', which='major', labelsize=7)  # 恢复为原来的大小
        
        # 设置X轴范围
        ax.set_xlim(380, 780)
        
        # 设置固定的刻度位置，包括50nm间隔和边缘值
        tick_positions = [380, 400, 450, 500, 550, 600, 650, 700, 750, 780]
        ax.xaxis.set_major_locator(ticker.FixedLocator(tick_positions))
        
        # 启用网格
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # 检查是否有数据可以绘制
        if self.data['reflectance']:
            max_reflectance = 0
            
            # 绘制反射率数据
            for file_name, result_data in self.data['reflectance'].items():
                # 获取波长和反射率数据
                if 'reflectance_1nm' in result_data and 'wavelengths_1nm' in result_data:
                    wavelengths = result_data['wavelengths_1nm']
                    reflectance = result_data['reflectance_1nm']
                else:
                    wavelengths = result_data['wavelengths'] if 'wavelengths' in result_data else self.data['wavelengths']
                    reflectance = result_data['reflectance']
                
                # 更新最大反射率值
                if len(reflectance) > 0:
                    max_reflectance = max(max_reflectance, np.max(reflectance))
                
                # 处理数据长度不匹配
                if len(wavelengths) != len(reflectance):
                    try:
                        # 进行插值
                        source_wavelengths = np.linspace(wavelengths[0], wavelengths[-1], len(reflectance))
                        interp_func = interp.interp1d(source_wavelengths, reflectance, bounds_error=False, fill_value="extrapolate")
                        reflectance = interp_func(wavelengths)
                    except Exception as e:
                        print(f"插值失败: {e}")
                        continue
                
                # 绘制曲线
                ax.plot(wavelengths, reflectance, label=file_name)
            
            # 自适应调整Y轴范围
            if max_reflectance > 0:
                if max_reflectance > 1.0:
                    # 如果反射率大于1.0，设置适当的上限
                    ax.set_ylim(0, max_reflectance * 1.05)
                elif max_reflectance < 0.1:
                    # 如果最大反射率很小，使用更合适的上限
                    ax.set_ylim(0, max_reflectance * 1.5)
                else:
                    # 如果反射率在0.1到1.0之间，使用标准设置
                    ax.set_ylim(0, min(1.05, max_reflectance * 1.2))
            else:
                # 如果没有有效数据，使用默认范围
                ax.set_ylim(0, 1.05)
            
            # 添加图例（如果有多条曲线）
            if len(self.data['reflectance']) > 1:
                # 根据设置决定是否显示图例
                show_legend = self.settings['plot'].get('reflectance_show_legend', True)
                if show_legend:
                    ax.legend(fontsize=7)
                    print("显示反射率图表图例")
                else:
                    print("反射率图表图例已被设置为不显示")
            else:
                print("只有一条曲线，不需要显示图例")
        else:
            # 没有数据时使用默认范围
            ax.set_ylim(0, 1.05)
        
        # 调整底部边距，确保X轴标签显示
        self.reflectance_figure.subplots_adjust(bottom=0.2)
        
        # 调整图表布局以适应标题显示/隐藏状态
        self.reflectance_figure.tight_layout(pad=0.4)
        
        # 刷新图表
        self.reflectance_canvas.draw()
    
    def update_cie_plot(self):
        """更新CIE图表，使用colour库绘制带颜色的色度图"""
        # 清除图表
        self.cie_figure.clear()
        
        # 创建子图
        ax = self.cie_figure.add_subplot(111)
        
        # 设置默认字体大小 - 恢复原来的字体大小设置
        tick_size = 8
        label_size = 9
        wavelength_label_size = 6  # 波长标签使用更小的字体
        
        # 检查是否有数据可以绘制
        has_data = len(self.data['results']) > 0
        
        # 启用轴线背景设置，确保网格在所有元素后面
        ax.set_axisbelow(True)
        
        try:
            # 禁用警告消息
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # 首先绘制色度图的彩色背景
                plot_chromaticity_diagram_colours(
                    axes=ax,
                    diagram_colours="RGB",  # 使用RGB颜色
                    method="CIE 1931",  # 使用CIE 1931方法
                    standalone=False,  # 不独立绘图
                    title=False,  # 不使用默认标题
                    bounding_box=(0, 0.8, 0, 0.9)  # 恢复原始设置
                )
                
                # 获取光谱轨迹线的数据点
                cmfs = colour.colorimetry.MSDS_CMFS['CIE 1931 2 Degree Standard Observer']
                XYZ = cmfs.values
                xy = colour.XYZ_to_xy(XYZ)
                wavelengths = cmfs.wavelengths
                
                # 创建波长到坐标的映射
                wavelength_dict = {wl: (x, y) for wl, (x, y) in zip(wavelengths, xy)}
                
                # 定义我们想要标记的波长范围（460-620nm，每20nm一个标记）
                custom_wavelength_labels = list(range(460, 640, 20))
                
                # 创建平滑的边界线 - 使用更多的点插值以获得更平滑的效果
                # 使用scipy的插值方法
                from scipy.interpolate import interp1d
                
                # 创建闭合的光谱轨迹点列表（首尾相连）
                # 光谱轨迹线
                x_locus = np.append(xy[..., 0], xy[0, 0])
                y_locus = np.append(xy[..., 1], xy[0, 1])
                
                # 创建参数化的坐标，用于插值
                t = np.linspace(0, 1, len(x_locus))
                
                # 创建插值函数
                fx = interp1d(t, x_locus, kind='cubic')
                fy = interp1d(t, y_locus, kind='cubic')
                
                # 生成更密集的点进行插值，使曲线更平滑
                t_new = np.linspace(0, 1, 1000)
                x_smooth = fx(t_new)
                y_smooth = fy(t_new)
                
                # 使用高zorder绘制平滑的光谱边界线
                ax.plot(
                    x_smooth, 
                    y_smooth, 
                    color='black', 
                    linewidth=1.0,
                    solid_capstyle='round',
                    zorder=10
                )
                
                # 紫色线 - 连接最高和最低波长的点
                purple_line = np.vstack([
                    [xy[-1, 0], xy[-1, 1]],  # 最高波长点
                    [xy[0, 0], xy[0, 1]]      # 最低波长点
                ])
                
                # 使用虚线绘制紫色线
                ax.plot(
                    purple_line[:, 0], 
                    purple_line[:, 1], 
                    color='black', 
                    linewidth=1.0,
                    linestyle='--',
                    zorder=10
                )
                
                # 手动绘制色域，确保使用细黑线
                gamut = self.settings['general']['gamut']
                
                # 绘制色域边界 - 根据选择的色域定义相应顶点
                if gamut == 'None':
                    # 不绘制色域
                    pass
                elif gamut == 'sRGB':
                    # sRGB色域顶点
                    r = (0.64, 0.33)
                    g = (0.30, 0.60)
                    b = (0.15, 0.06)
                elif gamut == 'Adobe RGB':
                    # Adobe RGB色域顶点
                    r = (0.64, 0.33)
                    g = (0.21, 0.71)
                    b = (0.15, 0.06)
                elif gamut == 'HTC VIVE Pro Eye':
                    # HTC VIVE Pro Eye色域顶点（精确值）
                    r = (0.6585, 0.3407)
                    g = (0.2326, 0.7119)
                    b = (0.1431, 0.0428)
                elif gamut == 'Meta Oculus Quest 1':
                    # Meta Oculus Quest 1色域顶点（精确值）
                    r = (0.6596, 0.3396)
                    g = (0.2395, 0.7069)
                    b = (0.1452, 0.0531)
                elif gamut == 'Meta Oculus Quest 2':
                    # Meta Oculus Quest 2色域顶点（精确值）
                    r = (0.6364, 0.3305)
                    g = (0.3032, 0.5938)
                    b = (0.1536, 0.0632)
                elif gamut == 'Meta Oculus Rift':
                    # Meta Oculus Rift色域顶点（精确值）
                    r = (0.6690, 0.3300)
                    g = (0.2545, 0.7015)
                    b = (0.1396, 0.0519)
                else:
                    # 默认使用sRGB
                    r = (0.64, 0.33)
                    g = (0.30, 0.60)
                    b = (0.15, 0.06)
                
                # 仅当色域不是'None'时创建和绘制色域多边形
                if gamut != 'None':
                    # 创建闭合多边形的点列表
                    x_points = [r[0], g[0], b[0], r[0]]
                    y_points = [r[1], g[1], b[1], r[1]]
                    
                    # 使用黑色细线绘制色域边界，zorder设置为30以确保在最上层
                    ax.plot(x_points, y_points, '-', color='black', linewidth=1.0, 
                           zorder=30, label=gamut)
                
                # 绘制当前使用的光源点
                illuminant = self.settings['general']['illuminant']
                
                # 常见光源的xy坐标
                illuminant_coords = {
                    'D65': (0.3128, 0.3290),
                    'D50': (0.3457, 0.3585),
                    'A': (0.4476, 0.4074),
                    'E': (1/3, 1/3)  # 等能光源在(1/3, 1/3)
                }
                
                # 移除所有可能遗留的标记点和文本标注（保留这部分代码）
                for child in ax.get_children():
                    # 移除文本标注（波长数字）
                    if hasattr(child, 'get_text') and child.get_text() and child.get_text().isdigit():
                        child.remove()
                    # 移除点标记，但不包括数据点
                    if hasattr(child, 'get_marker') and child.get_marker() not in [None, 'None', ''] and child.get_zorder() < 30:
                        child.remove()
                
                # 在移除标记点之后绘制光源点
                if illuminant in illuminant_coords:
                    # 获取光源坐标
                    x_illum, y_illum = illuminant_coords[illuminant]
                    
                    # 绘制光源点，使用小空心黑点
                    ax.plot(x_illum, y_illum, 'o', color='black', markersize=4, markerfacecolor='none', markeredgewidth=0.8, zorder=50)
                    
                    # 在光源点右上方添加标注，使用透明背景
                    ax.annotate(
                        f"{illuminant}",
                        (x_illum + 0.02, y_illum + 0.02),  # 偏移量确保标注在点的右上方
                        fontsize=wavelength_label_size,  # 与波长标签一样的字体大小
                        color='black',
                        ha='left',  # 左对齐
                        va='bottom',  # 底对齐
                        zorder=50
                    )
                
                # 在CIE边界上添加460-620nm的波长标记，确保小巧美观
                for wl in custom_wavelength_labels:
                    if wl in wavelength_dict:
                        x, y = wavelength_dict[wl]
                        
                        # 获取点位置与中心点(1/3, 1/3)的方向向量
                        center = np.array([1/3, 1/3])
                        point = np.array([x, y])
                        direction = point - center
                        
                        # 标准化方向向量并延长
                        direction = direction / np.linalg.norm(direction)
                        
                        # 为特定波长调整偏移量
                        if wl == 460:
                            # 对于460nm，向左上方移动以避免超出边界
                            offset = np.array([-0.02, 0.02])
                        elif wl == 540:
                            # 对于540nm，向右上方移动更多
                            offset = np.array([0.07, 0.03])
                        elif wl == 620:
                            # 对于620nm，更多向右上方移动
                            offset = np.array([0.03, 0.05])
                        else:
                            # 其他波长使用标准偏移量
                            offset = direction * 0.015
                        
                        # 绘制小点
                        ax.plot(x, y, 'o', color='black', markersize=2, zorder=15)
                        
                        # 确定文本对齐方式
                        h_align = 'left' if direction[0] > 0 else 'right'
                        v_align = 'bottom' if direction[1] > 0 else 'top'
                        
                        # 添加波长标签，字体更小
                        ax.annotate(
                            f"{wl}",
                            (x + offset[0], y + offset[1]),
                            fontsize=wavelength_label_size,
                            color='black',
                            ha=h_align,
                            va=v_align,
                            zorder=15,
                            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.1')
                        )
                
        except Exception as e:
            # 如果colour库绘制失败，回退到原始方法
            print(f"Colour库绘制失败，回退到原始方法: {e}")
            self.draw_cie_boundary(ax)
        
        # 设置标题和轴标签
        # 设置标题（根据设置决定是否显示）
        show_title = self.settings['plot'].get('cie_show_title', True)
        title_text = self.settings['plot'].get('cie_title', "CIE 1931 Chromaticity Diagram")
        
        if show_title:
            ax.set_title(title_text, fontsize=label_size)
        
        ax.set_xlabel("x", fontsize=label_size)
        ax.set_ylabel("y", fontsize=label_size)
        
        # 设置轴范围 - 恢复原始范围
        ax.set_xlim(0, 0.8)
        ax.set_ylim(0, 0.9)
        
        # 确保坐标轴显示刻度（不论是否有数据）
        # X轴刻度
        ax.set_xticks(np.arange(0, 0.9, 0.1))
        ax.tick_params(axis='x', which='major', labelsize=tick_size)
        
        # Y轴刻度
        ax.set_yticks(np.arange(0, 1.0, 0.1))
        ax.tick_params(axis='y', which='major', labelsize=tick_size)
        
        # 始终禁用网格，不考虑设置中的grid_enabled值
        ax.grid(False)
        
        # 如果没有数据，跳过后续步骤
        if not has_data:
            # 调整布局，确保标签可见
            self.cie_figure.tight_layout(pad=0.4)
            self.cie_canvas.draw()
            return
        
        # 绘制色度坐标点
        print(f"Plotting {len(self.data['results'])} CIE coordinates")
        for result in self.data['results']:
            x, y = result['x'], result['y']
            hex_color = result['hex_color']
            file_name = result['file_name']
            print(f"  Plotting point: {file_name} at ({x:.4f}, {y:.4f})")
            # 设置数据点与光源点大小一致，使用实心点，并添加标签供图例显示
            ax.plot(x, y, 'o', color=hex_color, markersize=4, markeredgecolor='black', 
                   markeredgewidth=0.8, zorder=100, label=file_name)
        
        # 根据设置决定是否显示图例 - 包括测量点和色域
        show_legend = self.settings['plot'].get('cie_show_legend', True)
        if show_legend:
            # 获取图例对象并设置较小的字体大小
            legend = ax.legend(fontsize=6, loc='upper right', frameon=True,
                            bbox_to_anchor=(1.0, 1.0))
            if legend is not None:
                # 设置图例框属性
                legend.set_frame_on(True)
                legend.set_title('')  # 移除图例标题
                # 调整图例大小
                legend._legend_box.align = "right"
        else:
            # 如果设置为不显示图例，则移除任何现有的图例
            legend = ax.get_legend()
            if legend is not None:
                legend.remove()
        
        # 调整布局 - 改用tight_layout代替固定的调整参数，以便更好地适应容器
        self.cie_figure.tight_layout(pad=0.4)
        
        # 刷新画布
        self.cie_canvas.draw()
    
    def draw_cie_boundary(self, ax):
        """绘制CIE 1931色度图边界"""
        # 使用简化的CIE 1931色度图边界点
        boundary_x = [0.1740, 0.0000, 0.0000, 0.0332, 0.0648, 0.0919, 0.1390, 0.1738, 0.2080, 0.2586, 0.3230, 0.3962, 0.4400, 0.4699, 0.4999, 0.5140, 0.5295, 0.5482, 0.5651, 0.5780, 0.5832, 0.5800, 0.5672, 0.5314, 0.4649, 0.3652, 0.2615, 0.1740]
        boundary_y = [0.0049, 0.0000, 0.0100, 0.0380, 0.0650, 0.0910, 0.2080, 0.2737, 0.3344, 0.4077, 0.4964, 0.5574, 0.5800, 0.5888, 0.5991, 0.6039, 0.6089, 0.6128, 0.6150, 0.6160, 0.6160, 0.6155, 0.6123, 0.6030, 0.5657, 0.4679, 0.2624, 0.0049]
        
        # 绘制边界
        ax.plot(boundary_x, boundary_y, 'k-')
        
        # 填充范围
        ax.fill(boundary_x, boundary_y, alpha=0.1, color='gray')
        
        # 绘制白点
        ax.plot(0.3127, 0.3290, 'ko', markersize=6, label='D65')
        
        # 绘制sRGB色域（手动定义顶点）
        srgb_r = (0.64, 0.33)
        srgb_g = (0.30, 0.60)
        srgb_b = (0.15, 0.06)
        srgb_x = [srgb_r[0], srgb_g[0], srgb_b[0], srgb_r[0]]
        srgb_y = [srgb_r[1], srgb_g[1], srgb_b[1], srgb_r[1]]
        ax.plot(srgb_x, srgb_y, 'r--', label=self.settings['general']['gamut'])
        
        # 设置网格，添加默认值检查
        grid_enabled = True  # 默认启用网格
        if 'plot' in self.settings:
            grid_enabled = self.settings['plot'].get('grid', True)
        ax.grid(grid_enabled)
    
    def update_results_table(self):
        """更新结果表格"""
        # 清空表格
        self.ui.table_results.setRowCount(0)
        
        # 检查是否有数据可以显示
        if not self.data['results']:
            print("No results to display in table")
            return
        
        # 填充结果
        print(f"Updating table with {len(self.data['results'])} results")
        
        # 获取RGB值格式设置
        rgb_format = self.settings['general']['rgb_values']
        
        for i, result in enumerate(self.data['results']):
            row_position = self.ui.table_results.rowCount()
            self.ui.table_results.insertRow(row_position)
            
            # 添加颜色列
            color_item = QTableWidgetItem()
            color_item.setBackground(QColor(result['hex_color']))
            self.ui.table_results.setItem(row_position, 0, color_item)
            
            # 添加文件名
            file_item = QTableWidgetItem(result['file_name'])
            self.ui.table_results.setItem(row_position, 1, file_item)
            
            # 添加x坐标
            x_item = QTableWidgetItem(f"{result['x']:.6f}")
            x_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.ui.table_results.setItem(row_position, 2, x_item)
            
            # 添加y坐标
            y_item = QTableWidgetItem(f"{result['y']:.6f}")
            y_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.ui.table_results.setItem(row_position, 3, y_item)
            
            # 添加线性sRGB
            rgb_linear = result['rgb_linear']
            rgb_linear_str = f"({rgb_linear[0]:.4f}, {rgb_linear[1]:.4f}, {rgb_linear[2]:.4f})"
            rgb_linear_item = QTableWidgetItem(rgb_linear_str)
            rgb_linear_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.ui.table_results.setItem(row_position, 4, rgb_linear_item)
            
            # 添加Gamma校正sRGB，根据设置进行格式化
            rgb_gamma = result['rgb_gamma']
            
            if rgb_format == '0 ... 255':
                # 格式化为0-255范围
                r_gamma = rgb_gamma[0] * 255
                g_gamma = rgb_gamma[1] * 255
                b_gamma = rgb_gamma[2] * 255
                rgb_gamma_str = f"({int(r_gamma) if r_gamma <= 255 else 255}, {int(g_gamma) if g_gamma <= 255 else 255}, {int(b_gamma) if b_gamma <= 255 else 255})"
            else:  # '0 ... 1'
                # 保持0-1范围
                rgb_gamma_str = f"({rgb_gamma[0]:.4f}, {rgb_gamma[1]:.4f}, {rgb_gamma[2]:.4f})"
            
            rgb_gamma_item = QTableWidgetItem(rgb_gamma_str)
            rgb_gamma_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.ui.table_results.setItem(row_position, 5, rgb_gamma_item)
        
        # 调整表格列宽
        self.adjust_table_columns()
        
        print("Table updated successfully")
    
    def open_export_dialog(self):
        """打开导出对话框"""
        if not self.data['results']:
            QMessageBox.warning(self, "Warning", "No data to export.")
            return
        
        dialog = ExportDialog(self.data, self.settings, self)
        # 直接执行对话框
        dialog.exec()
        # 对话框内部处理导出逻辑
    
    def open_plot_dialog(self):
        """打开图表导出对话框"""
        # 检查是否有可以导出的数据
        if not hasattr(self, 'reflectance_figure') or not hasattr(self, 'cie_figure'):
            QMessageBox.warning(self, "Warning", "No charts available.")
            return
        
        # 创建并显示图表导出对话框
        dialog = PlotDialog(self.data, self.settings, self)
        dialog.exec()
    
    def open_settings_dialog(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self, self.settings)
        if dialog.exec():
            # 如果用户点击了"确定"，则更新设置（但保留那些不在对话框中的设置）
            new_settings = dialog.get_settings()
            
            # 更新现有设置而不是完全替换
            for category in new_settings:
                if category in self.settings:
                    self.settings[category].update(new_settings[category])
                else:
                    self.settings[category] = new_settings[category]
            
            # 保存设置
            self.save_settings()
            # 应用设置
            self.apply_settings()
            # 如果有必要，重新计算结果
            self.recalculate_results()
    
    def apply_settings(self):
        """应用设置"""
        # 应用光源设置
        illuminant = self.settings['general']['illuminant']
        self.color_calculator.set_illuminant(illuminant)
        
        # 应用rho_lambda设置
        rho_lambda = self.settings['general']['rho_lambda']
        self.color_calculator.set_rho_lambda(rho_lambda)
        print(f"应用rho_lambda设置: {rho_lambda}")
        
        # 更新菜单选中状态
        if hasattr(self, 'illuminant_actions'):
            for name, action in self.illuminant_actions.items():
                action.setChecked(name == illuminant)
        
        # 应用Gamut设置
        gamut = self.settings['general']['gamut']
        if hasattr(self, 'gamut_actions'):
            for name, action in self.gamut_actions.items():
                action.setChecked(name == gamut)
        
        # 无论是否有数据，都立即更新反射率图表和CIE图表，应用新的标题和显示设置
        if hasattr(self, 'reflectance_canvas'):
            print("立即更新反射率图表应用新设置...")
            
            # 先保存当前大小
            if hasattr(self, 'reflectance_figure'):
                orig_size = self.reflectance_figure.get_size_inches()
                
            # 更新图表
            self.update_reflectance_plot()
            
            # 确保布局自适应（对于标题显示/隐藏特别重要）
            if hasattr(self, 'reflectance_figure'):
                # 应用tight_layout以确保所有元素可见且布局良好
                self.reflectance_figure.tight_layout(pad=0.4)
                # 重置到原始大小以防止尺寸漂移
                if 'orig_size' in locals():
                    self.reflectance_figure.set_size_inches(orig_size)
                # 强制完全重绘
                self.reflectance_canvas.draw()
            
        # 更新CIE图表显示，确保光源点显示正确
        if hasattr(self, 'cie_canvas'):
            self.update_cie_plot()
            
        # 如果扩展CIE图表窗口打开，也更新它
        if hasattr(self, 'cie_dialog') and self.cie_dialog is not None and self.cie_dialog.isVisible():
            print("更新扩展CIE图表应用新设置...")
            self.update_expanded_cie_plot()
        
        # 检查是否已经有计算结果，如果有且不需要重新计算，则直接更新表格
        if self.data['results'] and self.settings['general'].get('rgb_values') is not None:
            # 如果只是RGB格式改变，不需要重新计算，只需要更新表格
            self.update_results_table()
        
        # 仅当有原始数据且设置变化需要重新计算时，才重新计算
        if self.data['raw_measurements'] and (illuminant != self.color_calculator.illuminant or 
                                             rho_lambda != self.color_calculator.rho_lambda):
            print("设置变化需要重新计算颜色值...")
            self.recalculate_results()
        else:
            print("无需重新计算数据")
    
    def recalculate_results(self):
        """重新计算所有结果，使用原始测量数据"""
        if not self.data['raw_measurements']:
            print("没有原始测量数据，无法重新计算")
            return
        
        # 清空当前结果
        self.data['results'] = []
        
        # 确保重新设置校准模式（如果之前使用了校准）
        if 'black_reference' in self.data and 'white_reference' in self.data:
            black_ref = self.data['black_reference']
            white_ref = self.data['white_reference']
            self.color_calculator.set_calibration_mode(True, black_ref['values'], white_ref['values'])
            print("重新设置校准模式")
        
        # 重新计算每个数据集
        for file_name, raw_data in self.data['raw_measurements'].items():
            # 从原始测量数据中获取波长和测量值
            wavelengths = raw_data['wavelengths']
            values = raw_data['values']
            
            print(f"使用原始测量数据重新计算'{file_name}': 波长范围={wavelengths[0]}-{wavelengths[-1]}nm, "
                  f"点数={len(wavelengths)}, 步长={wavelengths[1]-wavelengths[0]}nm")
            
            # 计算颜色参数
            result = self.color_calculator.process_measurement(values, wavelengths)
            
            # 更新存储的反射率数据
            self.data['reflectance'][file_name] = result
            
            # 存储结果
            self.data['results'].append({
                'file_name': file_name,
                'x': result['xy'][0],
                'y': result['xy'][1],
                'rgb_linear': result['rgb_linear'],
                'rgb_gamma': result['rgb_gamma'],
                'hex_color': result['hex_color']
            })
        
        # 更新界面
        self.update_reflectance_plot()
        self.update_cie_plot()
        self.update_results_table()
        
        # 更新扩展CIE图表窗口（如果已打开）
        if self.cie_dialog is not None and self.cie_dialog.isVisible():
            print("重新计算后更新扩展CIE图表窗口...")
            self.update_expanded_cie_plot()
        
        print(f"成功重新计算 {len(self.data['results'])} 个结果")
    
    def open_about_dialog(self):
        """打开关于对话框"""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def open_manual(self):
        """打开使用手册"""
        QMessageBox.information(self, "Manual", "User manual not available yet.")
    
    def change_illuminant(self):
        """更改光源设置"""
        action = self.sender()
        if not action.isChecked():
            # 防止取消选中
            action.setChecked(True)
            return
        
        # 获取选中的光源
        illuminant = action.data()
        
        # 更新其他光源选项的选中状态
        for name, act in self.illuminant_actions.items():
            if name != illuminant:
                act.setChecked(False)
        
        # 更新设置
        self.settings['general']['illuminant'] = illuminant
        self.color_calculator.set_illuminant(illuminant)
        
        # 更新CIE图表显示，确保光源点显示正确
        self.update_cie_plot()
        
        # 重新计算并更新显示
        self.recalculate_results()
        
        print(f"已切换光源为: {illuminant}")
    
    def change_gamut(self):
        """更改Gamut设置"""
        action = self.sender()
        if not action.isChecked():
            # 防止取消选中
            action.setChecked(True)
            return
        
        # 获取选中的Gamut
        gamut = action.data()
        
        # 更新其他Gamut选项的选中状态
        for name, act in self.gamut_actions.items():
            if name != gamut:
                act.setChecked(False)
        
        # 更新设置
        self.settings['general']['gamut'] = gamut
        
        # 目前不需要重新计算，但可能需要更新显示
        self.update_cie_plot()
        
        # 如果扩展CIE图表窗口打开，也更新它
        if self.cie_dialog is not None and self.cie_dialog.isVisible():
            self.update_expanded_cie_plot()
    
    def copy_all_data(self):
        """复制所有数据到剪贴板"""
        if not self.data['results']:
            QMessageBox.warning(self, "Warning", "No data to copy.")
            return
        
        # 获取RGB值格式设置
        rgb_format = self.settings['general']['rgb_values']
        
        # 构建表格数据字符串
        text = "File Name\tx\ty\tsRGB linear\tsRGB gamma\tHex Color\n"
        
        for result in self.data['results']:
            rgb_linear = result['rgb_linear']
            rgb_gamma = result['rgb_gamma']
            
            # 根据设置格式化RGB Gamma值
            if rgb_format == '0 ... 255':
                # 格式化为0-255范围
                r_gamma = rgb_gamma[0] * 255
                g_gamma = rgb_gamma[1] * 255
                b_gamma = rgb_gamma[2] * 255
                rgb_gamma_str = f"({int(r_gamma) if r_gamma <= 255 else 255}, {int(g_gamma) if g_gamma <= 255 else 255}, {int(b_gamma) if b_gamma <= 255 else 255})"
            else:  # '0 ... 1'
                # 保持0-1范围
                rgb_gamma_str = f"({rgb_gamma[0]:.4f}, {rgb_gamma[1]:.4f}, {rgb_gamma[2]:.4f})"
            
            row = [
                result['file_name'],
                f"{result['x']:.6f}",
                f"{result['y']:.6f}",
                f"({rgb_linear[0]:.4f}, {rgb_linear[1]:.4f}, {rgb_linear[2]:.4f})",
                rgb_gamma_str,
                result['hex_color']
            ]
            
            text += "\t".join(row) + "\n"
        
        # 复制到剪贴板
        QApplication.clipboard().setText(text)
        
        # 显示提示
        QMessageBox.information(self, "Copy", "Data copied to clipboard.")
    
    def copy_table_data(self):
        """复制表格数据到剪贴板，不包括颜色列"""
        if self.ui.table_results.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "No data to copy.")
            return
        
        # 构建表格数据字符串
        text = ""
        
        # 添加表头，跳过颜色列
        headers = []
        for col in range(1, self.ui.table_results.columnCount()):
            headers.append(self.ui.table_results.horizontalHeaderItem(col).text())
        text += "\t".join(headers) + "\n"
        
        # 添加数据行，跳过颜色列
        for row in range(self.ui.table_results.rowCount()):
            row_data = []
            for col in range(1, self.ui.table_results.columnCount()):
                item = self.ui.table_results.item(row, col)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            text += "\t".join(row_data) + "\n"
        
        # 复制到剪贴板
        QApplication.clipboard().setText(text)
        
        # 显示提示
        QMessageBox.information(self, "Copy", "Table data copied to clipboard (excluding color column).")
    
    def clear_data(self):
        """Clear all data"""
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Clear",  # Window title
            "Are you sure you want to clear all data? This action cannot be undone.",  # Message
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,  # Button options
            QMessageBox.StandardButton.No  # Default button
        )

        if reply == QMessageBox.StandardButton.Yes:
            print("User confirmed clearing data")
            self.reset_data()
            self.update_reflectance_plot()
            self.update_cie_plot()
            self.ui.table_results.setRowCount(0)
            self.update_menu_state(False)  # Disable Export and Plot
            
            # 如果反射率数据对话框打开，关闭它
            if self.reflectance_dialog is not None and self.reflectance_dialog.isVisible():
                self.reflectance_dialog.close()
                self.reflectance_dialog = None
            
            # 如果CIE图表窗口打开，关闭它
            if self.cie_dialog is not None and self.cie_dialog.isVisible():
                self.cie_dialog.close()
                self.cie_dialog = None
                
            QMessageBox.information(self, "Data Cleared", "All data has been successfully cleared.")  # Success message
        else:
            print("User cancelled clearing data")
    
    def show_reflectance_data(self):
        """显示反射率数据"""
        if not self.data['reflectance']:
            QMessageBox.warning(self, "Warning", "No reflectance data to show.")
            return
        
        # 优先使用原始波长数据（通常是1nm间隔）
        wavelengths = self.data['original_wavelengths'] if self.data['original_wavelengths'] is not None else self.data['wavelengths']
        
        # 打印波长信息
        if len(wavelengths) > 1:
            print(f"显示反射率数据使用波长: 范围={wavelengths[0]:.1f}-{wavelengths[-1]:.1f}nm, "
                  f"点数={len(wavelengths)}, 步长={wavelengths[1]-wavelengths[0]:.1f}nm")
        
        # 创建数据集字典
        datasets = {}
        for name, reflectance_data in self.data['reflectance'].items():
            print(f"处理数据集 '{name}'...")
            
            # 检查数据格式，以适应新旧两种结构
            if isinstance(reflectance_data, dict):
                # 新格式：字典结构
                # 优先使用1nm步长的数据(reflectance_1nm)用于显示
                if 'reflectance_1nm' in reflectance_data and len(reflectance_data['reflectance_1nm']) > 0:
                    reflectance = reflectance_data['reflectance_1nm']
                    wavelen = reflectance_data['wavelengths_1nm'] if 'wavelengths_1nm' in reflectance_data else wavelengths
                    print(f"使用1nm步长数据显示: {len(reflectance)}点")
                # 其次使用原始反射率数据
                elif 'reflectance' in reflectance_data:
                    reflectance = reflectance_data['reflectance']
                    wavelen = reflectance_data['wavelengths'] if 'wavelengths' in reflectance_data else wavelengths
                    print(f"使用原始反射率数据显示: {len(reflectance)}点")
                else:
                    print(f"警告: 数据集'{name}'格式无效，跳过")
                    continue
            else:
                # 旧格式：直接是数据数组
                reflectance = reflectance_data
                wavelen = wavelengths
                print(f"使用旧格式数据显示: {len(reflectance)}点")
            
            # 检查长度匹配
            if len(wavelen) != len(reflectance):
                print(f"警告: 波长和反射率长度不匹配: 波长={len(wavelen)}, 反射率={len(reflectance)}")
                
                # 如果wavelen不是我们需要的波长，需要重采样
                if np.array_equal(wavelen, wavelengths):
                    print("波长数组匹配，但数据长度不一致，可能数据已损坏")
                    datasets[name] = reflectance  # 直接使用数据，可能显示不正确
                else:
                    print("波长数组不匹配，尝试重采样...")
                    try:
                        # 使用提供的波长和目标波长进行插值
                        interp_func = interp.interp1d(
                            wavelen, 
                            reflectance, 
                            bounds_error=False, 
                            fill_value="extrapolate"
                        )
                        
                        # 重采样反射率数据以匹配目标波长数组
                        resampled_reflectance = interp_func(wavelengths)
                        datasets[name] = resampled_reflectance
                        print(f"重采样完成: {len(reflectance)} -> {len(resampled_reflectance)} 点")
                    except Exception as e:
                        print(f"重采样失败: {str(e)}")
                        # 如果重采样失败，创建与目标波长长度相同的零数组
                        datasets[name] = np.zeros_like(wavelengths)
                        print("创建了零填充数组作为替代")
            else:
                # 长度匹配，直接使用
                datasets[name] = reflectance
                print(f"数据长度匹配，直接使用: {len(reflectance)}点")
        
        if not datasets:
            QMessageBox.warning(self, "Warning", "No valid reflectance data to show.")
            return
        
        # 检查对话框是否已经存在
        if self.reflectance_dialog is None or not self.reflectance_dialog.isVisible():
            # 创建新对话框
            self.reflectance_dialog = ReflectanceDataDialog(wavelengths, datasets, self)
            # 使用show()而不是exec()，使对话框非模态
            self.reflectance_dialog.show()
        else:
            # 更新现有对话框数据
            self.reflectance_dialog.update_data(wavelengths, datasets)
    
    def on_window_resize(self, event):
        """窗口大小改变时调整表格列宽"""
        # 调用父类的resizeEvent
        super().resizeEvent(event)
        
        # 重新调整表格列宽
        self.adjust_table_columns()
    
    def adjust_table_columns(self):
        """调整表格列宽以适应内容和窗口大小"""
        if not hasattr(self.ui, 'table_results') or self.ui.table_results.columnCount() == 0:
            return
        
        # 获取表格的总宽度
        table_width = self.ui.table_results.width()
        
        # 获取表头
        header = self.ui.table_results.horizontalHeader()
        
        # 颜色列宽度
        color_width = 25  # 减小颜色列宽度
        
        # 首先计算文件名列所需的实际宽度（基于内容）
        max_filename_width = 0
        filename_padding = 15  # 减小文件名周围的padding
        
        # 获取字体度量来计算文本宽度
        font_metrics = self.ui.table_results.fontMetrics()
        
        # 计算表头的宽度
        header_text = self.ui.table_results.horizontalHeaderItem(1).text()
        header_width = font_metrics.horizontalAdvance(header_text) + filename_padding
        
        # 计算所有文件名的最大宽度
        for row in range(self.ui.table_results.rowCount()):
            item = self.ui.table_results.item(row, 1)
            if item is not None:
                text_width = font_metrics.horizontalAdvance(item.text()) + filename_padding
                max_filename_width = max(max_filename_width, text_width)
        
        # 取表头和内容的最大宽度
        filename_width = max(max_filename_width, header_width, 80)  # 至少80像素
                
        # 计算其他列所需的固定空间
        fixed_width = color_width
        for col in [2, 3, 4, 5]:  # x, y, sRGB Linear, sRGB Gamma列
            if col == 2 or col == 3:  # x和y列
                width = max(60, header.sectionSize(col))  # 确保x和y列至少60像素
            else:  # RGB列
                width = max(120, header.sectionSize(col))  # 至少120像素
            fixed_width += width
        
        # 检查文件名列的宽度是否会超出可用空间
        available_width = table_width - fixed_width - 5  # 减5像素作为缓冲
        if filename_width > available_width and available_width >= 80:
            # 如果超出可用空间但可用空间足够显示基本内容，则使用可用空间
            filename_width = available_width
        
        # 设置颜色列宽度，允许自适应
        color_section_size = header.sectionSize(0)
        if color_section_size > color_width:
            # 如果用户调整了宽度，使用用户设置的宽度
            self.ui.table_results.setColumnWidth(0, color_section_size)
        else:
            # 否则使用默认宽度
            self.ui.table_results.setColumnWidth(0, color_width)
        
        # 设置文件名列宽度
        self.ui.table_results.setColumnWidth(1, filename_width)
        
        # 设置其他列的宽度
        self.ui.table_results.setColumnWidth(2, max(60, header.sectionSize(2)))  # x列
        self.ui.table_results.setColumnWidth(3, max(60, header.sectionSize(3)))  # y列
        self.ui.table_results.setColumnWidth(4, max(120, header.sectionSize(4)))  # sRGB Linear列
        self.ui.table_results.setColumnWidth(5, max(120, header.sectionSize(5)))  # sRGB Gamma列

    def update_menu_state(self, has_data):
        """更新菜单状态"""
        if hasattr(self, 'ui'):
            self.ui.actionExport.setEnabled(has_data)
            self.ui.actionPlot.setEnabled(has_data)

    def show_cie_data(self):
        """显示CIE色度图的放大视图，而不是数据表格"""
        # 不再检查是否有数据，直接显示CIE图表
        
        # 检查对话框是否已存在
        if self.cie_dialog is None or not self.cie_dialog.isVisible():
            # 创建一个新的对话框窗口
            self.cie_dialog = QDialog(self)
            self.cie_dialog.setWindowTitle("CIE Chromaticity Diagram")
            self.cie_dialog.resize(900, 900)  # 增大尺寸从600x600到900x900
            
            # 获取父窗口的位置和大小
            parent_geometry = self.geometry()
            parent_x = parent_geometry.x()
            parent_y = parent_geometry.y()
            parent_width = parent_geometry.width()
            
            # 将窗口放在主窗口右侧
            self.cie_dialog.setGeometry(parent_x + parent_width + 10, parent_y, 900, 900)  # 更新尺寸
            
            # 创建布局
            layout = QVBoxLayout(self.cie_dialog)
            
            # 创建图形和画布 - 增大尺寸
            self.cie_expanded_figure = Figure(figsize=(10, 10), dpi=100)  # 增大从8x8到10x10
            self.cie_expanded_canvas = FigureCanvas(self.cie_expanded_figure)
            
            # 添加画布到布局
            layout.addWidget(self.cie_expanded_canvas)
            
            # 更新CIE图表
            self.update_expanded_cie_plot()
            
            # 显示非模态对话框
            self.cie_dialog.show()
        else:
            # 如果对话框已经存在，更新图表
            self.update_expanded_cie_plot()
            # 确保窗口可见
            self.cie_dialog.show()
            self.cie_dialog.raise_()
    
    def update_expanded_cie_plot(self):
        """更新放大版CIE图表"""
        if not hasattr(self, 'cie_expanded_figure') or not hasattr(self, 'cie_expanded_canvas'):
            return
            
        # 清除图表
        self.cie_expanded_figure.clear()
        
        # 创建子图
        ax = self.cie_expanded_figure.add_subplot(111)
        
        # 设置字体大小 - 调整为适应高分辨率
        title_size = 12
        label_size = 10
        tick_size = 9
        wavelength_label_size = 8
        annotation_size = 8
        legend_size = 9
        
        # 使用与主窗口相同的绘图逻辑，但调整部分参数使其更清晰
        try:
            # 禁用警告消息
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # 首先绘制色度图的彩色背景
                plot_chromaticity_diagram_colours(
                    axes=ax,
                    diagram_colours="RGB",  # 使用RGB颜色
                    method="CIE 1931",  # 使用CIE 1931方法
                    standalone=False,  # 不独立绘图
                    title=False,  # 不使用默认标题
                    bounding_box=(0, 0.8, 0, 0.9)  # 恢复原始设置
                )
                
                # 获取光谱轨迹线的数据点
                cmfs = colour.colorimetry.MSDS_CMFS['CIE 1931 2 Degree Standard Observer']
                XYZ = cmfs.values
                xy = colour.XYZ_to_xy(XYZ)
                wavelengths = cmfs.wavelengths
                
                # 创建波长到坐标的映射
                wavelength_dict = {wl: (x, y) for wl, (x, y) in zip(wavelengths, xy)}
                
                # 定义我们想要标记的波长范围（460-620nm，每20nm一个标记）
                custom_wavelength_labels = list(range(460, 640, 20))
                
                # 创建平滑的边界线
                from scipy.interpolate import interp1d
                
                # 光谱轨迹线
                x_locus = np.append(xy[..., 0], xy[0, 0])
                y_locus = np.append(xy[..., 1], xy[0, 1])
                
                # 创建参数化的坐标
                t = np.linspace(0, 1, len(x_locus))
                
                # 创建插值函数
                fx = interp1d(t, x_locus, kind='cubic')
                fy = interp1d(t, y_locus, kind='cubic')
                
                # 生成更密集的点
                t_new = np.linspace(0, 1, 1000)
                x_smooth = fx(t_new)
                y_smooth = fy(t_new)
                
                # 绘制光谱边界线
                ax.plot(
                    x_smooth, 
                    y_smooth, 
                    color='black', 
                    linewidth=1.2,  # 稍微加粗
                    solid_capstyle='round',
                    zorder=10
                )
                
                # 紫色线
                purple_line = np.vstack([
                    [xy[-1, 0], xy[-1, 1]],
                    [xy[0, 0], xy[0, 1]]
                ])
                
                # 绘制紫色线
                ax.plot(
                    purple_line[:, 0], 
                    purple_line[:, 1], 
                    color='black', 
                    linewidth=1.2,  # 稍微加粗
                    linestyle='--',
                    zorder=10
                )
                
                # 绘制色域
                gamut = self.settings['general']['gamut']
                
                # 根据选择的色域定义相应顶点
                if gamut == 'None':
                    pass
                elif gamut == 'sRGB':
                    r = (0.64, 0.33)
                    g = (0.30, 0.60)
                    b = (0.15, 0.06)
                elif gamut == 'Adobe RGB':
                    r = (0.64, 0.33)
                    g = (0.21, 0.71)
                    b = (0.15, 0.06)
                elif gamut == 'HTC VIVE Pro Eye':
                    r = (0.6585, 0.3407)
                    g = (0.2326, 0.7119)
                    b = (0.1431, 0.0428)
                elif gamut == 'Meta Oculus Quest 1':
                    r = (0.6596, 0.3396)
                    g = (0.2395, 0.7069)
                    b = (0.1452, 0.0531)
                elif gamut == 'Meta Oculus Quest 2':
                    r = (0.6364, 0.3305)
                    g = (0.3032, 0.5938)
                    b = (0.1536, 0.0632)
                elif gamut == 'Meta Oculus Rift':
                    r = (0.6690, 0.3300)
                    g = (0.2545, 0.7015)
                    b = (0.1396, 0.0519)
                else:
                    # 默认使用sRGB
                    r = (0.64, 0.33)
                    g = (0.30, 0.60)
                    b = (0.15, 0.06)
                
                # 绘制色域多边形
                if gamut != 'None':
                    x_points = [r[0], g[0], b[0], r[0]]
                    y_points = [r[1], g[1], b[1], r[1]]
                    
                    ax.plot(x_points, y_points, '-', color='black', linewidth=1.2, 
                           zorder=30, label=gamut)
                
                # 绘制光源点
                illuminant = self.settings['general']['illuminant']
                
                # 常见光源坐标
                illuminant_coords = {
                    'D65': (0.3128, 0.3290),
                    'D50': (0.3457, 0.3585),
                    'A': (0.4476, 0.4074),
                    'E': (1/3, 1/3)
                }
                
                # 绘制当前光源点
                if illuminant in illuminant_coords:
                    x_illum, y_illum = illuminant_coords[illuminant]
                    
                    ax.plot(x_illum, y_illum, 'o', color='black', markersize=6, 
                           markerfacecolor='none', markeredgewidth=1.2, zorder=50)
                    
                    # 添加光源标注
                    ax.annotate(
                        f"{illuminant}",
                        (x_illum + 0.02, y_illum + 0.02),
                        fontsize=annotation_size,
                        color='black',
                        ha='left',
                        va='bottom',
                        zorder=50
                    )
                
                # 添加波长标记
                for wl in custom_wavelength_labels:
                    if wl in wavelength_dict:
                        x, y = wavelength_dict[wl]
                        
                        # 计算偏移方向
                        center = np.array([1/3, 1/3])
                        point = np.array([x, y])
                        direction = point - center
                        
                        # 标准化方向向量
                        direction = direction / np.linalg.norm(direction)
                        
                        # 调整特定波长的偏移
                        if wl == 460:
                            offset = np.array([-0.02, 0.02])
                        elif wl == 540:
                            offset = np.array([0.07, 0.03])
                        elif wl == 620:
                            offset = np.array([0.03, 0.05])
                        else:
                            offset = direction * 0.015
                        
                        # 绘制波长点
                        ax.plot(x, y, 'o', color='black', markersize=3, zorder=15)
                        
                        # 确定文本对齐方式
                        h_align = 'left' if direction[0] > 0 else 'right'
                        v_align = 'bottom' if direction[1] > 0 else 'top'
                        
                        # 添加波长标签
                        ax.annotate(
                            f"{wl}",
                            (x + offset[0], y + offset[1]),
                            fontsize=wavelength_label_size,
                            color='black',
                            ha=h_align,
                            va=v_align,
                            zorder=15,
                            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.1')
                        )
                        
                # 仅当有数据时绘制数据点
                if self.data['results']:
                    # 绘制数据点 - 使用更大的点以方便在大图上查看
                    for result in self.data['results']:
                        x, y = result['x'], result['y']
                        hex_color = result['hex_color']
                        file_name = result['file_name']
                        # 为大视图增大点的尺寸，使用标签用于图例
                        ax.plot(x, y, 'o', color=hex_color, markersize=8, markeredgecolor='black', 
                              markeredgewidth=1.2, zorder=100, label=file_name)
                
                # 根据设置决定是否显示图例 - 包括测量点和色域
                show_legend = self.settings['plot'].get('cie_show_legend', True)
                if show_legend:
                    # 获取图例对象并设置较小的字体大小
                    legend = ax.legend(fontsize=legend_size, loc='upper right', frameon=True,
                                    bbox_to_anchor=(1.0, 1.0))
                    if legend is not None:
                        # 设置图例框属性
                        legend.set_frame_on(True)
                        legend.set_title('')  # 移除图例标题
                        # 调整图例大小
                        legend._legend_box.align = "right"
                else:
                    # 如果设置为不显示图例，则移除任何现有的图例
                    legend = ax.get_legend()
                    if legend is not None:
                        legend.remove()
                
        except Exception as e:
            print(f"Error drawing expanded CIE chart: {e}")
            # 回退到简化版绘图
            self.draw_simplified_cie_boundary(ax)
        
        # 设置标题和轴标签 - 从settings获取标题设置
        show_title = self.settings['plot'].get('cie_show_title', True)
        title_text = self.settings['plot'].get('cie_title', "CIE 1931 Chromaticity Diagram")
        
        if show_title:
            ax.set_title(title_text, fontsize=title_size)
        
        ax.set_xlabel("x", fontsize=label_size)
        ax.set_ylabel("y", fontsize=label_size)
        
        # 设置轴范围
        ax.set_xlim(0, 0.8)
        ax.set_ylim(0, 0.9)
        
        # 设置刻度
        ax.set_xticks(np.arange(0, 0.9, 0.1))
        ax.tick_params(axis='x', which='major', labelsize=tick_size)
        
        ax.set_yticks(np.arange(0, 1.0, 0.1))
        ax.tick_params(axis='y', which='major', labelsize=tick_size)
        
        # 禁用网格
        ax.grid(False)
        
        # 调整布局
        self.cie_expanded_figure.tight_layout()
        
        # 更新画布
        self.cie_expanded_canvas.draw()
    
    def draw_simplified_cie_boundary(self, ax):
        """为扩展CIE图表绘制简化版边界（备用方法）"""
        # 使用简化的CIE边界点
        boundary_x = [0.1740, 0.0000, 0.0000, 0.0332, 0.0648, 0.0919, 0.1390, 0.1738, 0.2080, 0.2586, 0.3230, 0.3962, 0.4400, 0.4699, 0.4999, 0.5140, 0.5295, 0.5482, 0.5651, 0.5780, 0.5832, 0.5800, 0.5672, 0.5314, 0.4649, 0.3652, 0.2615, 0.1740]
        boundary_y = [0.0049, 0.0000, 0.0100, 0.0380, 0.0650, 0.0910, 0.2080, 0.2737, 0.3344, 0.4077, 0.4964, 0.5574, 0.5800, 0.5888, 0.5991, 0.6039, 0.6089, 0.6128, 0.6150, 0.6160, 0.6160, 0.6155, 0.6123, 0.6030, 0.5657, 0.4679, 0.2624, 0.0049]
        
        # 绘制边界
        ax.plot(boundary_x, boundary_y, 'k-', linewidth=1.5)
        
        # 填充范围
        ax.fill(boundary_x, boundary_y, alpha=0.1, color='gray')
        
        # 绘制光源
        illuminant = self.settings['general']['illuminant']
        # 常见光源坐标
        illuminant_coords = {
            'D65': (0.3128, 0.3290),
            'D50': (0.3457, 0.3585),
            'A': (0.4476, 0.4074),
            'E': (1/3, 1/3)
        }
        
        if illuminant in illuminant_coords:
            x_illum, y_illum = illuminant_coords[illuminant]
            ax.plot(x_illum, y_illum, 'o', color='black', markersize=6, 
                   markerfacecolor='none', markeredgewidth=1.2, zorder=50)
        
        # 绘制色域（如果有）
        gamut = self.settings['general']['gamut']
        if gamut != 'None':
            # 根据选择的色域定义相应顶点
            if gamut == 'sRGB':
                r = (0.64, 0.33)
                g = (0.30, 0.60)
                b = (0.15, 0.06)
            elif gamut == 'Adobe RGB':
                r = (0.64, 0.33)
                g = (0.21, 0.71)
                b = (0.15, 0.06)
            elif gamut == 'HTC VIVE Pro Eye':
                r = (0.6585, 0.3407)
                g = (0.2326, 0.7119)
                b = (0.1431, 0.0428)
            elif gamut == 'Meta Oculus Quest 1':
                r = (0.6596, 0.3396)
                g = (0.2395, 0.7069)
                b = (0.1452, 0.0531)
            elif gamut == 'Meta Oculus Quest 2':
                r = (0.6364, 0.3305)
                g = (0.3032, 0.5938)
                b = (0.1536, 0.0632)
            elif gamut == 'Meta Oculus Rift':
                r = (0.6690, 0.3300)
                g = (0.2545, 0.7015)
                b = (0.1396, 0.0519)
            else:
                # 默认使用sRGB
                r = (0.64, 0.33)
                g = (0.30, 0.60)
                b = (0.15, 0.06)
                
            # 创建闭合多边形的点列表
            x_points = [r[0], g[0], b[0], r[0]]
            y_points = [r[1], g[1], b[1], r[1]]
            
            # 绘制色域边界，并添加标签
            ax.plot(x_points, y_points, 'k-', linewidth=1.5, label=gamut)
        
        # 绘制数据点 - 使用标签而不是直接标注
        for result in self.data['results']:
            x, y = result['x'], result['y']
            hex_color = result['hex_color']
            file_name = result['file_name']
            ax.plot(x, y, 'o', color=hex_color, markersize=8, markeredgecolor='black', 
                   markeredgewidth=1.2, zorder=100, label=file_name)
        
        # 根据设置决定是否显示图例
        show_legend = self.settings['plot'].get('cie_show_legend', True)
        if show_legend:
            # 添加图例
            legend = ax.legend(fontsize=8, loc='upper right', frameon=True)
            if legend is not None:
                legend.set_frame_on(True)
                legend.set_title('')
        else:
            # 不显示图例
            legend = ax.get_legend()
            if legend is not None:
                legend.remove()
                
        # 设置标题（从settings中获取设置）
        show_title = self.settings['plot'].get('cie_show_title', True)
        title_text = self.settings['plot'].get('cie_title', "CIE 1931 Chromaticity Diagram")
        
        if show_title:
            ax.set_title(title_text, fontsize=12)
    
    def resizeEvent(self, event):
        """处理窗口尺寸变化事件，调整UI元素"""
        super().resizeEvent(event)
        self.adjust_table_columns()
        
        # 刷新图表
        if hasattr(self, 'reflectance_canvas'):
            self.reflectance_canvas.draw()
        if hasattr(self, 'cie_canvas'):
            self.cie_canvas.draw()
        
        # 触发窗口大小变化事件
        if hasattr(self, 'reflectance_canvas') or hasattr(self, 'cie_canvas'):
            self.on_window_resize(event)
    
    def closeEvent(self, event):
        """
        处理程序关闭事件，确保保存所有用户设置
        """
        # 保存当前的所有设置到配置文件
        self.save_settings()
        
        # 调用父类的closeEvent处理默认关闭行为
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())