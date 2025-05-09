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
from ui_plot_dialog import Ui_Dialog_plot


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
        
        # Initialize UI
        self.ui = Ui_Dialog_plot()
        self.ui.setupUi(self)
        
        # Set default filename and path
        default_dir = self.settings['export']['default_directory']
        default_filename = "plot.png"
        self.ui.lineEdit_Plot_File.setText(os.path.join(default_dir, default_filename))
        
        # Set default resolution - no longer from settings, use fixed value
        self.ui.comboBox_Plot_Resolution.setCurrentIndex(1)  # Default to 300 dpi (good)
        
        # Connect browse button signal
        self.ui.pushButton_Plot_Browse.clicked.connect(self.browse_file)
        
        # Connect confirmation button signals
        self.ui.buttonBox.accepted.connect(self.on_accepted)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        # Ensure at least one plot type is selected
        self.ui.checkBox_Plot_Reflectance.stateChanged.connect(self.check_selection)
        self.ui.checkBox_Plot_CIE.stateChanged.connect(self.check_selection)
        self.check_selection() # Initial check
    
    def check_selection(self):
        """Ensure at least one plot type is selected."""
        is_any_checked = self.ui.checkBox_Plot_Reflectance.isChecked() or self.ui.checkBox_Plot_CIE.isChecked()
        self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Ok).setEnabled(is_any_checked)
    
    def browse_file(self):
        """Browse and select the export file path."""
        current_path = self.ui.lineEdit_Plot_File.text()
        current_dir = os.path.dirname(current_path) if current_path else self.settings['export']['default_directory']
        
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
        
        # Get DPI setting - get corresponding DPI value from dropdown
        resolution_idx = self.ui.comboBox_Plot_Resolution.currentIndex()
        if resolution_idx == 0:
            dpi = 150  # draft
        elif resolution_idx == 1:
            dpi = 300  # good
        else:
            dpi = 600  # best
        
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
                
                # Get reflectance plot dimensions from settings
                width_px = self.settings['plot'].get('reflectance_width', 800)
                height_px = self.settings['plot'].get('reflectance_height', 600)
                
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
                    
                    # Adjust plot layout to ensure legend elements also scale proportionally
                    orig_fig.tight_layout(pad=1.1)  # Add a little padding to ensure elements are not clipped
                    
                    # Force redraw to update all elements
                    orig_fig.canvas.draw()
                    
                    # Save plot
                    orig_fig.savefig(
                        reflectance_file_path, 
                        dpi=dpi, 
                        bbox_inches='tight',
                        pad_inches=0.1  # Ensure there's enough space around the edge
                    )
                    
                    exported_files.append(reflectance_file_path)
                    print(f"Reflectance Plot exported to: {reflectance_file_path}")
                    
                finally:
                    # Restore original size and DPI
                    orig_fig.set_size_inches(orig_size)
                    orig_fig.set_dpi(orig_dpi)
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
                width_px = self.settings['plot'].get('cie_width', 600)
                height_px = self.settings['plot'].get('cie_height', 600)
                
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
                    
                    # Adjust plot layout to ensure legend elements also scale proportionally
                    orig_fig.tight_layout(pad=1.1)  # Add a little padding to ensure elements are not clipped
                    
                    # Force redraw to update all elements
                    orig_fig.canvas.draw()
                    
                    # Save plot
                    orig_fig.savefig(
                        cie_file_path, 
                        dpi=dpi, 
                        bbox_inches='tight',
                        pad_inches=0.1  # Ensure there's enough space around the edge
                    )
                    
                    exported_files.append(cie_file_path)
                    print(f"CIE Chromaticity Diagram exported to: {cie_file_path}")
                    
                finally:
                    # Restore original size and DPI
                    orig_fig.set_size_inches(orig_size)
                    orig_fig.set_dpi(orig_dpi)
                    # Restore original layout
                    orig_fig.tight_layout()
                    orig_fig.canvas.draw()
            
            # If export is successful
            if success and exported_files:
                # Save export directory to settings
                self.settings['export']['default_directory'] = file_dir
                # No longer save DPI to settings
                if self.parent:
                    self.parent.save_settings()
                
                # Show success message
                QMessageBox.information(self, "Success", f"Plots successfully exported to:\n{', '.join(exported_files)}")
                
                # Close dialog
                self.accept()
            else:
                QMessageBox.warning(self, "Export Error", "An error occurred during export")
        
        except Exception as e:
            print(f"Error during plot export: {e}")
            QMessageBox.critical(self, "Export Error", f"An error occurred during plot export: {e}")
            success = False
        
        if not success:
            QMessageBox.warning(self, "Export Error", "An error occurred during export") 