import sys
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QHBoxLayout, QWidget, QHeaderView, QApplication
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QClipboard, QFont


class ReflectanceDataDialog(QDialog):
    def __init__(self, wavelengths, datasets, parent=None):
        """
        初始化反射率数据对话框。
        
        参数:
            wavelengths: 波长数据数组
            datasets: 字典，键为数据集名称，值为对应的反射率数据数组
            parent: 父窗口
        """
        super().__init__(parent)
        self.setWindowTitle("Reflectance Data")
        
        # 获取父窗口的位置和大小
        parent_geometry = parent.geometry()
        parent_width = parent_geometry.width()
        parent_height = parent_geometry.height()
        parent_x = parent_geometry.x()
        parent_y = parent_geometry.y()
        
        # 设置窗口位置在父窗口右侧，窄长形状态
        dialog_width = 400  # 设置固定宽度
        dialog_height = parent_height  # 与父窗口等高
        self.setGeometry(parent_x + parent_width + 10, parent_y, dialog_width, dialog_height)
        
        # 存储数据
        self.wavelengths = wavelengths
        self.datasets = datasets
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  # 设置更适合的边距
        
        # 创建表格
        self.table = QTableWidget()
        self.setup_table_style()  # 设置表格样式
        self.populate_table()
        layout.addWidget(self.table)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 创建复制按钮
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(self.copy_button)
        
        # 将按钮布局添加到主布局
        button_container = QWidget()
        button_container.setLayout(button_layout)
        layout.addWidget(button_container)
    
    def setup_table_style(self):
        """设置表格样式，与主窗口表格一致"""
        # 设置行高
        self.table.verticalHeader().setDefaultSectionSize(22)  # 调整行高为22像素
        self.table.verticalHeader().setVisible(False)  # 隐藏垂直表头
        
        # 设置表格样式
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                font-size: 10pt;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 3px;
                font-size: 10pt;
                border: 1px solid #d0d0d0;
            }
            QTableWidget::item {
                padding: 3px;
            }
        """)
        
        # 设置表格属性
        self.table.setAlternatingRowColors(True)  # 交替行颜色
        self.table.setSortingEnabled(False)  # 禁用排序，与主表格一致
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
    
    def populate_table(self):
        """
        填充表格数据。
        """
        # 设置列数 (Lambda + 数据集数量)
        num_columns = 1 + len(self.datasets)
        self.table.setColumnCount(num_columns)
        
        # 设置行数 (波长数量)
        num_rows = len(self.wavelengths)
        self.table.setRowCount(num_rows)
        
        # 设置表头
        headers = ["Lambda (nm)"] + list(self.datasets.keys())
        self.table.setHorizontalHeaderLabels(headers)
        
        # 填充波长数据
        for row, wavelength in enumerate(self.wavelengths):
            wavelength_item = QTableWidgetItem(f"{wavelength:.2f}")
            wavelength_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 0, wavelength_item)
            
            # 填充各数据集的反射率数据
            for col, (dataset_name, dataset_values) in enumerate(self.datasets.items(), start=1):
                if row < len(dataset_values):
                    value_item = QTableWidgetItem(f"{dataset_values[row]:.6f}")
                    value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.table.setItem(row, col, value_item)
        
        # 初始设置波长列宽度
        self.table.setColumnWidth(0, 85)
        
        # 设置列宽 - 初始设置
        self.adjust_columns()
    
    def adjust_columns(self):
        """调整列宽以适应内容和窗口大小"""
        # 获取表格总宽度
        table_width = self.table.width()
        num_data_columns = len(self.datasets)
        
        if num_data_columns > 0:
            # 波长列固定宽度
            wavelength_column_width = 85  # 从100减小到85像素
            self.table.setColumnWidth(0, wavelength_column_width)
            
            # 其他列平均分配剩余空间
            remaining_width = table_width - wavelength_column_width - 20  # 减20作为滚动条和边距缓冲
            if remaining_width > 0 and num_data_columns > 0:
                data_column_width = max(100, remaining_width // num_data_columns)
                
                for col in range(1, self.table.columnCount()):
                    self.table.setColumnWidth(col, data_column_width)
    
    def copy_to_clipboard(self):
        """
        将表格数据复制到剪贴板。
        """
        clipboard = QApplication.clipboard()
        
        # 构建表格数据的文本表示
        text = ""
        
        # 添加表头
        headers = []
        for col in range(self.table.columnCount()):
            headers.append(self.table.horizontalHeaderItem(col).text())
        text += "\t".join(headers) + "\n"
        
        # 添加数据行
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            text += "\t".join(row_data) + "\n"
        
        # 设置剪贴板内容
        clipboard.setText(text)
    
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        # 调整列宽
        self.adjust_columns()
        
    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        # 窗口显示后调整列宽
        QTimer.singleShot(100, self.adjust_columns) 