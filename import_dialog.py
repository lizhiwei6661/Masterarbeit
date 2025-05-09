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
        
        # Set window title
        self.setWindowTitle("Import Data")

        # Initialize data storage
        self.black_reference_path = None
        self.white_reference_path = None
        self.black_reference_data = None
        self.white_reference_data = None
        self.measurement_files = []
        self.selected_measurements = []
        
        # Initialize data model
        self.file_model = QStandardItemModel()
        self.ui.listView_import_file.setModel(self.file_model)

        # Initialize matplotlib canvas - set a more suitable chart size
        self.figure = Figure(figsize=(5, 3.8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        # Remove top toolbar (menubar)
        # self.toolbar = NavigationToolbar(self.canvas, self)
        
        # Give view_spec some padding to make the canvas slightly smaller
        self.ui.view_spec.setContentsMargins(8, 8, 8, 8)
        
        # Create layout, clear default margins
        layout = QVBoxLayout(self.ui.view_spec)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # No longer add toolbar
        # layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # Configure chart initial layout - further increase bottom margins
        self.figure.subplots_adjust(left=0.18, right=0.92, bottom=0.22, top=0.92)
        
        # Initialize an empty chart to ensure axis labels are displayed
        self.initialize_empty_plot()
        
        # Add select/deselect all buttons
        self.select_buttons_layout = QHBoxLayout()
        self.select_all_button = QPushButton("Select All")
        self.deselect_all_button = QPushButton("Deselect All")
        self.select_buttons_layout.addWidget(self.select_all_button)
        self.select_buttons_layout.addWidget(self.deselect_all_button)
        
        # Create a container for these buttons
        self.select_buttons_widget = QWidget()
        self.select_buttons_widget.setLayout(self.select_buttons_layout)
        
        # Add buttons to the grid layout
        self.ui.gridLayout_3.addWidget(self.select_buttons_widget, 11, 1, 1, 1)
        
        # Rename OK button to Import Selected Data
        self.ui.buttonBox_import.button(self.ui.buttonBox_import.StandardButton.Ok).setText("Import Selected Data")

        # Initialize button state
        self.update_buttons_state()

        # Bind interaction events
        self.ui.comboBox_equp.currentIndexChanged.connect(self.update_buttons_state)
        self.ui.pushButton_black.clicked.connect(self.select_black_reference)
        self.ui.pushButton_white.clicked.connect(self.select_white_reference)
        self.ui.pushButton_clear_ref.clicked.connect(self.clear_reference)
        self.ui.pushButton_select_data.clicked.connect(self.select_measurements)
        self.select_all_button.clicked.connect(self.select_all_items)
        self.deselect_all_button.clicked.connect(self.deselect_all_items)
        
        # Connect dialog buttons
        self.ui.buttonBox_import.accepted.connect(self.accept)
        self.ui.buttonBox_import.rejected.connect(self.reject)
        
        # Initialize empty chart
        self.update_preview()

    def initialize_empty_plot(self):
        """Initialize an empty plot with axes and labels."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Set labels - consistent with update_preview
        ax.set_xlabel("Wavelength [nm]", fontsize=6)
        ax.set_ylabel("Spectral Irradiance [W/sqm*nm]", fontsize=6)
        ax.tick_params(axis='both', which='major', labelsize=5)
        
        # Set range
        ax.set_xlim(380, 780)
        ax.set_ylim(0, 1.0)
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.6)
        
        # Ensure labels are displayed
        self.figure.subplots_adjust(left=0.18, right=0.92, bottom=0.22, top=0.92)
        
        # Add blank data points to ensure chart initializes correctly
        ax.plot([380, 780], [0, 0], alpha=0)
        
        # Refresh canvas
        self.canvas.draw()

    def update_buttons_state(self):
        """
        Dynamically update button states based on the selected equipment type.
        """
        selected_equipment = self.ui.comboBox_equp.currentText()
        if selected_equipment == "Aleksameter":
            print("Aleksameter mode selected")
            self.ui.pushButton_black.setEnabled(True)
            self.ui.pushButton_white.setEnabled(True)
            self.ui.pushButton_clear_ref.setEnabled(True)
            # Check if reference files are selected
            self.check_references_selected()
        elif selected_equipment == "Generic":
            print("Generic mode selected")
            self.ui.pushButton_black.setEnabled(False)
            self.ui.pushButton_white.setEnabled(False)
            self.ui.pushButton_clear_ref.setEnabled(False)
            # Enable measurement data selection directly in Generic mode
            self.ui.pushButton_select_data.setEnabled(True)
            # Clear reference data
            self.black_reference_path = None
            self.white_reference_path = None
            # Clear preview plot
            self.figure.clear()
            self.canvas.draw()

    def check_references_selected(self):
        """
        Check if both black and white reference files are selected.
        If so, enable the measurement data selection button.
        """
        print(f"Black ref: {self.black_reference_path}, White ref: {self.white_reference_path}")
        if self.ui.comboBox_equp.currentText() == "Aleksameter":
            if self.black_reference_path and self.white_reference_path:
                self.ui.pushButton_select_data.setEnabled(True)
            else:
                self.ui.pushButton_select_data.setEnabled(False)

    def select_black_reference(self):
        """
        Select the black reference file.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Black Reference File", 
            self.get_import_directory(),
            "All Supported Files (*.csv *.txt *.mat);;CSV Files (*.csv);;Text Files (*.txt);;MATLAB Files (*.mat);;All Files (*.*)"
        )
        if file_path:
            print(f"Selected black reference: {file_path}")
            self.black_reference_path = file_path
            
            # Load data
            data = self.load_data_file(file_path)
            if data:
                self.black_reference_data = data  # Store data for preview
                self.update_preview()  # Update preview plot
                self.check_references_selected()
            else:
                QMessageBox.warning(self, "Error", f"Failed to load black reference file: {os.path.basename(file_path)}")
                self.black_reference_path = None # Reset path if loading failed
            
            # Remember directory for next time
            self.save_import_directory(os.path.dirname(file_path))

    def select_white_reference(self):
        """
        Select the white reference file.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select White Reference File", 
            self.get_import_directory(),
            "All Supported Files (*.csv *.txt *.mat);;CSV Files (*.csv);;Text Files (*.txt);;MATLAB Files (*.mat);;All Files (*.*)"
        )
        if file_path:
            print(f"Selected white reference: {file_path}")
            self.white_reference_path = file_path
            
            # Load data
            data = self.load_data_file(file_path)
            if data:
                self.white_reference_data = data  # Store data for preview
                self.update_preview()  # Update preview plot
                self.check_references_selected()
            else:
                QMessageBox.warning(self, "Error", f"Failed to load white reference file: {os.path.basename(file_path)}")
                self.white_reference_path = None # Reset path if loading failed
            
            # Remember directory for next time
            self.save_import_directory(os.path.dirname(file_path))

    def clear_reference(self):
        """
        Clear reference data.
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
        Select measurement data files.
        """
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Measurement Files", 
            self.get_import_directory(),
            "All Supported Files (*.csv *.txt *.mat);;CSV Files (*.csv);;Text Files (*.txt);;MATLAB Files (*.mat);;All Files (*.*)"
        )
        if file_paths:
            print(f"Selected measurements: {file_paths}")
            # Check if any files failed to load
            valid_files = []
            failed_files = []
            for fp in file_paths:
                data = self.load_data_file(fp)
                if data:
                    valid_files.append(fp)
                else:
                    failed_files.append(os.path.basename(fp))
            
            self.measurement_files = valid_files
            self.populate_file_list()
            self.update_preview()  # Update preview with loaded files
            
            if failed_files:
                QMessageBox.warning(self, "Warning", f"The following files could not be loaded or parsed:\n\n" + "\n".join(failed_files))
            
            # Remember directory for next time
            if self.measurement_files:
                self.save_import_directory(os.path.dirname(self.measurement_files[0]))

    def populate_file_list(self):
        """
        Fill file list and add checkboxes for each file.
        """
        print(f"Populating file list with {len(self.measurement_files)} files")
        self.file_model.clear()
        for file_path in self.measurement_files:
            file_name = os.path.basename(file_path)
            item = QStandardItem(file_name)
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Checked)  # Default selected
            item.setData(file_path, Qt.ItemDataRole.UserRole)  # Store full path
            self.file_model.appendRow(item)
        
        # Default all files are selected
        self.selected_measurements = self.measurement_files.copy()
        
        # Allow ListView items to be clicked to allow selection/deselection
        self.ui.listView_import_file.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self.ui.listView_import_file.clicked.connect(self.on_item_clicked)

    def on_item_clicked(self, index):
        """
        Handle list item click event
        """
        item = self.file_model.itemFromIndex(index)
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)
        
        # Update preview plot
        self.update_preview()

    def update_preview(self):
        """
        Update preview plot, display black and white reference and selected measurement data
        """
        # Clear chart
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Set smaller font size
        axis_label_size = 6  # Smaller axis labels
        tick_label_size = 6  # Tick labels
        legend_size = 6  # Chart legend font
        
        # Track successfully plotted data sets
        plot_count = 0  
        
        # Set axis labels - display even if no data
        ax.set_xlabel("Wavelength [nm]", fontsize=axis_label_size)
        ax.set_ylabel("Spectral Irradiance [W/sqm*nm]", fontsize=axis_label_size)
        
        # Ensure X axis labels are displayed, using settings from __init__
        self.figure.subplots_adjust(left=0.18, right=0.92, bottom=0.22, top=0.92)
        
        # Add grid lines
        ax.grid(True, linestyle='--', alpha=0.6)
        
        # Plot black reference data
        if self.black_reference_data:
            wavelengths = self.black_reference_data['wavelengths']
            values = self.black_reference_data['values']
            ax.plot(wavelengths, values, 'k-', label="Black Reference", linewidth=1.5)
            plot_count += 1
        
        # Plot white reference data
        if self.white_reference_data:
            wavelengths = self.white_reference_data['wavelengths']
            values = self.white_reference_data['values']
            ax.plot(wavelengths, values, 'k--', label="White Reference", linewidth=1.5)
            plot_count += 1
        
        # Plot selected measurement data (up to 3)
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
        
        # Add legend (if there is data)
        if plot_count > 0:
            ax.legend(loc='best', fontsize=legend_size, framealpha=0.7)
        
        # Set X axis range to visible light range
        ax.set_xlim(380, 780)
        
        # Display tick labels based on whether there is data
        if plot_count > 0:
            # There is data, display tick labels
            ax.tick_params(axis='both', which='major', labelsize=tick_label_size)
            
            # Y axis auto scale - use automatic scaling
            ax.autoscale(axis='y')
            # Ensure Y axis lower limit is 0 (unless there are negatives)
            y_min, y_max = ax.get_ylim()
            if y_min >= 0:
                ax.set_ylim(0, y_max)
        else:
            # No data, hide tick labels but keep axis
            ax.tick_params(axis='both', which='both', 
                          labelbottom=False, labelleft=False,  # Hide tick numbers
                          length=0)  # Hide tick lines
            
            # Use default range when there is no data
            ax.set_ylim(0, 1.0)
        
        # Refresh canvas
        self.canvas.draw()
        
        # Connect size change event to ensure adaptation
        try:
            self.canvas.mpl_disconnect(self._resize_id)
        except:
            pass
        self._resize_id = self.canvas.mpl_connect('resize_event', self._on_resize)

    def load_data_file(self, file_path):
        """
        Load data file, handle file type appropriately.
        """
        try:
            # Choose different load method based on file extension
            ext = os.path.splitext(file_path)[1].lower()
            
            # Handle CSV file (specifically for example format)
            if ext == '.csv':
                print(f"Loading CSV file: {file_path}")
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                # Find start of data section
                data_start_index = -1
                for i, line in enumerate(lines):
                    if line.startswith("Wavelength [nm],"):
                        data_start_index = i + 1
                        break
                
                if data_start_index >= 0:
                    print(f"Found data section starting at line {data_start_index}")
                    # Extract data
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
                        # Ensure using numpy arrays
                        return {
                            'wavelengths': np.array(wavelengths),
                            'values': np.array(values)
                        }
                
                # If above parsing fails, try regular CSV parsing
                try:
                    data = pd.read_csv(file_path)
                    if len(data.columns) >= 2:
                        print(f"Fallback to pandas: {data.shape[0]} rows, {data.shape[1]} columns")
                        # Ensure returning numpy arrays
                        return {
                            'wavelengths': np.array(data.iloc[:, 0].values),
                            'values': np.array(data.iloc[:, 1].values)
                        }
                except Exception as ex:
                    print(f"Pandas CSV read error: {ex}")
                
                return None
                
            # Handle TXT file
            elif ext == '.txt':
                print(f"Loading TXT file: {file_path}")
                try:
                    # Try using numpy's loadtxt
                    data = np.loadtxt(file_path)
                    if data.shape[1] >= 2:  # Ensure at least two columns
                        return {
                            'wavelengths': np.array(data[:, 0]),
                            'values': np.array(data[:, 1])
                        }
                except Exception as ex:
                    print(f"Numpy loadtxt error: {ex}")
                    
                # Try manual parsing
                try:
                    wavelengths = []
                    values = []
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            try:
                                # Try different delimiters
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
                
            # Handle other file types
            else:
                # Try using pandas to read
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
        except FileNotFoundError:
            QMessageBox.warning(self, "Import Error", f"File not found: {file_path}")
            return None
        except pd.errors.ParserError:
            QMessageBox.warning(self, "Import Error", f"Error parsing file: {file_path}. Ensure it is a valid CSV/TXT file with numeric data.")
            return None
        except ImportError:
            QMessageBox.critical(self, "Import Error", "Optional dependency 'scipy' not found. Cannot load .mat files.")
            return None
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"An unexpected error occurred while loading {file_path}: {e}")
            return None

    def select_all_items(self):
        """
        Select all items.
        """
        print("Selecting all items")
        for row in range(self.file_model.rowCount()):
            item = self.file_model.item(row)
            item.setCheckState(Qt.CheckState.Checked)
        
        # Update preview plot
        self.update_preview()
    
    def deselect_all_items(self):
        """
        Deselect all items.
        """
        print("Deselecting all items")
        for row in range(self.file_model.rowCount()):
            item = self.file_model.item(row)
            item.setCheckState(Qt.CheckState.Unchecked)
        
        # Update preview plot
        self.update_preview()
    
    def get_selected_measurements(self):
        """Get current selected measurement file list"""
        selected = []
        for row in range(self.file_model.rowCount()):
            item = self.file_model.item(row)
            if item.checkState() == Qt.CheckState.Checked:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                selected.append(file_path)
        return selected
    
    def accept(self):
        """
        Handle the OK button click.
        Validates data and accepts the dialog.
        """
        selected_equipment = self.ui.comboBox_equp.currentText()
        self.selected_measurements = self.get_selected_measurements()
        
        if selected_equipment == "Aleksameter":
            if not self.black_reference_path or not self.white_reference_path:
                QMessageBox.warning(self, "Missing Reference", "Please select both black and white reference files.")
                return
            if not self.selected_measurements:
                QMessageBox.warning(self, "Missing Measurements", "Please select at least one measurement file.")
                return
        elif selected_equipment == "Generic":
            if not self.selected_measurements:
                QMessageBox.warning(self, "Missing Measurements", "Please select at least one measurement file.")
                return
        
        print("Import dialog accepted.")
        super().accept()

    def get_import_directory(self):
        """Get import directory, use cached if available, otherwise return default directory"""
        # Try reading last import directory from settings
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
        
        # Default directory
        return os.path.expanduser('~')
    
    def save_import_directory(self, directory):
        """Save import directory to settings"""
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
        Get all selected data.
        """
        # Get selected measurement file list
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
        """Handle chart size change event"""
        # Update to use same bottom margins
        self.figure.subplots_adjust(left=0.18, right=0.92, bottom=0.22, top=0.92)
            
        # Redraw chart
        self.canvas.draw_idle()