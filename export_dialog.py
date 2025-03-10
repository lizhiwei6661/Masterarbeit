import os
import pandas as pd
import numpy as np
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QLineEdit, QPushButton, QFileDialog,
    QDialogButtonBox, QFormLayout, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt


class ExportDialog(QDialog):
    def __init__(self, data, settings, parent=None):
        """
        初始化导出对话框。
        
        参数:
            data: 要导出的数据字典，包含以下键:
                - reflectance: 反射率数据
                - wavelengths: 波长数据
                - results: 计算结果数据
            settings: 应用程序设置
            parent: 父窗口
        """
        super().__init__(parent)
        self.setWindowTitle("Export Data")
        self.resize(500, 250)
        
        # 存储数据和设置
        self.data = data
        self.settings = settings
        
        # 创建布局
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # 文件格式选择
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Excel (.xlsx)", "CSV (.csv)", "Text (.txt)"])
        # 根据设置选择默认格式
        default_format = self.settings['export']['default_format']
        if default_format == 'xlsx':
            self.format_combo.setCurrentIndex(0)
        elif default_format == 'csv':
            self.format_combo.setCurrentIndex(1)
        elif default_format == 'txt':
            self.format_combo.setCurrentIndex(2)
        form_layout.addRow("File Format:", self.format_combo)
        
        # 文件名和路径
        self.file_layout = QHBoxLayout()
        self.file_edit = QLineEdit()
        self.file_edit.setText(os.path.join(
            self.settings['export']['default_directory'], 
            "reflectance_data"
        ))
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_file)
        self.file_layout.addWidget(self.file_edit)
        self.file_layout.addWidget(self.browse_button)
        
        file_widget = QWidget()
        file_widget.setLayout(self.file_layout)
        form_layout.addRow("File:", file_widget)
        
        # 导出选项
        self.export_reflectance_check = QCheckBox("Export Reflectance Data")
        self.export_reflectance_check.setChecked(True)
        form_layout.addRow("", self.export_reflectance_check)
        
        self.export_results_check = QCheckBox("Export Calculation Results")
        self.export_results_check.setChecked(True)
        form_layout.addRow("", self.export_results_check)
        
        self.include_header_check = QCheckBox("Include Header")
        self.include_header_check.setChecked(self.settings['export']['include_header'])
        form_layout.addRow("", self.include_header_check)
        
        # 小数位数
        self.decimal_combo = QComboBox()
        self.decimal_combo.addItems(["2", "4", "6", "8"])
        self.decimal_combo.setCurrentText(str(self.settings['export']['decimal_places']))
        form_layout.addRow("Decimal Places:", self.decimal_combo)
        
        # 添加表单布局
        layout.addLayout(form_layout)
        
        # 添加按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
    
    def browse_file(self):
        """浏览并选择导出文件路径"""
        # 根据选择的格式确定文件过滤器
        format_index = self.format_combo.currentIndex()
        if format_index == 0:
            file_filter = "Excel Files (*.xlsx)"
            default_ext = ".xlsx"
        elif format_index == 1:
            file_filter = "CSV Files (*.csv)"
            default_ext = ".csv"
        else:
            file_filter = "Text Files (*.txt)"
            default_ext = ".txt"
        
        # 获取当前文件名（不含扩展名）
        current_path = self.file_edit.text()
        current_dir = os.path.dirname(current_path)
        current_name = os.path.splitext(os.path.basename(current_path))[0]
        
        # 打开文件对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Data", 
            os.path.join(current_dir, current_name + default_ext),
            file_filter
        )
        
        if file_path:
            self.file_edit.setText(file_path)
    
    def accept(self):
        """确认导出数据"""
        # 检查是否至少选择了一种导出数据类型
        if not self.export_reflectance_check.isChecked() and not self.export_results_check.isChecked():
            QMessageBox.warning(self, "Warning", "Please select at least one data type to export.")
            return
        
        # 获取导出文件路径
        file_path = self.file_edit.text()
        if not file_path:
            QMessageBox.warning(self, "Warning", "Please specify a file path.")
            return
        
        # 确保文件路径有正确的扩展名
        format_index = self.format_combo.currentIndex()
        if format_index == 0 and not file_path.lower().endswith('.xlsx'):
            file_path += '.xlsx'
        elif format_index == 1 and not file_path.lower().endswith('.csv'):
            file_path += '.csv'
        elif format_index == 2 and not file_path.lower().endswith('.txt'):
            file_path += '.txt'
        
        # 获取小数位数
        decimal_places = int(self.decimal_combo.currentText())
        
        try:
            # 导出数据
            self.export_data(
                file_path, 
                format_index, 
                self.export_reflectance_check.isChecked(),
                self.export_results_check.isChecked(),
                self.include_header_check.isChecked(),
                decimal_places
            )
            
            # 显示成功消息
            QMessageBox.information(self, "Success", f"Data exported successfully to {file_path}")
            
            # 关闭对话框
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export data: {e}")
    
    def export_data(self, file_path, format_index, export_reflectance, export_results, include_header, decimal_places):
        """
        导出数据到文件。
        
        参数:
            file_path: 导出文件路径
            format_index: 文件格式索引 (0=xlsx, 1=csv, 2=txt)
            export_reflectance: 是否导出反射率数据
            export_results: 是否导出计算结果
            include_header: 是否包含表头
            decimal_places: 小数位数
        """
        # 准备数据
        dfs = []
        
        # 反射率数据
        if export_reflectance and 'reflectance' in self.data and 'wavelengths' in self.data:
            reflectance_data = {}
            reflectance_data['Wavelength (nm)'] = self.data['wavelengths']
            
            # 添加每个数据集的反射率
            for name, values in self.data['reflectance'].items():
                reflectance_data[f"{name}"] = values
            
            reflectance_df = pd.DataFrame(reflectance_data)
            dfs.append(("Reflectance", reflectance_df))
        
        # 计算结果
        if export_results and 'results' in self.data:
            results_df = pd.DataFrame(self.data['results'])
            dfs.append(("Results", results_df))
        
        # 根据格式导出
        if format_index == 0:  # Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for sheet_name, df in dfs:
                    df.to_excel(
                        writer, 
                        sheet_name=sheet_name, 
                        index=False if include_header else None,
                        header=include_header,
                        float_format=f"%.{decimal_places}f"
                    )
        elif format_index == 1:  # CSV
            # 对于CSV，我们将所有数据合并到一个文件中
            if len(dfs) > 0:
                combined_df = dfs[0][1]
                combined_df.to_csv(
                    file_path, 
                    index=False if include_header else None,
                    header=include_header,
                    float_format=f"%.{decimal_places}f"
                )
        else:  # TXT
            # 对于TXT，我们将所有数据合并到一个文件中
            if len(dfs) > 0:
                combined_df = dfs[0][1]
                combined_df.to_csv(
                    file_path, 
                    sep='\t',
                    index=False if include_header else None,
                    header=include_header,
                    float_format=f"%.{decimal_places}f"
                ) 