import os
import json
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QLineEdit, QPushButton, QFileDialog,
    QDialogButtonBox, QFormLayout, QCheckBox, QMessageBox,
    QSpinBox, QGroupBox
)
from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
from ui_plot_dialog import Ui_Dialog_plot
import matplotlib


class PlotDialog(QDialog):
    def __init__(self, data, settings, parent=None):
        """
        Initialize the plot export dialog.
        
        Parameters:
            data: Dictionary containing data to plot, with keys:
                - reflectance: Reflectance data
                - wavelengths: Wavelength data
            settings: Application settings
            parent: Parent window
        """
        super().__init__(parent)
        self.setWindowTitle("Plot Export")
        self.resize(400, 300)
        
        # Store data and settings
        self.data = data
        self.settings = settings
        self.parent = parent
        
        # loaded字体设置
        self.font_settings = self.load_font_settings()
        
        # Initialize UI
        self.ui = Ui_Dialog_plot()
        self.ui.setupUi(self)
        
        # 确保settings中有plot_export部分
        if 'plot_export' not in self.settings:
            self.settings['plot_export'] = {}
        
        # Set default filename and path
        default_dir = self.settings['export'].get('last_plot_directory', self.settings['export']['default_directory'])
        default_filename = "plot.png"
        self.ui.lineEdit_Plot_File.setText(os.path.join(default_dir, default_filename))
        
        # Load last selection from settings
        self.load_previous_selections()
        
        # Connect browse button signal
        self.ui.pushButton_Plot_Browse.clicked.connect(self.browse_file)
        
        # Connect confirmation button signals
        self.ui.buttonBox.accepted.connect(self.on_accepted)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        # Connect format combo box change signal
        self.ui.comboBox_Plot_Format.currentIndexChanged.connect(self.update_filename_extension)
        
        # Ensure at least one plot type is selected
        self.ui.checkBox_Plot_Reflectance.stateChanged.connect(self.check_selection)
        self.ui.checkBox_Plot_CIE.stateChanged.connect(self.check_selection)
        self.check_selection() # Initial check
    
    def load_font_settings(self):
        """loaded字体Settings file"""
        # 默认字体设置
        default_settings = {
            "font_families": ["Arial", "Times New Roman", "Helvetica"],
            "default_font_family": "Arial",
            "font_sizes": {
                "Small": {
                    "title_size": 9.6,
                    "axis_label_size": 8,
                    "tick_label_size": 6.4,
                    "legend_size": 7.2
                },
                "Medium": {
                    "title_size": 12,
                    "axis_label_size": 10,
                    "tick_label_size": 8,
                    "legend_size": 9
                },
                "Large": {
                    "title_size": 14.4,
                    "axis_label_size": 12,
                    "tick_label_size": 9.6,
                    "legend_size": 10.8
                }
            },
            "dpi_scaling": {
                "150": 1.0,
                "300": 0.9,
                "600": 0.3
            }
        }
        
        # 尝试从文件loaded
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            font_settings_path = os.path.join(script_dir, 'font_settings.json')
            
            if os.path.exists(font_settings_path):
                with open(font_settings_path, 'r', encoding='utf-8') as f:
                    font_settings = json.load(f)
                print(f"Loaded font settings from {font_settings_path}")
                return font_settings
        except Exception as e:
            print(f"Error loading font settings: {str(e)}")
        
        # 如果loaded失败，返回默认设置
        print("Using default font settings")
        return default_settings
    
    def load_previous_selections(self):
        """Load previous user selections from settings."""
        plot_export_settings = self.settings['plot_export']
        
        # Settings file format
        format_index = plot_export_settings.get('format_index', 0)  # 默认为PNG (index 0)
        self.ui.comboBox_Plot_Format.setCurrentIndex(format_index)
        
        # 设置选择的图表类型
        export_reflectance = plot_export_settings.get('export_reflectance', True)
        export_cie = plot_export_settings.get('export_cie', True)
        
        self.ui.checkBox_Plot_Reflectance.setChecked(export_reflectance)
        self.ui.checkBox_Plot_CIE.setChecked(export_cie)
        
        # Update filename extension to match selected format
        self.update_filename_extension()
    
    def update_filename_extension(self):
        """更新文件名扩展名以匹配当前选择的格式"""
        current_path = self.ui.lineEdit_Plot_File.text()
        if not current_path:
            return
            
        # 获取当前文件名（不含扩展名）and目录
        dir_path = os.path.dirname(current_path)
        filename = os.path.basename(current_path)
        filename_base = os.path.splitext(filename)[0]
        
        # 获取当前选择的格式
        format_idx = self.ui.comboBox_Plot_Format.currentIndex()
        if format_idx == 0:
            ext = ".png"
        elif format_idx == 1:
            ext = ".jpg"
        elif format_idx == 2:
            ext = ".tif"
        else:
            ext = ".pdf"
        
        # 更新文件路径
        new_path = os.path.join(dir_path, filename_base + ext)
        self.ui.lineEdit_Plot_File.setText(new_path)
    
    def check_selection(self):
        """Ensure at least one plot type is selected."""
        is_any_checked = self.ui.checkBox_Plot_Reflectance.isChecked() or self.ui.checkBox_Plot_CIE.isChecked()
        self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Ok).setEnabled(is_any_checked)
    
    def browse_file(self):
        """Browse and select the export file path."""
        current_path = self.ui.lineEdit_Plot_File.text()
        current_dir = os.path.dirname(current_path) if current_path else self.settings['export'].get('last_plot_directory', self.settings['export']['default_directory'])
        
        # Get the currently selected file format
        format_idx = self.ui.comboBox_Plot_Format.currentIndex()
        if format_idx == 0:
            filter_text = "PNG Files (*.png)"
            ext = ".png"
        elif format_idx == 1:
            filter_text = "JPEG Files (*.jpg *.jpeg)" # Added *.jpeg
            ext = ".jpg"
        elif format_idx == 2:
            filter_text = "TIFF Files (*.tif *.tiff)" # Added *.tiff
            ext = ".tif"
        else:
            filter_text = "PDF Files (*.pdf)"
            ext = ".pdf"
        
        # Open file selection dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Plot", # Changed title to English
            os.path.join(current_dir, f"plot{ext}"),
            filter_text
        )
        
        if file_path:
            # Ensure the correct extension is added if missing
            if not file_path.lower().endswith(ext):
                 file_path += ext
            self.ui.lineEdit_Plot_File.setText(file_path)
            
            # Save currently selected directory
            self.settings['export']['last_plot_directory'] = os.path.dirname(file_path)
    
    def on_accepted(self):
        """Handle the OK button click."""
        export_reflectance = self.ui.checkBox_Plot_Reflectance.isChecked()
        export_cie = self.ui.checkBox_Plot_CIE.isChecked()
        
        if not export_reflectance and not export_cie:
            QMessageBox.warning(self, "Export Error", "Please select at least one plot type to export.")
            return
        
        file_path = self.ui.lineEdit_Plot_File.text()
        if not file_path:
            QMessageBox.warning(self, "Export Error", "Please specify an export file path.")
            return
        
        # Get the currently selected file format
        format_idx = self.ui.comboBox_Plot_Format.currentIndex()
        if format_idx == 0:
            file_ext = ".png"
        elif format_idx == 1:
             file_ext = ".jpg"
        elif format_idx == 2:
            file_ext = ".tif"
        else:
            file_ext = ".pdf"
            
        # Ensure correct extension
        if not file_path.lower().endswith(file_ext):
            file_path += file_ext
        
        # Get filename (without extension) and directory
        file_dir = os.path.dirname(file_path)
        file_name_base = os.path.splitext(os.path.basename(file_path))[0]
        
        # 保存最后使用的目录
        self.settings['export']['last_plot_directory'] = file_dir
        
        # 从settings中获取DPI设置值
        dpi = self.settings['plot'].get('reflectance_dpi', 300)  # 默认为300 dpi
        
        success = True
        exported_files = []

        try:
            # Export Reflectance Plot
            if export_reflectance and hasattr(self.parent, 'reflectance_figure'):
                # Determine the file path for the reflectance plot
                if export_cie:
                    reflectance_file_path = os.path.join(file_dir, f"{file_name_base}_reflectance{file_ext}")
                else:
                    reflectance_file_path = file_path # Use the main path if only exporting this one
                
                # Get reflectance plot dimensions from settings - 确保使用正确的默认值
                width_px = self.settings['plot'].get('reflectance_width', 1600)
                height_px = self.settings['plot'].get('reflectance_height', 800)
                
                # Calculate inches size
                width_inches = width_px / dpi
                height_inches = height_px / dpi
                
                print(f"Exporting Reflectance Plot: {width_px}x{height_px}px ({width_inches:.2f}x{height_inches:.2f} inches), DPI={dpi}")
                
                # Get original plot
                orig_fig = self.parent.reflectance_figure
                
                # Save current size for later restoration
                orig_size = orig_fig.get_size_inches()
                orig_dpi = orig_fig.dpi
                
                try:
                    # First update plot to ensure latest settings are applied
                    self.parent.update_reflectance_plot()
                    
                    # Temporary adjustment of plot size
                    orig_fig.set_size_inches(width_inches, height_inches)
                    orig_fig.set_dpi(dpi)
                    
                    # 从设置中读取字体配置
                    font_family = self.font_settings['default_font_family']
                    
                    # 根据字体大小设置获取具体的字号
                    reflectance_font_size = self.settings['plot'].get('reflectance_font_size', 'Medium')
                    
                    # 获取font_sizes配置中的具体值
                    font_sizes = self.font_settings['font_sizes']
                    font_size_config = font_sizes.get(reflectance_font_size, {})
                    
                    # 从配置中获取字体大小值，如果没有配置则使用默认值
                    title_size = font_size_config.get('title_size', 12)
                    axis_label_size = font_size_config.get('axis_label_size', 10)
                    tick_label_size = font_size_config.get('tick_label_size', 8)
                    legend_size = font_size_config.get('legend_size', 9)
                    
                    # 获取当前DPI对应的缩放比例
                    dpi_str = str(dpi)
                    if dpi_str in self.font_settings['dpi_scaling']:
                        scale_factor = self.font_settings['dpi_scaling'][dpi_str]
                    else:
                        # 对于600DPI特别Processing，强制使用较小的缩放值
                        if dpi >= 600:
                            scale_factor = 0.3
                        else:
                            scale_factor = dpi / 300.0
                    
                    print(f"Using scale factor: {scale_factor} for DPI: {dpi}")
                    
                    # 应用缩放比例
                    title_size = int(title_size * scale_factor)
                    axis_label_size = int(axis_label_size * scale_factor)
                    tick_label_size = int(tick_label_size * scale_factor)
                    legend_size = int(legend_size * scale_factor)
                    
                    # 调整所有子图的字体大小
                    for ax in orig_fig.get_axes():
                        # 调整标题and轴标签的字体大小
                        if ax.title.get_text():
                            ax.title.set_fontsize(title_size)
                            ax.title.set_fontfamily(font_family)
                        if ax.xaxis.label.get_text():
                            ax.xaxis.label.set_fontsize(axis_label_size)
                            ax.xaxis.label.set_fontfamily(font_family)
                        if ax.yaxis.label.get_text():
                            ax.yaxis.label.set_fontsize(axis_label_size)
                            ax.yaxis.label.set_fontfamily(font_family)
                        
                        # 调整刻度标签的字体大小
                        ax.tick_params(axis='both', which='major', labelsize=tick_label_size)
                        
                        # 调整刻度标签的字体系列
                        for label in ax.get_xticklabels() + ax.get_yticklabels():
                            label.set_fontfamily(font_family)
                        
                        # 如果有图例，调整图例字体大小
                        if ax.get_legend():
                            for text in ax.get_legend().get_texts():
                                text.set_fontsize(legend_size * scale_factor)
                                text.set_fontfamily(font_family)
                        
                        # 调整wavelength标签的大小 (380,400,420等)
                        for artist in ax.get_children():
                            # 检查是否为文本注释
                            if isinstance(artist, matplotlib.text.Annotation):
                                # 检查文本内容是否可能是wavelength标签(通常是3位数字)
                                text = artist.get_text()
                                if text.isdigit() and len(text) == 3:
                                    # wavelength标签使用与刻度标签相同的大小
                                    artist.set_fontsize(tick_label_size)
                                    artist.set_fontfamily(font_family)
                    
                    # Adjust plot layout to ensure legend elements also scale proportionally
                    orig_fig.tight_layout(pad=0.8)  # 减小边距，确保图表能更好地利用空间
                    
                    # Force redraw to update all elements
                    orig_fig.canvas.draw()
                    
                    # Save plot
                    orig_fig.savefig(
                        reflectance_file_path,
                        dpi=dpi,
                        bbox_inches='tight',  # 自动调整边界确保所有内容可见
                        pad_inches=0.25 * scale_factor  # 根据DPI调整边距
                    )
                    
                    exported_files.append(reflectance_file_path)
                    print(f"Reflectance Plot exported to: {reflectance_file_path}")
                    
                finally:
                    # Restore original size and DPI
                    orig_fig.set_size_inches(orig_size)
                    orig_fig.set_dpi(orig_dpi)
                    
                    # 恢复Original字体大小
                    for ax in orig_fig.get_axes():
                        # 恢复保存的Original字体大小
                        if ax.title.get_text():
                            ax.title.set_fontsize(10)  # 恢复到默认值
                        if ax.xaxis.label.get_text():
                            ax.xaxis.label.set_fontsize(8)  # 恢复到默认值
                        if ax.yaxis.label.get_text():
                            ax.yaxis.label.set_fontsize(8)  # 恢复到默认值
                        ax.tick_params(axis='both', which='major', labelsize=7)  # 恢复到默认值
                        
                        # 恢复图例字体
                        if ax.get_legend():
                            for text in ax.get_legend().get_texts():
                                text.set_fontsize(7)  # 恢复到默认值
                    
                    # Restore original layout
                    orig_fig.tight_layout()
                    orig_fig.canvas.draw()
            
            # Export CIE Chromaticity Diagram
            if export_cie and hasattr(self.parent, 'cie_figure'):
                # Determine the file path for the CIE plot
                if export_reflectance:
                    cie_file_path = os.path.join(file_dir, f"{file_name_base}_cie{file_ext}")
                else:
                    cie_file_path = file_path # Use the main path if only exporting this one
                
                # Get CIE plot dimensions from settings
                width_px = self.settings['plot'].get('cie_width', 900)
                height_px = self.settings['plot'].get('cie_height', 900)
                
                # 获取CIE图表的DPI
                dpi = self.settings['plot'].get('cie_dpi', 300)  # 默认为300 dpi
                
                # Calculate inches size
                width_inches = width_px / dpi
                height_inches = height_px / dpi
                
                print(f"Exporting CIE Plot: {width_px}x{height_px}px ({width_inches:.2f}x{height_inches:.2f} inches), DPI={dpi}")
                
                # Get original plot
                orig_fig = self.parent.cie_figure
                
                # Save current size for later restoration
                orig_size = orig_fig.get_size_inches()
                orig_dpi = orig_fig.dpi
                
                try:
                    # First update plot to ensure latest settings are applied
                    self.parent.update_cie_plot()
                    
                    # Temporary adjustment of plot size
                    orig_fig.set_size_inches(width_inches, height_inches)
                    orig_fig.set_dpi(dpi)
                    
                    # 从设置中读取字体配置
                    font_family = self.font_settings['default_font_family']
                    
                    # 根据字体大小设置获取具体的字号
                    cie_font_size = self.settings['plot'].get('cie_font_size', 'Medium')
                    
                    # 获取font_sizes配置中的具体值
                    font_sizes = self.font_settings['font_sizes']
                    font_size_config = font_sizes.get(cie_font_size, {})
                    
                    # 从配置中获取字体大小值，如果没有配置则使用默认值
                    title_size = font_size_config.get('title_size', 12)
                    axis_label_size = font_size_config.get('axis_label_size', 10)
                    tick_label_size = font_size_config.get('tick_label_size', 8)
                    legend_size = font_size_config.get('legend_size', 9)
                    
                    # 获取当前DPI对应的缩放比例
                    dpi_str = str(dpi)
                    if dpi_str in self.font_settings['dpi_scaling']:
                        scale_factor = self.font_settings['dpi_scaling'][dpi_str]
                    else:
                        # 对于600DPI特别Processing，强制使用较小的缩放值
                        if dpi >= 600:
                            scale_factor = 0.3
                        else:
                            scale_factor = dpi / 300.0
                    
                    print(f"Using scale factor: {scale_factor} for DPI: {dpi}")
                    
                    # 应用缩放比例
                    title_size = int(title_size * scale_factor)
                    axis_label_size = int(axis_label_size * scale_factor)
                    tick_label_size = int(tick_label_size * scale_factor)
                    legend_size = int(legend_size * scale_factor)
                    
                    # 调整所有子图的字体大小
                    for ax in orig_fig.get_axes():
                        # 调整标题and轴标签的字体大小
                        if ax.title.get_text():
                            ax.title.set_fontsize(title_size)
                            ax.title.set_fontfamily(font_family)
                        if ax.xaxis.label.get_text():
                            ax.xaxis.label.set_fontsize(axis_label_size)
                            ax.xaxis.label.set_fontfamily(font_family)
                        if ax.yaxis.label.get_text():
                            ax.yaxis.label.set_fontsize(axis_label_size)
                            ax.yaxis.label.set_fontfamily(font_family)
                        
                        # 调整刻度标签的字体大小
                        ax.tick_params(axis='both', which='major', labelsize=tick_label_size)
                        
                        # 调整刻度标签的字体系列
                        for label in ax.get_xticklabels() + ax.get_yticklabels():
                            label.set_fontfamily(font_family)
                        
                        # 如果有图例，调整图例字体大小
                        if ax.get_legend():
                            for text in ax.get_legend().get_texts():
                                text.set_fontsize(legend_size * scale_factor)
                                text.set_fontfamily(font_family)
                        
                        # 调整wavelength标签的大小 (380,400,420等)
                        for artist in ax.get_children():
                            # 检查是否为文本注释
                            if isinstance(artist, matplotlib.text.Annotation):
                                # 检查文本内容是否可能是wavelength标签(通常是3位数字)
                                text = artist.get_text()
                                if text.isdigit() and len(text) == 3:
                                    # wavelength标签使用与刻度标签相同的大小
                                    artist.set_fontsize(tick_label_size)
                                    artist.set_fontfamily(font_family)
                    
                    # Adjust plot layout to ensure legend elements also scale proportionally
                    orig_fig.tight_layout(pad=0.8)  # 减小边距，确保图表能更好地利用空间
                    
                    # Force redraw to update all elements
                    orig_fig.canvas.draw()
                    
                    # Save plot
                    orig_fig.savefig(
                        cie_file_path,
                        dpi=dpi,
                        bbox_inches='tight',  # 自动调整边界确保所有内容可见
                        pad_inches=0.25 * scale_factor  # 根据DPI调整边距
                    )
                    
                    exported_files.append(cie_file_path)
                    print(f"CIE Plot exported to: {cie_file_path}")
                    
                finally:
                    # Restore original size and DPI
                    orig_fig.set_size_inches(orig_size)
                    orig_fig.set_dpi(orig_dpi)
                    
                    # 恢复Original字体大小
                    for ax in orig_fig.get_axes():
                        # 恢复保存的Original字体大小
                        if ax.title.get_text():
                            ax.title.set_fontsize(10)  # 恢复到默认值
                        if ax.xaxis.label.get_text():
                            ax.xaxis.label.set_fontsize(8)  # 恢复到默认值
                        if ax.yaxis.label.get_text():
                            ax.yaxis.label.set_fontsize(8)  # 恢复到默认值
                        ax.tick_params(axis='both', which='major', labelsize=7)  # 恢复到默认值
                        
                        # 恢复图例字体
                        if ax.get_legend():
                            for text in ax.get_legend().get_texts():
                                text.set_fontsize(7)  # 恢复到默认值
                    
                    # Restore original layout
                    orig_fig.tight_layout()
                    orig_fig.canvas.draw()
        except Exception as e:
            print(f"Error exporting plots: {str(e)}")
            QMessageBox.critical(self, "Export Error", f"An error occurred during plot export: {str(e)}")
            success = False
        
        # Save current selections to settings
        self.settings['plot_export']['format_index'] = self.ui.comboBox_Plot_Format.currentIndex()
        self.settings['plot_export']['export_reflectance'] = export_reflectance
        self.settings['plot_export']['export_cie'] = export_cie
        
        if success:
            if len(exported_files) == 1:
                QMessageBox.information(self, "Export Successful", f"Plot exported to:\n{exported_files[0]}")
            else:
                exported_files_text = "\n".join(exported_files)
                QMessageBox.information(self, "Export Successful", f"Plots exported to:\n{exported_files_text}")
            
            self.accept()  # Close dialog only upon successful export 