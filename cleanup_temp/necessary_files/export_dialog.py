import os
import pandas as pd
import numpy as np
from PySide6.QtWidgets import (
    QDialog, QFileDialog, QMessageBox, QPushButton, QLineEdit, QHBoxLayout, QWidget
)
from PySide6.QtCore import Qt
from ui_export_dialog import Ui_Dialog_export

class ExportDialog(QDialog):
    def __init__(self, data, settings, parent=None):
        """
        导出对话框，允许用户选择要导出的数据类型。
        
        参数:
            data: 要导出的数据字典
            settings: 应用程序设置
            parent: 父窗口
        """
        super().__init__(parent)
        self.data = data
        self.settings = settings
        self.parent = parent
        self.setModal(True)  # 设置为模态对话框，防止创建多个实例
        
        # 初始化UI
        self.ui = Ui_Dialog_export()
        self.ui.setupUi(self)
        
        # 设置默认文件名和路径
        default_dir = self.settings['export']['default_directory']
        default_filename = "export_data.xlsx"
        self.ui.lineEdit_Export_File.setText(os.path.join(default_dir, default_filename))
        
        # 连接浏览按钮的信号
        self.ui.pushButton_Export_Browse.clicked.connect(self.browse_file)
        
        # 连接确认按钮的信号
        self.ui.buttonBox.accepted.connect(self.on_accepted)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        # 确保至少选择一种数据类型
        self.ui.checkBox_Export_Rho.stateChanged.connect(self.check_selection)
        self.ui.checkBox_Export_Color.stateChanged.connect(self.check_selection)
    
    def check_selection(self):
        """确保至少选择一种数据类型"""
        if not self.ui.checkBox_Export_Rho.isChecked() and not self.ui.checkBox_Export_Color.isChecked():
            # 如果两个复选框都未选中，禁用确定按钮
            self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Ok).setEnabled(False)
        else:
            # 如果至少选中一个，启用确定按钮
            self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Ok).setEnabled(True)
    
    def browse_file(self):
        """打开文件选择对话框"""
        current_path = self.ui.lineEdit_Export_File.text()
        current_dir = os.path.dirname(current_path) if current_path else self.settings['export']['default_directory']
        
        # 获取当前选择的文件格式
        format_idx = self.ui.comboBox_Export_Format.currentIndex()
        if format_idx == 0:
            filter_text = "Excel 文件 (*.xlsx)"
            ext = ".xlsx"
        elif format_idx == 1:
            filter_text = "CSV 文件 (*.csv)"
            ext = ".csv"
        elif format_idx == 2:
            filter_text = "文本文件 (*.txt)"
            ext = ".txt"
        elif format_idx == 3:
            filter_text = "JSON 文件 (*.json)"
            ext = ".json"
        else:
            filter_text = "文本文件 (*.txt)"
            ext = ".txt"
        
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "导出数据",
            os.path.join(current_dir, f"export_data{ext}"),
            filter_text
        )
        
        if file_path:
            self.ui.lineEdit_Export_File.setText(file_path)
    
    def on_accepted(self):
        """用户点击确定按钮时的处理"""
        export_rho = self.ui.checkBox_Export_Rho.isChecked()
        export_color = self.ui.checkBox_Export_Color.isChecked()
        
        if not export_rho and not export_color:
            QMessageBox.warning(self, "导出错误", "请至少选择一种数据类型进行导出")
            return
        
        file_path = self.ui.lineEdit_Export_File.text()
        if not file_path:
            QMessageBox.warning(self, "导出错误", "请指定导出文件路径")
            return
        
        # 根据选择的格式调用相应的导出函数
        format_idx = self.ui.comboBox_Export_Format.currentIndex()
        
        # 确保有正确的扩展名
        if format_idx == 0 and not file_path.lower().endswith('.xlsx'):
            file_path += '.xlsx'
        elif format_idx == 1 and not file_path.lower().endswith('.csv'):
            file_path += '.csv'
        elif format_idx == 2 and not file_path.lower().endswith('.txt'):
            file_path += '.txt'
        elif format_idx == 3 and not file_path.lower().endswith('.json'):
            file_path += '.json'
        
        success = False
        
        if format_idx == 0:
            success = self.export_to_excel(file_path, export_rho, export_color)
        elif format_idx == 1:
            success = self.export_to_csv(file_path, export_rho, export_color)
        elif format_idx == 2:
            success = self.export_to_txt(file_path, export_rho, export_color)
        elif format_idx == 3:
            success = self.export_to_json(file_path, export_rho, export_color)
        
        if success:
            # 保存导出目录到设置
            self.settings['export']['default_directory'] = os.path.dirname(file_path)
            if self.parent:
                self.parent.save_settings()
            
            # 显示成功消息
            QMessageBox.information(self, "成功", f"数据已成功导出至 {file_path}")
            
            # 关闭对话框
            self.accept()
    
    def export_to_excel(self, file_path, export_rho=True, export_color=True):
        """导出数据到Excel文件，可选择导出的数据类型"""
        try:
            # 获取原始波长数据
            wavelengths = self.data.get('original_wavelengths', None)
            if wavelengths is None and 'wavelengths' in self.data:
                wavelengths = self.data['wavelengths']
            
            if export_rho and wavelengths is None:
                raise Exception("没有找到波长数据，无法导出反射率数据")
            
            # 获取文件名列表
            file_names = []
            for result in self.data['results']:
                if result['file_name'] not in file_names:
                    file_names.append(result['file_name'])
            
            # 使用openpyxl引擎，创建Excel写入对象
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                
                # 创建并导出反射率数据（如果选择导出）
                if export_rho:
                    # 创建反射率数据
                    rho_data = {'Lambda': wavelengths}
                    
                    # 添加每个文件的反射率数据，去掉扩展名
                    for file_name in file_names:
                        if file_name in self.data['reflectance']:
                            # 去掉文件扩展名
                            base_name = os.path.splitext(file_name)[0]
                            
                            reflectance_data = self.data['reflectance'][file_name]
                            reflectance_values = None
                            
                            # 尝试提取反射率数据
                            if isinstance(reflectance_data, dict):
                                if 'reflectance_1nm' in reflectance_data and len(reflectance_data['reflectance_1nm']) == len(wavelengths):
                                    reflectance_values = reflectance_data['reflectance_1nm']
                                elif 'reflectance' in reflectance_data and len(reflectance_data['reflectance']) == len(wavelengths):
                                    reflectance_values = reflectance_data['reflectance']
                            elif isinstance(reflectance_data, np.ndarray) and len(reflectance_data) == len(wavelengths):
                                reflectance_values = reflectance_data
                            
                            # 只添加长度匹配的数据
                            if reflectance_values is not None:
                                rho_data[base_name] = reflectance_values
                    
                    # 创建DataFrame并导出
                    rho_df = pd.DataFrame(rho_data)
                    rho_df.to_excel(writer, index=False, header=True, sheet_name='rho')
                
                # 创建并导出颜色数据（如果选择导出）
                if export_color:
                    # 准备颜色数据
                    color_data = {
                        'Unnamed: 0': [],  # 文件名列
                        'x': [],
                        'y': [],
                        'R (lin)': [],
                        'G (lin)': [],
                        'B (lin)': [],
                        'R (gamma)': [],
                        'G (gamma)': [],
                        'B (gamma)': []
                    }
                    
                    # 按文件名顺序填充数据
                    for i in range(min(3, len(self.data['results']))):
                        # 获取结果数据
                        result = self.data['results'][i]
                        # 去掉文件扩展名
                        base_name = os.path.splitext(result['file_name'])[0]
                        
                        # 文件名和色度坐标
                        color_data['Unnamed: 0'].append(base_name)
                        color_data['x'].append(result['x'])
                        color_data['y'].append(result['y'])
                        
                        # RGB线性值 - 直接使用计算结果
                        color_data['R (lin)'].append(result['rgb_linear'][0])
                        color_data['G (lin)'].append(result['rgb_linear'][1])
                        color_data['B (lin)'].append(result['rgb_linear'][2])
                        
                        # RGB伽马值（0-255范围）- 直接使用计算结果
                        # 注意：R值需要截断为255，如示例文件所示
                        r_gamma = round(result['rgb_gamma'][0] * 255)
                        if r_gamma > 255:
                            r_gamma = 255
                        
                        color_data['R (gamma)'].append(r_gamma)
                        color_data['G (gamma)'].append(round(result['rgb_gamma'][1] * 255))
                        color_data['B (gamma)'].append(round(result['rgb_gamma'][2] * 255))
                    
                    # 创建DataFrame并导出
                    color_df = pd.DataFrame(color_data)
                    color_df.to_excel(writer, index=False, header=True, sheet_name='color')
                
                # 获取工作表，应用格式
                workbook = writer.book
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    
                    # 移除所有单元格格式
                    from openpyxl.styles import Font, Alignment, Border, Side
                    
                    # 创建一个普通字体和对齐方式
                    normal_font = Font(name='Calibri', size=11, bold=False)
                    general_alignment = Alignment(horizontal='general', vertical='bottom')
                    no_border = Border(left=Side(style=None), right=Side(style=None), 
                                      top=Side(style=None), bottom=Side(style=None))
                    
                    # 应用于所有单元格
                    for row in worksheet.rows:
                        for cell in row:
                            cell.font = normal_font
                            cell.alignment = general_alignment
                            cell.border = no_border
            
            print(f"数据已成功导出到 {file_path}")
            return True
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出Excel文件失败: {e}")
            print(f"导出Excel文件失败: {e}")
            return False
    
    def export_to_csv(self, file_path, export_rho=True, export_color=True):
        """导出数据到CSV文件，可以分别导出反射率数据和颜色数据到不同的CSV文件"""
        try:
            # 检查要导出的数据类型
            if not export_rho and not export_color:
                QMessageBox.warning(self, "导出错误", "请至少选择一种数据类型进行导出")
                return False
                
            # 获取文件名（不含扩展名）和目录
            file_dir = os.path.dirname(file_path)
            file_name_base = os.path.splitext(os.path.basename(file_path))[0]
            
            success = True
            exported_files = []
            
            # 导出反射率数据（如果选择了导出反射率）
            if export_rho:
                # 创建反射率CSV文件路径
                rho_file_path = os.path.join(file_dir, f"{file_name_base}_rho.csv")
                
                # 获取波长数据
                wavelengths = self.data.get('original_wavelengths', None)
                if wavelengths is None and 'wavelengths' in self.data:
                    wavelengths = self.data['wavelengths']
                
                if wavelengths is None:
                    QMessageBox.warning(self, "导出错误", "没有找到波长数据，无法导出反射率数据")
                    return False
                
                # 创建反射率数据
                rho_data = {'Wavelength [nm]': wavelengths}
                
                # 获取文件名列表
                file_names = []
                for result in self.data['results']:
                    if result['file_name'] not in file_names:
                        file_names.append(result['file_name'])
                
                # 添加每个文件的反射率数据
                for file_name in file_names:
                    if file_name in self.data['reflectance']:
                        # 去掉文件扩展名
                        base_name = os.path.splitext(file_name)[0]
                        
                        reflectance_data = self.data['reflectance'][file_name]
                        reflectance_values = None
                        
                        # 尝试提取反射率数据
                        if isinstance(reflectance_data, dict):
                            if 'reflectance_1nm' in reflectance_data and len(reflectance_data['reflectance_1nm']) == len(wavelengths):
                                reflectance_values = reflectance_data['reflectance_1nm']
                            elif 'reflectance' in reflectance_data and len(reflectance_data['reflectance']) == len(wavelengths):
                                reflectance_values = reflectance_data['reflectance']
                        elif isinstance(reflectance_data, np.ndarray) and len(reflectance_data) == len(wavelengths):
                            reflectance_values = reflectance_data
                        
                        # 只添加长度匹配的数据
                        if reflectance_values is not None:
                            rho_data[base_name] = reflectance_values
                
                # 创建DataFrame并导出
                rho_df = pd.DataFrame(rho_data)
                
                # 在CSV文件开头添加元数据信息（类似于示例文件）
                with open(rho_file_path, 'w') as f:
                    f.write("MODEL,Aleksameter\n")
                    f.write("TYPE,Reflectance\n")
                    f.write(f"Number of datasets,{len(rho_data) - 1}\n")
                    f.write("Operator,\n")
                    f.write("Memo,\n")
                    f.write(f"Start Wavelength [nm],{wavelengths[0]}\n")
                    f.write(f"End Wavelength [nm],{wavelengths[-1]}\n")
                    f.write(f"Number of points,{len(wavelengths)}\n")
                    f.write("\n")
                    
                    # 添加当前日期和时间
                    from datetime import datetime
                    now = datetime.now()
                    f.write(f"Date,{now.strftime('%m/%d/%Y')}\n")
                    f.write(f"Time,{now.strftime('%I:%M:%S%p')}\n")
                    f.write("\n")
                    
                    # 添加列标题和数据
                    f.write("Wavelength [nm],")
                    f.write(",".join([col for col in rho_df.columns if col != 'Wavelength [nm]']))
                    f.write("\n")
                    
                    # 逐行写入数据
                    for idx, row in rho_df.iterrows():
                        f.write(",".join([f"{val:.8E}" if isinstance(val, float) else str(val) for val in row]))
                        f.write("\n")
                
                exported_files.append(rho_file_path)
                print(f"反射率数据已成功导出到 {rho_file_path}")
            
            # 导出颜色数据（如果选择了导出颜色）
            if export_color:
                # 创建颜色CSV文件路径
                color_file_path = os.path.join(file_dir, f"{file_name_base}_color.csv")
                
                # 准备颜色数据
                color_data = {
                    'File': [],
                    'x': [],
                    'y': [],
                    'R_lin': [],
                    'G_lin': [],
                    'B_lin': [],
                    'R_gamma': [],
                    'G_gamma': [],
                    'B_gamma': []
                }
                
                # 填充颜色数据
                for result in self.data['results']:
                    # 去掉文件扩展名
                    base_name = os.path.splitext(result['file_name'])[0]
                    
                    color_data['File'].append(base_name)
                    color_data['x'].append(result['x'])
                    color_data['y'].append(result['y'])
                    
                    # RGB线性值
                    color_data['R_lin'].append(result['rgb_linear'][0])
                    color_data['G_lin'].append(result['rgb_linear'][1])
                    color_data['B_lin'].append(result['rgb_linear'][2])
                    
                    # RGB伽马值（0-255范围）
                    r_gamma = result['rgb_gamma'][0] * 255
                    if r_gamma > 255:
                        r_gamma = 255
                    
                    color_data['R_gamma'].append(r_gamma)
                    color_data['G_gamma'].append(result['rgb_gamma'][1] * 255)
                    color_data['B_gamma'].append(result['rgb_gamma'][2] * 255)
                
                # 创建DataFrame
                color_df = pd.DataFrame(color_data)
                
                # 在CSV文件开头添加元数据信息
                with open(color_file_path, 'w') as f:
                    f.write("MODEL,Aleksameter\n")
                    f.write("TYPE,Color Data\n")
                    f.write(f"Number of samples,{len(color_df)}\n")
                    f.write("Operator,\n")
                    f.write("Memo,\n")
                    f.write("\n")
                    
                    # 添加当前日期和时间
                    from datetime import datetime
                    now = datetime.now()
                    f.write(f"Date,{now.strftime('%m/%d/%Y')}\n")
                    f.write(f"Time,{now.strftime('%I:%M:%S%p')}\n")
                    f.write("\n")
                    
                    # 添加列标题
                    f.write("File,x,y,R (lin),G (lin),B (lin),R (gamma),G (gamma),B (gamma)\n")
                    
                    # 逐行写入数据
                    for idx, row in color_df.iterrows():
                        f.write(f"{row['File']},{row['x']:.6f},{row['y']:.6f},{row['R_lin']:.6f},{row['G_lin']:.6f},{row['B_lin']:.6f},{int(row['R_gamma'])},{int(row['G_gamma'])},{int(row['B_gamma'])}\n")
                
                exported_files.append(color_file_path)
                print(f"颜色数据已成功导出到 {color_file_path}")
            
            # 显示导出成功消息
            if len(exported_files) > 0:
                QMessageBox.information(self, "导出成功", f"数据已成功导出到以下文件：\n" + "\n".join(exported_files))
                return True
            else:
                return False
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出CSV文件失败: {e}")
            print(f"导出CSV文件失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def export_to_txt(self, file_path, export_rho=True, export_color=True):
        """导出数据到TXT文件，可以分别导出反射率数据和颜色数据到不同的TXT文件"""
        try:
            # 检查要导出的数据类型
            if not export_rho and not export_color:
                QMessageBox.warning(self, "导出错误", "请至少选择一种数据类型进行导出")
                return False
                
            # 获取文件名（不含扩展名）和目录
            file_dir = os.path.dirname(file_path)
            file_name_base = os.path.splitext(os.path.basename(file_path))[0]
            
            success = True
            exported_files = []
            
            # 获取数字分隔符设置
            use_comma_as_decimal = self.settings['export']['separator'] == 'Comma'
            decimal_separator = ',' if use_comma_as_decimal else '.'
            
            # 获取是否添加header的设置
            include_header = self.settings['export']['copy_header'] == 'Yes'
            
            # 导出反射率数据（如果选择了导出反射率）
            if export_rho:
                # 创建反射率TXT文件路径
                rho_file_path = os.path.join(file_dir, f"{file_name_base}_rho.txt")
                
                # 获取波长数据
                wavelengths = self.data.get('original_wavelengths', None)
                if wavelengths is None and 'wavelengths' in self.data:
                    wavelengths = self.data['wavelengths']
                
                if wavelengths is None:
                    QMessageBox.warning(self, "导出错误", "没有找到波长数据，无法导出反射率数据")
                    return False
                
                # 创建反射率数据
                rho_data = {'Wavelength [nm]': wavelengths}
                
                # 获取文件名列表
                file_names = []
                for result in self.data['results']:
                    if result['file_name'] not in file_names:
                        file_names.append(result['file_name'])
                
                # 添加每个文件的反射率数据
                for file_name in file_names:
                    if file_name in self.data['reflectance']:
                        # 去掉文件扩展名
                        base_name = os.path.splitext(file_name)[0]
                        
                        reflectance_data = self.data['reflectance'][file_name]
                        reflectance_values = None
                        
                        # 尝试提取反射率数据
                        if isinstance(reflectance_data, dict):
                            if 'reflectance_1nm' in reflectance_data and len(reflectance_data['reflectance_1nm']) == len(wavelengths):
                                reflectance_values = reflectance_data['reflectance_1nm']
                            elif 'reflectance' in reflectance_data and len(reflectance_data['reflectance']) == len(wavelengths):
                                reflectance_values = reflectance_data['reflectance']
                        elif isinstance(reflectance_data, np.ndarray) and len(reflectance_data) == len(wavelengths):
                            reflectance_values = reflectance_data
                        
                        # 只添加长度匹配的数据
                        if reflectance_values is not None:
                            rho_data[base_name] = reflectance_values
                
                # 创建DataFrame并导出
                rho_df = pd.DataFrame(rho_data)
                
                # 直接导出数据，根据设置决定是否包含header
                with open(rho_file_path, 'w') as f:
                    # 只有在设置为包含header时才添加列标题
                    if include_header:
                        f.write("Wavelength [nm]\t")
                        f.write("\t".join([col for col in rho_df.columns if col != 'Wavelength [nm]']))
                        f.write("\n")
                    
                    # 逐行写入数据，根据设置使用不同的小数点分隔符
                    for idx, row in rho_df.iterrows():
                        if use_comma_as_decimal:
                            # 使用逗号作为小数点分隔符
                            values = [f"{val:.8E}".replace('.', ',') if isinstance(val, float) else str(val) for val in row]
                            f.write("\t".join(values))
                        else:
                            # 使用点作为小数点分隔符（默认）
                            f.write("\t".join([f"{val:.8E}" if isinstance(val, float) else str(val) for val in row]))
                        f.write("\n")
                
                exported_files.append(rho_file_path)
                print(f"反射率数据已成功导出到 {rho_file_path}")
            
            # 导出颜色数据（如果选择了导出颜色）
            if export_color:
                # 创建颜色TXT文件路径
                color_file_path = os.path.join(file_dir, f"{file_name_base}_color.txt")
                
                # 准备颜色数据
                color_data = {
                    'File': [],
                    'x': [],
                    'y': [],
                    'R_lin': [],
                    'G_lin': [],
                    'B_lin': [],
                    'R_gamma': [],
                    'G_gamma': [],
                    'B_gamma': []
                }
                
                # 填充颜色数据
                for result in self.data['results']:
                    # 去掉文件扩展名
                    base_name = os.path.splitext(result['file_name'])[0]
                    
                    color_data['File'].append(base_name)
                    color_data['x'].append(result['x'])
                    color_data['y'].append(result['y'])
                    
                    # RGB线性值
                    color_data['R_lin'].append(result['rgb_linear'][0])
                    color_data['G_lin'].append(result['rgb_linear'][1])
                    color_data['B_lin'].append(result['rgb_linear'][2])
                    
                    # RGB伽马值（0-255范围）
                    r_gamma = result['rgb_gamma'][0] * 255
                    if r_gamma > 255:
                        r_gamma = 255
                    
                    color_data['R_gamma'].append(r_gamma)
                    color_data['G_gamma'].append(result['rgb_gamma'][1] * 255)
                    color_data['B_gamma'].append(result['rgb_gamma'][2] * 255)
                
                # 创建DataFrame
                color_df = pd.DataFrame(color_data)
                
                # 直接导出数据，根据设置决定是否包含header
                with open(color_file_path, 'w') as f:
                    # 只有在设置为包含header时才添加列标题
                    if include_header:
                        f.write("File\tx\ty\tR (lin)\tG (lin)\tB (lin)\tR (gamma)\tG (gamma)\tB (gamma)\n")
                    
                    # 逐行写入数据，根据设置使用不同的小数点分隔符
                    for idx, row in color_df.iterrows():
                        if use_comma_as_decimal:
                            # 使用逗号作为小数点分隔符
                            x_str = f"{row['x']:.6f}".replace('.', ',')
                            y_str = f"{row['y']:.6f}".replace('.', ',')
                            r_lin_str = f"{row['R_lin']:.6f}".replace('.', ',')
                            g_lin_str = f"{row['G_lin']:.6f}".replace('.', ',')
                            b_lin_str = f"{row['B_lin']:.6f}".replace('.', ',')
                            f.write(f"{row['File']}\t{x_str}\t{y_str}\t{r_lin_str}\t{g_lin_str}\t{b_lin_str}\t{int(row['R_gamma'])}\t{int(row['G_gamma'])}\t{int(row['B_gamma'])}\n")
                        else:
                            # 使用点作为小数点分隔符（默认）
                            f.write(f"{row['File']}\t{row['x']:.6f}\t{row['y']:.6f}\t{row['R_lin']:.6f}\t{row['G_lin']:.6f}\t{row['B_lin']:.6f}\t{int(row['R_gamma'])}\t{int(row['G_gamma'])}\t{int(row['B_gamma'])}\n")
                
                exported_files.append(color_file_path)
                print(f"颜色数据已成功导出到 {color_file_path}")
            
            # 显示导出成功消息
            if len(exported_files) > 0:
                QMessageBox.information(self, "导出成功", f"数据已成功导出到以下文件：\n" + "\n".join(exported_files))
                return True
            else:
                return False
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出TXT文件失败: {e}")
            print(f"导出TXT文件失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def export_to_json(self, file_path, export_rho=True, export_color=True):
        """导出数据到JSON文件，可选择导出反射率数据、颜色数据或两者兼有"""
        try:
            # 检查要导出的数据类型
            if not export_rho and not export_color:
                QMessageBox.warning(self, "导出错误", "请至少选择一种数据类型进行导出")
                return False
            
            import json
            from datetime import datetime
            
            # 获取当前日期和时间
            now = datetime.now()
            date_str = now.strftime('%m/%d/%Y')
            time_str = now.strftime('%I:%M:%S%p')
            
            # 创建存储所有数据的JSON对象
            json_data = {
                "model": "Aleksameter",
                "date": date_str,
                "time": time_str,
                "metadata": {
                    "operator": "",
                    "memo": ""
                }
            }
            
            # 导出反射率数据
            if export_rho:
                # 获取波长数据
                wavelengths = self.data.get('original_wavelengths', None)
                if wavelengths is None and 'wavelengths' in self.data:
                    wavelengths = self.data['wavelengths']
                
                if wavelengths is None:
                    QMessageBox.warning(self, "导出错误", "没有找到波长数据，无法导出反射率数据")
                    return False
                
                # 转换numpy数组为列表（JSON可序列化）
                wavelengths_list = wavelengths.tolist() if isinstance(wavelengths, np.ndarray) else list(wavelengths)
                
                # 创建反射率数据部分
                rho_data = {
                    "type": "Reflectance",
                    "metadata": {
                        "start_wavelength_nm": float(wavelengths[0]),
                        "end_wavelength_nm": float(wavelengths[-1]),
                        "num_points": len(wavelengths)
                    },
                    "wavelengths_nm": wavelengths_list,
                    "samples": {}
                }
                
                # 获取文件名列表
                file_names = []
                for result in self.data['results']:
                    if result['file_name'] not in file_names:
                        file_names.append(result['file_name'])
                
                # 添加每个文件的反射率数据
                for file_name in file_names:
                    if file_name in self.data['reflectance']:
                        # 去掉文件扩展名
                        base_name = os.path.splitext(file_name)[0]
                        
                        reflectance_data = self.data['reflectance'][file_name]
                        reflectance_values = None
                        
                        # 尝试提取反射率数据
                        if isinstance(reflectance_data, dict):
                            if 'reflectance_1nm' in reflectance_data and len(reflectance_data['reflectance_1nm']) == len(wavelengths):
                                reflectance_values = reflectance_data['reflectance_1nm']
                            elif 'reflectance' in reflectance_data and len(reflectance_data['reflectance']) == len(wavelengths):
                                reflectance_values = reflectance_data['reflectance']
                        elif isinstance(reflectance_data, np.ndarray) and len(reflectance_data) == len(wavelengths):
                            reflectance_values = reflectance_data
                        
                        # 只添加长度匹配的数据，转换为列表以便JSON序列化
                        if reflectance_values is not None:
                            rho_data["samples"][base_name] = reflectance_values.tolist() if isinstance(reflectance_values, np.ndarray) else list(reflectance_values)
                
                # 添加反射率数据到主JSON对象
                json_data["reflectance"] = rho_data
            
            # 导出颜色数据
            if export_color:
                # 创建颜色数据部分
                color_data = {
                    "type": "Color Data",
                    "metadata": {
                        "num_samples": len(self.data['results'])
                    },
                    "samples": []
                }
                
                # 填充颜色数据
                for result in self.data['results']:
                    # 去掉文件扩展名
                    base_name = os.path.splitext(result['file_name'])[0]
                    
                    # RGB伽马值（0-255范围）
                    r_gamma = result['rgb_gamma'][0] * 255
                    if r_gamma > 255:
                        r_gamma = 255
                    
                    # 创建样本数据对象
                    sample = {
                        "file": base_name,
                        "coordinates": {
                            "x": result['x'],
                            "y": result['y']
                        },
                        "rgb_linear": {
                            "r": result['rgb_linear'][0],
                            "g": result['rgb_linear'][1],
                            "b": result['rgb_linear'][2]
                        },
                        "rgb_gamma": {
                            "r": int(r_gamma),
                            "g": int(result['rgb_gamma'][1] * 255),
                            "b": int(result['rgb_gamma'][2] * 255)
                        }
                    }
                    
                    # 添加样本到颜色数据
                    color_data["samples"].append(sample)
                
                # 添加颜色数据到主JSON对象
                json_data["color"] = color_data
            
            # 写入JSON文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"数据已成功导出到 {file_path}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出JSON文件失败: {e}")
            print(f"导出JSON文件失败: {e}")
            import traceback
            traceback.print_exc()
            return False 