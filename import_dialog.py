import sys
import os
import pandas as pd
import numpy as np
from PySide6.QtWidgets import (
    QDialog, QFileDialog, QMessageBox, QVBoxLayout, 
    QCheckBox, QHBoxLayout, QPushButton, QWidget, QListView
)
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtGui import QStandardItemModel, QStandardItem
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar,
    FigureCanvasQTAgg as FigureCanvas,
)
from matplotlib.figure import Figure
from ui_Import import Ui_Dialog_import


class ImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog_import()
        self.ui.setupUi(self)
        
        # 设置窗口标题
        self.setWindowTitle("Import Data")

        # 初始化数据存储
        self.black_reference_path = None
        self.white_reference_path = None
        self.black_reference_data = None
        self.white_reference_data = None
        self.measurement_files = []
        self.selected_measurements = []
        
        # 初始化数据模型
        self.file_model = QStandardItemModel()
        self.ui.listView_import_file.setModel(self.file_model)

        # 初始化 matplotlib 画布 - 设置更合适的图表尺寸
        self.figure = Figure(figsize=(5, 3.8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        # 移除顶部工具栏（menubar）
        # self.toolbar = NavigationToolbar(self.canvas, self)
        
        # 给view_spec添加内边距，使画布稍微缩小
        self.ui.view_spec.setContentsMargins(8, 8, 8, 8)
        
        # 创建布局，清除默认边距
        layout = QVBoxLayout(self.ui.view_spec)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # 不再添加工具栏
        # layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # 配置图表的初始布局 - 进一步增加底部边距
        self.figure.subplots_adjust(left=0.18, right=0.92, bottom=0.22, top=0.92)
        
        # 初始化一个空图表，确保坐标轴标签显示
        self.initialize_empty_plot()
        
        # 添加选择/取消选择所有按钮
        self.select_buttons_layout = QHBoxLayout()
        self.select_all_button = QPushButton("Select All")
        self.deselect_all_button = QPushButton("Deselect All")
        self.select_buttons_layout.addWidget(self.select_all_button)
        self.select_buttons_layout.addWidget(self.deselect_all_button)
        
        # 创建一个容器来放置这些按钮
        self.select_buttons_widget = QWidget()
        self.select_buttons_widget.setLayout(self.select_buttons_layout)
        
        # 将按钮添加到网格布局中
        self.ui.gridLayout_3.addWidget(self.select_buttons_widget, 11, 1, 1, 1)
        
        # 重命名OK按钮为Import Selected Data
        self.ui.buttonBox_import.button(self.ui.buttonBox_import.StandardButton.Ok).setText("Import Selected Data")

        # 初始化按钮状态
        self.update_buttons_state()

        # 绑定交互事件
        self.ui.comboBox_equp.currentIndexChanged.connect(self.update_buttons_state)
        self.ui.pushButton_black.clicked.connect(self.select_black_reference)
        self.ui.pushButton_white.clicked.connect(self.select_white_reference)
        self.ui.pushButton_clear_ref.clicked.connect(self.clear_reference)
        self.ui.pushButton_select_data.clicked.connect(self.select_measurements)
        self.select_all_button.clicked.connect(self.select_all_items)
        self.deselect_all_button.clicked.connect(self.deselect_all_items)
        
        # 连接对话框按钮
        self.ui.buttonBox_import.accepted.connect(self.accept)
        self.ui.buttonBox_import.rejected.connect(self.reject)
        
        # 初始显示空图
        self.update_preview()

    def initialize_empty_plot(self):
        """初始化一个空的图表，显示坐标轴和标签"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # 设置标签 - 与update_preview保持一致
        ax.set_xlabel("Wavelength [nm]", fontsize=6)
        ax.set_ylabel("Spectral Irradiance [W/sqm*nm]", fontsize=6)
        ax.tick_params(axis='both', which='major', labelsize=5)
        
        # 设置范围
        ax.set_xlim(380, 780)
        ax.set_ylim(0, 1.0)
        
        # 添加网格
        ax.grid(True, linestyle='--', alpha=0.6)
        
        # 确保标签显示
        self.figure.subplots_adjust(left=0.18, right=0.92, bottom=0.22, top=0.92)
        
        # 添加空白数据点，确保图表初始化正常
        ax.plot([380, 780], [0, 0], alpha=0)
        
        # 刷新画布
        self.canvas.draw()

    def update_buttons_state(self):
        """
        根据设备类型动态更新按钮状态。
        """
        selected_equipment = self.ui.comboBox_equp.currentText()
        if selected_equipment == "Aleksameter":
            print("Aleksameter mode selected")
            self.ui.pushButton_black.setEnabled(True)
            self.ui.pushButton_white.setEnabled(True)
            self.ui.pushButton_clear_ref.setEnabled(True)
            # 检查是否已选择参考文件
            self.check_references_selected()
        elif selected_equipment == "Generic":
            print("Generic mode selected")
            self.ui.pushButton_black.setEnabled(False)
            self.ui.pushButton_white.setEnabled(False)
            self.ui.pushButton_clear_ref.setEnabled(False)
            # Generic模式下直接启用测量数据选择按钮
            self.ui.pushButton_select_data.setEnabled(True)
            # 清除参考数据
            self.black_reference_path = None
            self.white_reference_path = None
            # 清除预览图
            self.figure.clear()
            self.canvas.draw()

    def check_references_selected(self):
        """
        检查是否已选择黑白参考文件，如果都已选择则启用测量数据选择按钮
        """
        print(f"Black ref: {self.black_reference_path}, White ref: {self.white_reference_path}")
        if self.ui.comboBox_equp.currentText() == "Aleksameter":
            if self.black_reference_path and self.white_reference_path:
                self.ui.pushButton_select_data.setEnabled(True)
            else:
                self.ui.pushButton_select_data.setEnabled(False)

    def select_black_reference(self):
        """
        选择黑色参考文件。
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Black Reference File", 
            self.get_import_directory(),
            "All Supported Files (*.csv *.txt *.mat);;CSV Files (*.csv);;Text Files (*.txt);;MATLAB Files (*.mat);;All Files (*.*)"
        )
        if file_path:
            print(f"Selected black reference: {file_path}")
            self.black_reference_path = file_path
            
            # 加载数据
            data = self.load_data_file(file_path)
            if data:
                self.black_reference_data = data  # 保存数据以便预览使用
                self.update_preview()  # 更新预览图
                self.check_references_selected()
            
            # 记住目录以便下次使用
            self.save_import_directory(os.path.dirname(file_path))

    def select_white_reference(self):
        """
        选择白色参考文件。
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select White Reference File", 
            self.get_import_directory(),
            "All Supported Files (*.csv *.txt *.mat);;CSV Files (*.csv);;Text Files (*.txt);;MATLAB Files (*.mat);;All Files (*.*)"
        )
        if file_path:
            print(f"Selected white reference: {file_path}")
            self.white_reference_path = file_path
            
            # 加载数据
            data = self.load_data_file(file_path)
            if data:
                self.white_reference_data = data  # 保存数据以便预览使用
                self.update_preview()  # 更新预览图
                self.check_references_selected()
            
            # 记住目录以便下次使用
            self.save_import_directory(os.path.dirname(file_path))

    def clear_reference(self):
        """
        清除参考数据。
        """
        self.black_reference_path = None
        self.white_reference_path = None
        self.black_reference_data = None
        self.white_reference_data = None
        self.update_preview()
        self.check_references_selected()
        QMessageBox.information(self, "Clear", "Reference data cleared.")

    def select_measurements(self):
        """
        选择测量数据文件。
        """
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Measurement Files", 
            self.get_import_directory(),
            "All Supported Files (*.csv *.txt *.mat);;CSV Files (*.csv);;Text Files (*.txt);;MATLAB Files (*.mat);;All Files (*.*)"
        )
        if file_paths:
            print(f"Selected measurements: {file_paths}")
            self.measurement_files = file_paths
            self.populate_file_list()
            self.update_preview()  # 使用统一的预览更新函数
            
            # 记住目录以便下次使用
            if file_paths:
                self.save_import_directory(os.path.dirname(file_paths[0]))

    def populate_file_list(self):
        """
        填充文件列表，并为每个文件添加复选框。
        """
        print(f"Populating file list with {len(self.measurement_files)} files")
        self.file_model.clear()
        for file_path in self.measurement_files:
            file_name = os.path.basename(file_path)
            item = QStandardItem(file_name)
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Checked)  # 默认选中
            item.setData(file_path, Qt.ItemDataRole.UserRole)  # 存储完整路径
            self.file_model.appendRow(item)
        
        # 默认所有文件都被选中
        self.selected_measurements = self.measurement_files.copy()
        
        # 让ListView项目可点击，以允许选择/取消选择
        self.ui.listView_import_file.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self.ui.listView_import_file.clicked.connect(self.on_item_clicked)

    def on_item_clicked(self, index):
        """
        处理列表项目点击事件
        """
        item = self.file_model.itemFromIndex(index)
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)
        
        # 更新预览图
        self.update_preview()

    def update_preview(self):
        """
        更新预览图，显示黑白参考和所选测量数据
        """
        # 清除图表
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # 设置较小的字体大小
        axis_label_size = 6  # 坐标轴标签更小
        tick_label_size = 6  # 刻度标签
        legend_size = 6  # 图例字体
        
        # 跟踪成功绘制的数据集
        plot_count = 0  
        
        # 设置坐标轴标签 - 无论是否有数据都显示
        ax.set_xlabel("Wavelength [nm]", fontsize=axis_label_size)
        ax.set_ylabel("Spectral Irradiance [W/sqm*nm]", fontsize=axis_label_size)
        
        # 确保X轴标签显示，使用与__init__相同的设置
        self.figure.subplots_adjust(left=0.18, right=0.92, bottom=0.22, top=0.92)
        
        # 添加网格线
        ax.grid(True, linestyle='--', alpha=0.6)
        
        # 绘制黑色参考数据
        if self.black_reference_data:
            wavelengths = self.black_reference_data['wavelengths']
            values = self.black_reference_data['values']
            ax.plot(wavelengths, values, 'k-', label="Black Reference", linewidth=1.5)
            plot_count += 1
        
        # 绘制白色参考数据
        if self.white_reference_data:
            wavelengths = self.white_reference_data['wavelengths']
            values = self.white_reference_data['values']
            ax.plot(wavelengths, values, 'r-', label="White Reference", linewidth=1.5)
            plot_count += 1
        
        # 绘制选定的测量数据 (最多显示3个)
        selected_measurements = self.get_selected_measurements()
        preview_count = min(len(selected_measurements), 3)
        
        for i, file_path in enumerate(selected_measurements[:preview_count]):
            try:
                file_name = os.path.basename(file_path)
                data = self.load_data_file(file_path)
                if data and 'wavelengths' in data and 'values' in data:
                    wavelengths = data['wavelengths']
                    values = data['values']
                    
                    if len(wavelengths) == len(values) and len(wavelengths) > 0:
                        ax.plot(wavelengths, values, label=f"Meas: {file_name}", linewidth=1)
                        plot_count += 1
            except Exception as e:
                print(f"Error previewing {file_path}: {e}")
        
        # 添加图例（如果有数据）
        if plot_count > 0:
            ax.legend(loc='best', fontsize=legend_size, framealpha=0.7)
        
        # 设置X轴范围为可见光范围
        ax.set_xlim(380, 780)
        
        # 根据是否有数据设置刻度显示
        if plot_count > 0:
            # 有数据，显示刻度标签
            ax.tick_params(axis='both', which='major', labelsize=tick_label_size)
            
            # Y轴自适应 - 使用自动缩放
            ax.autoscale(axis='y')
            # 确保Y轴下限为0（除非有负值）
            y_min, y_max = ax.get_ylim()
            if y_min >= 0:
                ax.set_ylim(0, y_max)
        else:
            # 无数据，隐藏刻度标签但保留坐标轴
            ax.tick_params(axis='both', which='both', 
                          labelbottom=False, labelleft=False,  # 隐藏刻度数字
                          length=0)  # 隐藏刻度线
            
            # 无数据时使用默认范围
            ax.set_ylim(0, 1.0)
        
        # 刷新画布
        self.canvas.draw()
        
        # 连接尺寸变化事件，确保自适应
        try:
            self.canvas.mpl_disconnect(self._resize_id)
        except:
            pass
        self._resize_id = self.canvas.mpl_connect('resize_event', self._on_resize)

    def load_data_file(self, file_path):
        """
        加载数据文件，根据文件类型进行适当处理。
        """
        try:
            # 根据文件扩展名选择不同的加载方法
            ext = os.path.splitext(file_path)[1].lower()
            
            # 处理CSV文件（专门针对示例中的格式）
            if ext == '.csv':
                print(f"Loading CSV file: {file_path}")
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                # 查找数据部分开始的位置
                data_start_index = -1
                for i, line in enumerate(lines):
                    if line.startswith("Wavelength [nm],"):
                        data_start_index = i + 1
                        break
                
                if data_start_index >= 0:
                    print(f"Found data section starting at line {data_start_index}")
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
                        print(f"Extracted {len(wavelengths)} data points")
                        # 确保使用numpy数组
                        return {
                            'wavelengths': np.array(wavelengths),
                            'values': np.array(values)
                        }
                
                # 如果上述解析失败，尝试常规CSV解析
                try:
                    data = pd.read_csv(file_path)
                    if len(data.columns) >= 2:
                        print(f"Fallback to pandas: {data.shape[0]} rows, {data.shape[1]} columns")
                        # 确保返回numpy数组
                        return {
                            'wavelengths': np.array(data.iloc[:, 0].values),
                            'values': np.array(data.iloc[:, 1].values)
                        }
                except Exception as ex:
                    print(f"Pandas CSV read error: {ex}")
                
                return None
                
            # 处理TXT文件
            elif ext == '.txt':
                print(f"Loading TXT file: {file_path}")
                try:
                    # 尝试使用numpy的loadtxt
                    data = np.loadtxt(file_path)
                    if data.shape[1] >= 2:  # 确保至少有两列
                        return {
                            'wavelengths': np.array(data[:, 0]),
                            'values': np.array(data[:, 1])
                        }
                except Exception as ex:
                    print(f"Numpy loadtxt error: {ex}")
                    
                # 尝试手动解析
                try:
                    wavelengths = []
                    values = []
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            try:
                                # 尝试不同的分隔符
                                if ',' in line:
                                    parts = line.strip().split(',')
                                else:
                                    parts = line.strip().split()
                                
                                if len(parts) >= 2:
                                    wavelength = float(parts[0])
                                    value = float(parts[1])
                                    wavelengths.append(wavelength)
                                    values.append(value)
                            except (ValueError, IndexError):
                                continue
                    
                    if wavelengths and values:
                        return {
                            'wavelengths': np.array(wavelengths),
                            'values': np.array(values)
                        }
                except Exception as ex:
                    print(f"Manual parsing error: {ex}")
                
                return None
                
            # 处理其他类型的文件
            else:
                # 尝试使用pandas读取
                try:
                    data = pd.read_csv(file_path, sep=None, engine='python')
                    if len(data.columns) >= 2:
                        return {
                            'wavelengths': np.array(data.iloc[:, 0].values),
                            'values': np.array(data.iloc[:, 1].values)
                        }
                except Exception as ex:
                    print(f"Unknown file type, pandas read error: {ex}")
                
                return None
                
            return None
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            QMessageBox.warning(self, "Warning", f"Failed to load {file_path}: {e}")
            return None

    def select_all_items(self):
        """
        选择所有项目。
        """
        print("Selecting all items")
        for row in range(self.file_model.rowCount()):
            item = self.file_model.item(row)
            item.setCheckState(Qt.CheckState.Checked)
        
        # 更新预览图
        self.update_preview()
    
    def deselect_all_items(self):
        """
        取消选择所有项目。
        """
        print("Deselecting all items")
        for row in range(self.file_model.rowCount()):
            item = self.file_model.item(row)
            item.setCheckState(Qt.CheckState.Unchecked)
        
        # 更新预览图
        self.update_preview()
    
    def get_selected_measurements(self):
        """获取当前选中的测量文件列表"""
        selected = []
        for row in range(self.file_model.rowCount()):
            item = self.file_model.item(row)
            if item.checkState() == Qt.CheckState.Checked:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                selected.append(file_path)
        return selected
    
    def accept(self):
        """
        确认导入数据。
        """
        # 获取选中的测量文件列表
        selected_measurements = self.get_selected_measurements()
        
        # 检查是否有选中的测量数据
        if not selected_measurements:
            QMessageBox.warning(self, "警告", "未选择任何测量文件。")
            return
        
        # 在Aleksameter模式下检查是否选择了参考文件
        if self.ui.comboBox_equp.currentText() == "Aleksameter" and (not self.black_reference_path or not self.white_reference_path):
            QMessageBox.warning(self, "警告", "在Aleksameter模式下必须选择黑白参考文件。")
            return
        
        print("Import dialog accepting - data will be sent to main window")
        # 调用父类的accept方法关闭对话框并返回Accepted
        super().accept()

    def get_import_directory(self):
        """获取导入目录，有缓存则使用缓存，否则返回默认目录"""
        # 尝试从设置中读取上次的导入目录
        settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_settings.json')
        try:
            if os.path.exists(settings_file):
                import json
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    if 'import' in settings and 'default_directory' in settings['import']:
                        return settings['import']['default_directory']
        except:
            pass
        
        # 默认目录
        return os.path.expanduser('~')
    
    def save_import_directory(self, directory):
        """保存导入目录到设置中"""
        settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_settings.json')
        try:
            settings = {}
            if os.path.exists(settings_file):
                import json
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            
            if 'import' not in settings:
                settings['import'] = {}
            
            settings['import']['default_directory'] = directory
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
        except:
            pass

    def get_selected_data(self):
        """
        获取所有选中的数据。
        """
        # 获取选中的测量文件列表
        selected_measurements = self.get_selected_measurements()
        
        print(f"Selected data mode: {self.ui.comboBox_equp.currentText()}")
        print(f"Black reference: {self.black_reference_path}")
        print(f"White reference: {self.white_reference_path}")
        print(f"Selected measurements: {len(selected_measurements)} files")
        
        selected_data = {
            'mode': self.ui.comboBox_equp.currentText(),
            'black_reference': self.black_reference_path,
            'white_reference': self.white_reference_path,
            'measurements': selected_measurements
        }
        return selected_data

    def _on_resize(self, event):
        """处理图表尺寸变化事件"""
        # 更新为使用相同的底部边距
        self.figure.subplots_adjust(left=0.18, right=0.92, bottom=0.22, top=0.92)
            
        # 重新绘制图表
        self.canvas.draw_idle()