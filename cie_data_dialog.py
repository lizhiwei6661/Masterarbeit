import sys
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QWidget, QHeaderView, QApplication, QSplitter
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QClipboard, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches
import numpy as np


class CIEDataDialog(QDialog):
    def __init__(self, cie_data, parent=None):
        """
        初始化CIE数据对话框。
        
        参数:
            cie_data: CIE数据列表，每个元素为一个字典，包含x、y坐标和RGB颜色值
            parent: 父窗口
        """
        super().__init__(parent)
        self.setWindowTitle("CIE Data")
        
        # 获取父窗口的位置和大小
        parent_geometry = parent.geometry()
        parent_width = parent_geometry.width()
        parent_height = parent_geometry.height()
        parent_x = parent_geometry.x()
        parent_y = parent_geometry.y()
        
        # 设置窗口位置在父窗口右侧，适当大小
        dialog_width = 800
        dialog_height = parent_height * 0.8
        self.setGeometry(parent_x + parent_width + 10, parent_y, dialog_width, dialog_height)
        
        # 存储数据
        self.cie_data = cie_data
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建拆分器，上部显示图表，下部显示数据表格
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)
        
        # 创建CIE图表
        self.figure_widget = QWidget()
        self.figure_layout = QVBoxLayout(self.figure_widget)
        self.figure_layout.setContentsMargins(0, 0, 0, 0)
        
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.figure_layout.addWidget(self.canvas)
        
        # 添加图表到拆分器
        splitter.addWidget(self.figure_widget)
        
        # 创建数据表格
        self.table_widget = QWidget()
        self.table_layout = QVBoxLayout(self.table_widget)
        self.table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget()
        self.setup_table()
        self.table_layout.addWidget(self.table)
        
        # 添加复制按钮
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.button_layout.addWidget(self.copy_button)
        
        self.table_layout.addLayout(self.button_layout)
        
        # 添加表格到拆分器
        splitter.addWidget(self.table_widget)
        
        # 设置初始拆分比例
        splitter.setSizes([int(dialog_height * 0.6), int(dialog_height * 0.4)])
        
        # 添加拆分器到主布局
        main_layout.addWidget(splitter)
        
        # 设置对话框标志，允许与主窗口交互
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        # 在对话框显示后填充数据
        QTimer.singleShot(0, self.populate_data)
    
    def setup_table(self):
        """设置表格样式"""
        # 设置列数和表头
        self.table.setColumnCount(5)
        headers = ["Color", "File Name", "x", "y", "RGB"]
        for i, header in enumerate(headers):
            item = QTableWidgetItem(header)
            self.table.setHorizontalHeaderItem(i, item)
        
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
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        
        # 设置行高
        self.table.verticalHeader().setDefaultSectionSize(22)
        self.table.verticalHeader().setVisible(False)
        
        # 设置列宽
        self.table.setColumnWidth(0, 50)  # 颜色列
        self.table.setColumnWidth(1, 150)  # 文件名列
        self.table.setColumnWidth(2, 80)  # x列
        self.table.setColumnWidth(3, 80)  # y列
        self.table.setColumnWidth(4, 200)  # RGB列
    
    def populate_data(self):
        """填充数据到表格和图表"""
        self.populate_table()
        self.draw_cie_plot()
    
    def populate_table(self):
        """填充数据到表格"""
        # 清空表格
        self.table.setRowCount(0)
        
        # 添加数据行
        for i, data in enumerate(self.cie_data):
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            
            # 添加颜色单元格
            color_item = QTableWidgetItem()
            color_item.setBackground(QColor(data['hex_color']))
            self.table.setItem(row_position, 0, color_item)
            
            # 添加文件名
            file_name = data['file_name']
            # 移除文件扩展名
            if file_name.lower().endswith('.csv'):
                file_name = file_name[:-4]
                
            file_item = QTableWidgetItem(file_name)
            self.table.setItem(row_position, 1, file_item)
            
            # 添加x坐标
            x_item = QTableWidgetItem(f"{data['x']:.6f}")
            x_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row_position, 2, x_item)
            
            # 添加y坐标
            y_item = QTableWidgetItem(f"{data['y']:.6f}")
            y_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row_position, 3, y_item)
            
            # 添加RGB值
            rgb_linear = data['rgb_linear']
            rgb_gamma = data['rgb_gamma']
            rgb_item = QTableWidgetItem(f"Linear: ({rgb_linear[0]:.4f}, {rgb_linear[1]:.4f}, {rgb_linear[2]:.4f})\nGamma: ({int(rgb_gamma[0]*255)}, {int(rgb_gamma[1]*255)}, {int(rgb_gamma[2]*255)})")
            self.table.setItem(row_position, 4, rgb_item)
    
    def draw_cie_plot(self):
        """绘制CIE色度图"""
        # 清除图表
        self.figure.clear()
        
        # 创建子图
        ax = self.figure.add_subplot(111)
        
        # 设置标题和轴标签
        ax.set_title("CIE 1931 Chromaticity Diagram", fontsize=12)
        ax.set_xlabel("x", fontsize=10)
        ax.set_ylabel("y", fontsize=10)
        
        # 绘制CIE 1931色度图边界 - 使用简化的顶点
        boundary_x = [0.1740, 0.0000, 0.0000, 0.0332, 0.0648, 0.0919, 0.1390, 0.1738, 0.2080, 0.2586, 0.3230, 0.3962, 0.4400, 0.4699, 0.4999, 0.5140, 0.5295, 0.5482, 0.5651, 0.5780, 0.5832, 0.5800, 0.5672, 0.5314, 0.4649, 0.3652, 0.2615, 0.1740]
        boundary_y = [0.0049, 0.0000, 0.0100, 0.0380, 0.0650, 0.0910, 0.2080, 0.2737, 0.3344, 0.4077, 0.4964, 0.5574, 0.5800, 0.5888, 0.5991, 0.6039, 0.6089, 0.6128, 0.6150, 0.6160, 0.6160, 0.6155, 0.6123, 0.6030, 0.5657, 0.4679, 0.2624, 0.0049]
        
        # 填充CIE区域
        ax.fill(boundary_x, boundary_y, alpha=0.1, color='gray')
        
        # 绘制边界
        ax.plot(boundary_x, boundary_y, 'k-', linewidth=1.5)
        
        # 绘制光源点（假设D65）
        ax.plot(0.3128, 0.3290, 'ko', markersize=6, label='D65')
        
        # 绘制sRGB色域
        srgb_r = (0.64, 0.33)
        srgb_g = (0.30, 0.60)
        srgb_b = (0.15, 0.06)
        srgb_x = [srgb_r[0], srgb_g[0], srgb_b[0], srgb_r[0]]
        srgb_y = [srgb_r[1], srgb_g[1], srgb_b[1], srgb_r[1]]
        ax.plot(srgb_x, srgb_y, 'k--', linewidth=1.5, label='sRGB')
        
        # 绘制数据点
        for data in self.cie_data:
            x, y = data['x'], data['y']
            hex_color = data['hex_color']
            ax.scatter(x, y, color=hex_color, edgecolors='black', s=80, zorder=10)
            
            # 可选：添加标签
            # ax.annotate(data['file_name'], (x, y), textcoords="offset points", 
            #             xytext=(0, 10), ha='center', fontsize=8)
        
        # 设置图表范围
        ax.set_xlim(0, 0.8)
        ax.set_ylim(0, 0.9)
        
        # 添加网格线
        ax.grid(True, alpha=0.3)
        
        # 添加图例
        ax.legend(loc='best', fontsize=8)
        
        # 调整布局
        self.figure.tight_layout()
        
        # 刷新画布
        self.canvas.draw()
    
    def copy_to_clipboard(self):
        """复制表格数据到剪贴板"""
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
                if col == 0:  # 跳过颜色列
                    continue
                    
                item = self.table.item(row, col)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            text += "\t".join(row_data) + "\n"
        
        # 设置剪贴板内容
        clipboard.setText(text) 