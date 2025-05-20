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
        Export dialog allowing users to select data types for export.
        
        Parameters:
            data: Data dictionary to export
            settings: Application settings
            parent: Parent window
        """
        super().__init__(parent)
        self.data = data
        self.settings = settings
        self.parent = parent
        self.setModal(True)  # Set as modal to prevent multiple instances
        
        # Initialize UI
        self.ui = Ui_Dialog_export()
        self.ui.setupUi(self)
        
        # 确保settings中有export_dialog部分
        if 'export_dialog' not in self.settings:
            self.settings['export_dialog'] = {}
        
        # Set default filename and path
        default_dir = self.settings['export'].get('last_directory', self.settings['export']['default_directory'])
        default_filename = "export_data.xlsx" # Default to Excel
        self.ui.lineEdit_Export_File.setText(os.path.join(default_dir, default_filename))
        
        # 从设置中加载上次的选择
        self.load_previous_selections()
        
        # Connect format change signal to update default extension
        self.ui.comboBox_Export_Format.currentIndexChanged.connect(self.update_default_extension)
        
        # Connect browse button signal
        self.ui.pushButton_Export_Browse.clicked.connect(self.browse_file)
        
        # Connect confirmation button signals
        self.ui.buttonBox.accepted.connect(self.on_accepted)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        # Ensure at least one data type is selected
        self.ui.checkBox_Export_Rho.stateChanged.connect(self.check_selection)
        self.ui.checkBox_Export_Color.stateChanged.connect(self.check_selection)
        self.check_selection() # Initial check
    
    def load_previous_selections(self):
        """从设置中加载上次的选择"""
        export_dialog_settings = self.settings.get('export_dialog', {})
        
        # 设置文件格式
        format_index = export_dialog_settings.get('format_index', 0)  # 默认为Excel (index 0)
        self.ui.comboBox_Export_Format.setCurrentIndex(format_index)
        
        # 设置选择的数据类型
        export_rho = export_dialog_settings.get('export_rho', True)
        export_color = export_dialog_settings.get('export_color', True)
        
        self.ui.checkBox_Export_Rho.setChecked(export_rho)
        self.ui.checkBox_Export_Color.setChecked(export_color)
        
        # 更新文件名扩展名以匹配选择的格式
        self.update_default_extension()
    
    def check_selection(self):
        """Ensure at least one data type is selected."""
        is_any_checked = self.ui.checkBox_Export_Rho.isChecked() or self.ui.checkBox_Export_Color.isChecked()
        self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Ok).setEnabled(is_any_checked)
        
    def update_default_extension(self):
        """Update the default extension in the file path based on the selected format."""
        current_path = self.ui.lineEdit_Export_File.text()
        if not current_path:
            current_path = os.path.join(self.settings['export']['default_directory'], "export_data")

        # Get the currently selected file format
        format_idx = self.ui.comboBox_Export_Format.currentIndex()
        if format_idx == 0:
            ext = ".xlsx"
        elif format_idx == 1:
            ext = ".csv"
        elif format_idx == 2:
            ext = ".txt"
        elif format_idx == 3:
            ext = ".json"
        else:
            ext = ".txt" # Fallback
            
        # Change the extension
        base_name = os.path.splitext(current_path)[0]
        self.ui.lineEdit_Export_File.setText(base_name + ext)
    
    def browse_file(self):
        """Open file selection dialog."""
        current_path = self.ui.lineEdit_Export_File.text()
        current_dir = os.path.dirname(current_path) if current_path else self.settings['export'].get('last_directory', self.settings['export']['default_directory'])
        
        # Get the currently selected file format
        format_idx = self.ui.comboBox_Export_Format.currentIndex()
        if format_idx == 0:
            filter_text = "Excel Files (*.xlsx)"
            ext = ".xlsx"
        elif format_idx == 1:
            filter_text = "CSV Files (*.csv)"
            ext = ".csv"
        elif format_idx == 2:
            filter_text = "Text Files (*.txt)"
            ext = ".txt"
        elif format_idx == 3:
            filter_text = "JSON Files (*.json)"
            ext = ".json"
        else:
            filter_text = "Text Files (*.txt)" # Fallback
            ext = ".txt"
        
        # Default filename based on current format
        default_filename = os.path.basename(self.ui.lineEdit_Export_File.text()) or f"export_data{ext}"
        
        # Open file selection dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Data", # Changed title
            os.path.join(current_dir, default_filename),
            filter_text
        )
        
        if file_path:
             # Ensure the correct extension is added if missing
            if not file_path.lower().endswith(ext):
                 file_path += ext
            self.ui.lineEdit_Export_File.setText(file_path)
            
            # 保存当前选择的目录
            self.settings['export']['last_directory'] = os.path.dirname(file_path)
    
    def on_accepted(self):
        """Handle the OK button click."""
        export_rho = self.ui.checkBox_Export_Rho.isChecked()
        export_color = self.ui.checkBox_Export_Color.isChecked()
        
        if not export_rho and not export_color:
            QMessageBox.warning(self, "Export Error", "Please select at least one data type to export.")
            return
        
        file_path = self.ui.lineEdit_Export_File.text()
        if not file_path:
            QMessageBox.warning(self, "Export Error", "Please specify an export file path.")
            return
        
        # Call the appropriate export function based on the selected format
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
            # 同时保存为最后使用的目录
            self.settings['export']['last_directory'] = os.path.dirname(file_path)
            
            # 保存当前选择到设置中
            self.settings['export_dialog']['format_index'] = format_idx
            self.settings['export_dialog']['export_rho'] = export_rho
            self.settings['export_dialog']['export_color'] = export_color
            
            # 同时更新默认格式
            self.settings['export']['default_format'] = ['xlsx', 'csv', 'txt', 'json'][format_idx]
            
            # 保存设置
            if self.parent:
                self.parent.save_settings()
            
            # 显示成功消息
            QMessageBox.information(self, "Success", f"Data successfully exported to {file_path}")
            
            # 关闭对话框
            self.accept()
        else:
             # If success is False, an error message should have been shown already by the export function
             # But as a fallback:
             if not any(QMessageBox.StandardButton.Ok == btn.standardButton() for btn in QMessageBox.question(self, "Error", "Export failed. Please check the file path and permissions.", QMessageBox.StandardButton.Ok).buttons()):
                  print("Export failed message shown.") # Fallback message if the other didn't show
    
    def export_to_excel(self, file_path, export_rho=True, export_color=True):
        """Export data to an Excel file, with selectable data types."""
        try:
            # Get original wavelength data
            wavelengths = self.data.get('original_wavelengths', None)
            if wavelengths is None and 'wavelengths' in self.data:
                wavelengths = self.data['wavelengths']
            
            if export_rho and wavelengths is None:
                # Use 5nm wavelengths as fallback if original not available
                if 'wavelengths' in self.data:
                    wavelengths = self.data['wavelengths']
                    print("Warning: Original wavelengths not found, using 5nm interpolated wavelengths for rho export.")
                else:
                    QMessageBox.critical(self, "Export Error", "Wavelength data not found. Cannot export reflectance data.")
                    return False
            
            # Get list of filenames
            file_names = []
            for result in self.data['results']:
                if result['file_name'] not in file_names:
                    file_names.append(result['file_name'])
            
            # Use openpyxl engine, create Excel write object
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                
                # Create and export reflectance data (if selected)
                if export_rho:
                    # Create reflectance data
                    rho_data = {'Lambda': wavelengths}
                    
                    # Add reflectance data for each file, remove extension
                    for file_name in file_names:
                        if file_name in self.data['reflectance']:
                            # Remove file extension
                            base_name = os.path.splitext(file_name)[0]
                            
                            reflectance_data = self.data['reflectance'][file_name]
                            reflectance_values = None
                            
                            # Try to extract reflectance data
                            if isinstance(reflectance_data, dict):
                                if 'reflectance_1nm' in reflectance_data and len(reflectance_data['reflectance_1nm']) == len(wavelengths):
                                    reflectance_values = reflectance_data['reflectance_1nm']
                                elif 'reflectance' in reflectance_data and len(reflectance_data['reflectance']) == len(wavelengths):
                                    reflectance_values = reflectance_data['reflectance']
                            elif isinstance(reflectance_data, np.ndarray) and len(reflectance_data) == len(wavelengths):
                                reflectance_values = reflectance_data
                            
                            # Only add data with matching length
                            if reflectance_values is not None:
                                rho_data[base_name] = reflectance_values
                    
                    # Create DataFrame and export
                    rho_df = pd.DataFrame(rho_data)
                    rho_df.to_excel(writer, index=False, header=True, sheet_name='rho')
                
                # Create and export color data (if selected)
                if export_color:
                    # Prepare color data
                    color_data = {
                        'Unnamed: 0': [],  # File name column
                        'x': [],
                        'y': [],
                        'R (lin)': [],
                        'G (lin)': [],
                        'B (lin)': [],
                        'R (gamma)': [],
                        'G (gamma)': [],
                        'B (gamma)': []
                    }
                    
                    # Fill data in order by file name
                    for i in range(min(3, len(self.data['results']))):
                        # Get result data
                        result = self.data['results'][i]
                        # Remove file extension
                        base_name = os.path.splitext(result['file_name'])[0]
                        
                        # File name and chromaticity coordinates
                        color_data['Unnamed: 0'].append(base_name)
                        color_data['x'].append(result['x'])
                        color_data['y'].append(result['y'])
                        
                        # RGB linear values - directly use calculation results
                        color_data['R (lin)'].append(result['rgb_linear'][0])
                        color_data['G (lin)'].append(result['rgb_linear'][1])
                        color_data['B (lin)'].append(result['rgb_linear'][2])
                        
                        # RGB gamma values (0-255 range) - directly use calculation results
                        # Note: R value needs to be truncated to 255, as shown in example file
                        r_gamma = round(result['rgb_gamma'][0] * 255)
                        if r_gamma > 255:
                            r_gamma = 255
                        
                        color_data['R (gamma)'].append(r_gamma)
                        color_data['G (gamma)'].append(round(result['rgb_gamma'][1] * 255))
                        color_data['B (gamma)'].append(round(result['rgb_gamma'][2] * 255))
                    
                    # Create DataFrame and export
                    color_df = pd.DataFrame(color_data)
                    color_df.to_excel(writer, index=False, header=True, sheet_name='color')
                
                # Get worksheet, apply format
                workbook = writer.book
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    
                    # Remove all cell formats
                    from openpyxl.styles import Font, Alignment, Border, Side
                    
                    # Create a normal font and alignment
                    normal_font = Font(name='Calibri', size=11, bold=False)
                    general_alignment = Alignment(horizontal='general', vertical='bottom')
                    no_border = Border(left=Side(style=None), right=Side(style=None), 
                                      top=Side(style=None), bottom=Side(style=None))
                    
                    # Apply to all cells
                    for row in worksheet.rows:
                        for cell in row:
                            cell.font = normal_font
                            cell.alignment = general_alignment
                            cell.border = no_border
            
            print(f"Data successfully exported to {file_path}")
            return True
        
        except Exception as e:
            QMessageBox.critical(self, "Excel Export Error", f"An error occurred while exporting to Excel: {e}")
            return False
    
    def export_to_csv(self, file_path, export_rho=True, export_color=True):
        """Export data to a CSV file, handling potential file access issues."""
        try:
            # Determine the separator based on settings
            separator = ',' if self.settings['export'].get('separator', 'Comma') == 'Comma' else '.'
            decimal = '.' if separator == ',' else ',' # Use opposite for decimal
            
            # Get original wavelength data
            wavelengths = self.data.get('original_wavelengths', None)
            if export_rho and wavelengths is None:
                # Use 5nm wavelengths as fallback if original not available
                if 'wavelengths' in self.data:
                    wavelengths = self.data['wavelengths']
                    print("Warning: Original wavelengths not found, using 5nm interpolated wavelengths for rho export.")
                else:
                    QMessageBox.critical(self, "Export Error", "Wavelength data not found. Cannot export reflectance data.")
                    return False
                
            # Get list of filenames
            file_names = []
            for result in self.data['results']:
                if result['file_name'] not in file_names:
                    file_names.append(result['file_name'])
            
            # Create CSV content
            csv_data = ""
            
            # Export reflectance data if selected
            if export_rho:
                # Create header row
                header = f"Lambda{separator}"
                for file_name in file_names:
                    # Remove file extension for column headers
                    base_name = os.path.splitext(file_name)[0]
                    header += f"{base_name}{separator}"
                csv_data += header.rstrip(separator) + "\n"
                
                # Add data rows
                for i, wavelength in enumerate(wavelengths):
                    row = f"{wavelength:.1f}{separator}"
                    for file_name in file_names:
                        if file_name in self.data['reflectance']:
                            reflectance_data = self.data['reflectance'][file_name]
                            reflectance_value = None
                            
                            # Try to extract reflectance data
                            if isinstance(reflectance_data, dict):
                                if 'reflectance_1nm' in reflectance_data and len(reflectance_data['reflectance_1nm']) > i:
                                    reflectance_value = reflectance_data['reflectance_1nm'][i]
                                elif 'reflectance' in reflectance_data and len(reflectance_data['reflectance']) > i:
                                    reflectance_value = reflectance_data['reflectance'][i]
                            elif isinstance(reflectance_data, np.ndarray) and len(reflectance_data) > i:
                                reflectance_value = reflectance_data[i]
                            
                            if reflectance_value is not None:
                                row += f"{reflectance_value:.6f}{separator}"
                            else:
                                row += f"0.000000{separator}"
                        else:
                            row += f"0.000000{separator}"
                    csv_data += row.rstrip(separator) + "\n"
            
            # Export color data if selected
            if export_color:
                # Add a separator line if both types are exported
                if export_rho:
                    csv_data += "\n"
                
                # Create header row for color data
                header = f"File{separator}x{separator}y{separator}"
                header += f"R (lin){separator}G (lin){separator}B (lin){separator}"
                header += f"R (gamma){separator}G (gamma){separator}B (gamma)"
                csv_data += header + "\n"
                
                # Add color data rows
                for result in self.data['results']:
                    # Remove file extension
                    base_name = os.path.splitext(result['file_name'])[0]
                    
                    # Create row with file name and chromaticity coordinates
                    row = f"{base_name}{separator}{result['x']:.6f}{separator}{result['y']:.6f}{separator}"
                    
                    # Add RGB linear values
                    row += f"{result['rgb_linear'][0]:.6f}{separator}"
                    row += f"{result['rgb_linear'][1]:.6f}{separator}"
                    row += f"{result['rgb_linear'][2]:.6f}{separator}"
                    
                    # Add RGB gamma values (0-255 range)
                    r_gamma = min(255, round(result['rgb_gamma'][0] * 255))
                    row += f"{r_gamma}{separator}"
                    row += f"{round(result['rgb_gamma'][1] * 255)}{separator}"
                    row += f"{round(result['rgb_gamma'][2] * 255)}"
                    
                    csv_data += row + "\n"
            
            # Write data to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(csv_data)
            
            print(f"Data successfully exported to {file_path}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "CSV Export Error", f"An error occurred while exporting to CSV: {e}")
            return False
    
    def export_to_txt(self, file_path, export_rho=True, export_color=True):
        """Export data to a TXT file, handling potential file access issues."""
        try:
            # Determine the separator based on settings
            separator = '\t'  # Use tab for TXT files
            decimal = '.'     # Always use period for decimal
            include_header = self.settings['export'].get('include_header', True)
            
            # Get original wavelength data
            wavelengths = self.data.get('original_wavelengths', None)
            if export_rho and wavelengths is None:
                # Use 5nm wavelengths as fallback if original not available
                if 'wavelengths' in self.data:
                    wavelengths = self.data['wavelengths']
                    print("Warning: Original wavelengths not found, using 5nm interpolated wavelengths for rho export.")
                else:
                    QMessageBox.critical(self, "Export Error", "Wavelength data not found. Cannot export reflectance data.")
                    return False
                
            # Get list of filenames
            file_names = []
            for result in self.data['results']:
                if result['file_name'] not in file_names:
                    file_names.append(result['file_name'])
            
            # Create TXT content
            txt_data = ""
            
            # Export reflectance data if selected
            if export_rho:
                # Create header row if enabled
                if include_header:
                    header = f"Lambda{separator}"
                    for file_name in file_names:
                        # Remove file extension for column headers
                        base_name = os.path.splitext(file_name)[0]
                        header += f"{base_name}{separator}"
                    txt_data += header.rstrip(separator) + "\n"
                
                # Add data rows
                for i, wavelength in enumerate(wavelengths):
                    row = f"{wavelength:.1f}{separator}"
                    for file_name in file_names:
                        if file_name in self.data['reflectance']:
                            reflectance_data = self.data['reflectance'][file_name]
                            reflectance_value = None
                            
                            # Try to extract reflectance data
                            if isinstance(reflectance_data, dict):
                                if 'reflectance_1nm' in reflectance_data and len(reflectance_data['reflectance_1nm']) > i:
                                    reflectance_value = reflectance_data['reflectance_1nm'][i]
                                elif 'reflectance' in reflectance_data and len(reflectance_data['reflectance']) > i:
                                    reflectance_value = reflectance_data['reflectance'][i]
                            elif isinstance(reflectance_data, np.ndarray) and len(reflectance_data) > i:
                                reflectance_value = reflectance_data[i]
                            
                            if reflectance_value is not None:
                                row += f"{reflectance_value:.6f}{separator}"
                            else:
                                row += f"0.000000{separator}"
                        else:
                            row += f"0.000000{separator}"
                    txt_data += row.rstrip(separator) + "\n"
            
            # Export color data if selected
            if export_color:
                # Add a separator line if both types are exported
                if export_rho:
                    txt_data += "\n"
                
                # Create header row for color data
                if include_header:
                    header = f"File{separator}x{separator}y{separator}"
                    header += f"R (lin){separator}G (lin){separator}B (lin){separator}"
                    header += f"R (gamma){separator}G (gamma){separator}B (gamma)"
                    txt_data += header + "\n"
                
                # Add color data rows
                for result in self.data['results']:
                    # Remove file extension
                    base_name = os.path.splitext(result['file_name'])[0]
                    
                    # Create row with file name and chromaticity coordinates
                    row = f"{base_name}{separator}{result['x']:.6f}{separator}{result['y']:.6f}{separator}"
                    
                    # Add RGB linear values
                    row += f"{result['rgb_linear'][0]:.6f}{separator}"
                    row += f"{result['rgb_linear'][1]:.6f}{separator}"
                    row += f"{result['rgb_linear'][2]:.6f}{separator}"
                    
                    # Add RGB gamma values (0-255 range)
                    r_gamma = min(255, round(result['rgb_gamma'][0] * 255))
                    row += f"{r_gamma}{separator}"
                    row += f"{round(result['rgb_gamma'][1] * 255)}{separator}"
                    row += f"{round(result['rgb_gamma'][2] * 255)}"
                    
                    txt_data += row + "\n"
            
            # Write data to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(txt_data)
            
            print(f"Data successfully exported to {file_path}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "TXT Export Error", f"An error occurred while exporting to TXT: {e}")
            return False
    
    def export_to_json(self, file_path, export_rho=True, export_color=True):
        """Export data to a JSON file."""
        try:
            export_data = {}
            
            # Get original wavelength data
            wavelengths = self.data.get('original_wavelengths', None)
            if export_rho and wavelengths is None:
                # Use 5nm wavelengths as fallback if original not available
                if 'wavelengths' in self.data:
                    wavelengths = self.data['wavelengths']
                    print("Warning: Original wavelengths not found, using 5nm interpolated wavelengths for rho export.")
                else:
                    QMessageBox.critical(self, "Export Error", "Wavelength data not found. Cannot export reflectance data.")
                    return False
                
            # Get list of filenames
            file_names = []
            for result in self.data['results']:
                if result['file_name'] not in file_names:
                    file_names.append(result['file_name'])
            
            # Prepare reflectance data if selected
            if export_rho:
                # Convert NumPy arrays to lists for JSON serialization
                wavelengths_list = wavelengths.tolist() if isinstance(wavelengths, np.ndarray) else list(wavelengths)
                export_data['wavelengths'] = wavelengths_list
                
                # Add reflectance data for each file
                reflectance_data = {}
                for file_name in file_names:
                    if file_name in self.data['reflectance']:
                        # Remove file extension
                        base_name = os.path.splitext(file_name)[0]
                        
                        # Extract reflectance values
                        ref_data = self.data['reflectance'][file_name]
                        if isinstance(ref_data, dict):
                            if 'reflectance_1nm' in ref_data and len(ref_data['reflectance_1nm']) == len(wavelengths):
                                values = ref_data['reflectance_1nm'].tolist() if isinstance(ref_data['reflectance_1nm'], np.ndarray) else list(ref_data['reflectance_1nm'])
                                reflectance_data[base_name] = values
                            elif 'reflectance' in ref_data and len(ref_data['reflectance']) == len(wavelengths):
                                values = ref_data['reflectance'].tolist() if isinstance(ref_data['reflectance'], np.ndarray) else list(ref_data['reflectance'])
                                reflectance_data[base_name] = values
                        elif isinstance(ref_data, np.ndarray) and len(ref_data) == len(wavelengths):
                            values = ref_data.tolist() if isinstance(ref_data, np.ndarray) else list(ref_data)
                            reflectance_data[base_name] = values
                
                export_data['reflectance'] = reflectance_data
            
            # Prepare color data if selected
            if export_color:
                color_data = []
                for result in self.data['results']:
                    # Remove file extension
                    base_name = os.path.splitext(result['file_name'])[0]
                    
                    # Format RGB values
                    rgb_linear = result['rgb_linear']
                    rgb_gamma = result['rgb_gamma']
                    
                    # Create color record
                    color_record = {
                        'file_name': base_name,
                        'x': result['x'],
                        'y': result['y'],
                        'rgb_linear': {
                            'r': rgb_linear[0],
                            'g': rgb_linear[1],
                            'b': rgb_linear[2]
                        },
                        'rgb_gamma': {
                            'r': min(1.0, rgb_gamma[0]),  # Cap at 1.0
                            'g': rgb_gamma[1],
                            'b': rgb_gamma[2]
                        },
                        'rgb_gamma_255': {
                            'r': min(255, int(rgb_gamma[0] * 255)),
                            'g': int(rgb_gamma[1] * 255),
                            'b': int(rgb_gamma[2] * 255)
                        },
                        'hex_color': result['hex_color']
                    }
                    
                    color_data.append(color_record)
                
                export_data['color'] = color_data
            
            # Add metadata
            export_data['metadata'] = {
                'export_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                'illuminant': self.settings['general']['illuminant'],
                'rho_lambda': self.settings['general']['rho_lambda'],
                'gamut': self.settings['general']['gamut']
            }
            
            # Write to JSON file
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"Data successfully exported to {file_path}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "JSON Export Error", f"An error occurred while exporting to JSON: {e}")
            return False 