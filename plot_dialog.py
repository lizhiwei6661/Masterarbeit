import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QLineEdit, QPushButton, QFileDialog,
    QDialogButtonBox, QFormLayout, QCheckBox, QMessageBox,
    QSpinBox, QGroupBox
)
from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)


class PlotDialog(QDialog):
    def __init__(self, data, settings, parent=None):
        """
        初始化绘图对话框。
        
        参数:
            data: 要绘制的数据字典，包含以下键:
                - reflectance: 反射率数据
                - wavelengths: 波长数据
            settings: 应用程序设置
            parent: 父窗口
        """
        super().__init__(parent)
        self.setWindowTitle("Plot Settings")
        self.resize(800, 600)
        
        # 存储数据和设置
        self.data = data
        self.settings = settings
        
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 创建绘图预览区域
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # 添加绘图预览
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(self.toolbar)
        preview_layout.addWidget(self.canvas)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # 创建设置区域
        settings_group = QGroupBox("Plot Settings")
        settings_layout = QFormLayout()
        
        # 图表标题
        self.title_edit = QLineEdit("Reflectance Data")
        settings_layout.addRow("Title:", self.title_edit)
        
        # X轴标签
        self.xlabel_edit = QLineEdit("Wavelength (nm)")
        settings_layout.addRow("X-axis Label:", self.xlabel_edit)
        
        # Y轴标签
        self.ylabel_edit = QLineEdit("Reflectance")
        settings_layout.addRow("Y-axis Label:", self.ylabel_edit)
        
        # 显示网格
        self.grid_check = QCheckBox()
        self.grid_check.setChecked(self.settings['plot']['grid'])
        self.grid_check.stateChanged.connect(self.update_plot)
        settings_layout.addRow("Show Grid:", self.grid_check)
        
        # 显示图例
        self.legend_check = QCheckBox()
        self.legend_check.setChecked(self.settings['plot']['legend'])
        self.legend_check.stateChanged.connect(self.update_plot)
        settings_layout.addRow("Show Legend:", self.legend_check)
        
        # DPI设置
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 1200)
        self.dpi_spin.setValue(self.settings['plot']['dpi'])
        settings_layout.addRow("Export DPI:", self.dpi_spin)
        
        # 设置组
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # 创建导出区域
        export_group = QGroupBox("Export")
        export_layout = QFormLayout()
        
        # 文件格式选择
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG (.png)", "JPEG (.jpg)", "PDF (.pdf)", "SVG (.svg)"])
        export_layout.addRow("File Format:", self.format_combo)
        
        # 文件名和路径
        self.file_layout = QHBoxLayout()
        self.file_edit = QLineEdit()
        self.file_edit.setText(os.path.join(
            self.settings['export']['default_directory'], 
            "reflectance_plot.png"
        ))
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_file)
        self.file_layout.addWidget(self.file_edit)
        self.file_layout.addWidget(self.browse_button)
        
        file_widget = QWidget()
        file_widget.setLayout(self.file_layout)
        export_layout.addRow("File:", file_widget)
        
        # 导出组
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        
        # 更新预览按钮
        self.update_preview_button = QPushButton("Update Preview")
        self.update_preview_button.clicked.connect(self.update_plot)
        button_layout.addWidget(self.update_preview_button)
        
        # 添加空白区域
        button_layout.addStretch()
        
        # 确定和取消按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText("Export")
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        button_layout.addWidget(self.button_box)
        
        # 将按钮布局添加到主布局
        button_container = QWidget()
        button_container.setLayout(button_layout)
        layout.addWidget(button_container)
        
        # 初始化绘图
        self.update_plot()
    
    def update_plot(self):
        """更新绘图预览"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # 绘制反射率数据
        if 'reflectance' in self.data and 'wavelengths' in self.data:
            wavelengths = self.data['wavelengths']
            
            for name, values in self.data['reflectance'].items():
                ax.plot(wavelengths, values, label=name)
        
        # 设置标题和标签
        ax.set_title(self.title_edit.text())
        ax.set_xlabel(self.xlabel_edit.text())
        ax.set_ylabel(self.ylabel_edit.text())
        
        # 设置网格
        ax.grid(self.grid_check.isChecked())
        
        # 设置图例
        if self.legend_check.isChecked() and 'reflectance' in self.data:
            ax.legend()
        
        # 刷新画布
        self.canvas.draw()
    
    def browse_file(self):
        """浏览并选择导出文件路径"""
        # 根据选择的格式确定文件过滤器
        format_index = self.format_combo.currentIndex()
        if format_index == 0:
            file_filter = "PNG Files (*.png)"
            default_ext = ".png"
        elif format_index == 1:
            file_filter = "JPEG Files (*.jpg)"
            default_ext = ".jpg"
        elif format_index == 2:
            file_filter = "PDF Files (*.pdf)"
            default_ext = ".pdf"
        else:
            file_filter = "SVG Files (*.svg)"
            default_ext = ".svg"
        
        # 获取当前文件名（不含扩展名）
        current_path = self.file_edit.text()
        current_dir = os.path.dirname(current_path)
        current_name = os.path.splitext(os.path.basename(current_path))[0]
        
        # 打开文件对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Plot", 
            os.path.join(current_dir, current_name + default_ext),
            file_filter
        )
        
        if file_path:
            self.file_edit.setText(file_path)
    
    def accept(self):
        """确认导出图表"""
        # 获取导出文件路径
        file_path = self.file_edit.text()
        if not file_path:
            QMessageBox.warning(self, "Warning", "Please specify a file path.")
            return
        
        # 确保文件路径有正确的扩展名
        format_index = self.format_combo.currentIndex()
        if format_index == 0 and not file_path.lower().endswith('.png'):
            file_path += '.png'
        elif format_index == 1 and not file_path.lower().endswith('.jpg'):
            file_path += '.jpg'
        elif format_index == 2 and not file_path.lower().endswith('.pdf'):
            file_path += '.pdf'
        elif format_index == 3 and not file_path.lower().endswith('.svg'):
            file_path += '.svg'
        
        try:
            # 导出图表
            self.figure.savefig(
                file_path,
                dpi=self.dpi_spin.value(),
                bbox_inches='tight'
            )
            
            # 显示成功消息
            QMessageBox.information(self, "Success", f"Plot exported successfully to {file_path}")
            
            # 关闭对话框
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export plot: {e}") 