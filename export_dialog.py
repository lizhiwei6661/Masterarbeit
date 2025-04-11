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
        
        # Set default filename and path
        default_dir = self.settings['export']['default_directory']
        default_filename = "export_data.xlsx" # Default to Excel
        self.ui.lineEdit_Export_File.setText(os.path.join(default_dir, default_filename))
        
        # Set default export format from settings
        default_format = self.settings['export'].get('default_format', 'xlsx').lower()
        if default_format == 'xlsx':
            self.ui.comboBox_Export_Format.setCurrentIndex(0)
        elif default_format == 'csv':
            self.ui.comboBox_Export_Format.setCurrentIndex(1)
        elif default_format == 'txt':
            self.ui.comboBox_Export_Format.setCurrentIndex(2)
        elif default_format == 'json':
            self.ui.comboBox_Export_Format.setCurrentIndex(3)
            
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
        current_dir = os.path.dirname(current_path) if current_path else self.settings['export']['default_directory']
        
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

            # Create CSV content
            # ... existing code ...
            
            # ... existing code ...
        except Exception as e:
            QMessageBox.critical(self, "CSV Export Error", f"An error occurred while exporting to CSV: {e}")
            return False
        return True
    
    def export_to_txt(self, file_path, export_rho=True, export_color=True):
        """Export data to a TXT file, handling potential file access issues."""
        try:
             # Determine the separator based on settings
            separator = ',' if self.settings['export'].get('separator', 'Comma') == 'Comma' else '.'
            decimal = '.' if separator == ',' else ',' # Use opposite for decimal
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

            # Create TXT content
            # ... existing code ...
            
            # ... existing code ...
        except Exception as e:
             QMessageBox.critical(self, "TXT Export Error", f"An error occurred while exporting to TXT: {e}")
             return False
        return True
    
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

            # Prepare reflectance data if selected
            # ... existing code ...
            
            # ... existing code ...
        except Exception as e:
             QMessageBox.critical(self, "JSON Export Error", f"An error occurred while exporting to JSON: {e}")
             return False
        return True 