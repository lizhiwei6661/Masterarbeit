import os
import sys
import numpy as np
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QTableWidgetItem,
    QHeaderView, QFileDialog, QMenu, QColorDialog, QVBoxLayout, QDialog, QPushButton, QWidget, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QAction, QColor, QPixmap, QIcon, QClipboard, QScreen
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.patches as patches
import scipy.interpolate as interp
import json
import matplotlib.ticker as ticker
import warnings
import colour
from colour.plotting.diagrams import plot_chromaticity_diagram_colours
from colour.plotting import plot_RGB_colourspaces_in_chromaticity_diagram_CIE1931

from ui_form import Ui_MainWindow
from import_dialog import ImportDialog
from export_dialog import ExportDialog
from plot_dialog import PlotDialog
from settings_dialog import SettingsDialog
from about_dialog import AboutDialog
from reflectance_data_dialog import ReflectanceDataDialog
from color_calculator import ColorCalculator
from cie_data_dialog import CIEDataDialog


class MainWindow(QMainWindow):
    def __init__(self):
        """Initialize main window"""
        super().__init__()
        
        # Initialize UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Set window title
        self.setWindowTitle("Aleksameter App")
        
        # Set initial window size
        self.resize(833, 660)  # Set to 833x660 size
        
        # Initialize default settings
        self.settings = self.get_default_settings()
        
        # Load settings from config file (will override default settings)
        self.load_settings()
        
        # Initialize color calculator
        self.color_calculator = ColorCalculator()
        
        # Set rho_lambda value
        self.color_calculator.set_rho_lambda(self.settings['general']['rho_lambda'])
        
        # Set illuminant type
        self.color_calculator.set_illuminant(self.settings['general']['illuminant'])
        
        # Initialize data
        self.reset_data()
        
        # Set up interface
        self.setup_ui()
        
        # Create menu actions
        self.connect_menu_actions()
        
        # Connect button actions
        self.connect_button_actions()
        
        # Initialize import data directory
        self.import_directory = self.settings['import'].get('default_directory', None)
        
        # Place window in center of screen
        center_point = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        fg = self.frameGeometry()
        fg.moveCenter(center_point)
        self.move(fg.topLeft())
        
        # Initialize dialog references to None
        self.reflectance_dialog = None
        self.cie_dialog = None
        
        # Initially disable Export and Plot menu options
        self.update_menu_state(False)
    
    def reset_data(self):
        """Reset data storage"""
        self.data = {
            'wavelengths': self.color_calculator.wavelengths,
            'original_wavelengths': None,  # Used to store original measurement wavelength data (usually 1nm interval)
            'reflectance': {},
            'results': [],
            'file_names': [],
            # Add new field to store original measurement data
            'raw_measurements': {}  # Format: {'file_name': {'values': original values, 'wavelengths': wavelengths}}
        }
        
        # Reset charts
        if hasattr(self, 'reflectance_canvas'):
            self.update_reflectance_plot()
        if hasattr(self, 'cie_canvas'):
            self.update_cie_plot()
        
        # Clear results table
        if hasattr(self, 'ui') and hasattr(self.ui, 'table_results'):
            self.ui.table_results.setRowCount(0)
            
        # Disable Export and Plot menu options
        self.update_menu_state(False)
    
    def setup_ui(self):
        """Set up UI components"""
        # Set up reflectance chart
        self.setup_reflectance_plot()
        
        # Set up CIE chart
        self.setup_cie_plot()
        
        # Set up results table
        self.setup_results_table()
    
    def setup_reflectance_plot(self):
        """Set up reflectance chart"""
        # Create chart - using wider aspect ratio
        self.reflectance_figure = Figure(figsize=(6.5, 3.5), dpi=100)
        self.reflectance_canvas = FigureCanvas(self.reflectance_figure)
        # Remove toolbar, users don't need this feature
        # self.reflectance_toolbar = NavigationToolbar(self.reflectance_canvas, self)
        
        # Reserve enough space for X-axis labels, reduce left/right margins to make chart wider
        self.reflectance_figure.subplots_adjust(bottom=0.17, left=0.07, right=0.95, top=0.88)
        
        # Create layout and add to view_Reflections, making it fill the entire widget
        self.reflectance_layout = QVBoxLayout(self.ui.view_Reflections)
        self.reflectance_layout.setContentsMargins(0, 0, 0, 0)  # Remove layout margins
        self.reflectance_layout.setSpacing(0)  # Remove element spacing
        # No longer add toolbar
        # self.reflectance_layout.addWidget(self.reflectance_toolbar)
        self.reflectance_layout.addWidget(self.reflectance_canvas)
        
        # Set canvas size policy to expand and fill available space
        self.reflectance_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Connect canvas resize event to ensure chart adapts to container
        self.reflectance_canvas.mpl_connect('resize_event', self._on_reflectance_resize)
        
        # Initial drawing
        self.update_reflectance_plot()
    
    def _on_reflectance_resize(self, event):
        """Handle reflectance chart resize event"""
        # Get current title display state
        show_title = self.settings['plot'].get('reflectance_show_title', True)
        
        # Adjust top margin based on title display state
        if show_title:
            self.reflectance_figure.subplots_adjust(bottom=0.2, top=0.85)
        else:
            self.reflectance_figure.subplots_adjust(bottom=0.2, top=0.92)
            
        # Adjust chart layout to ensure labels are visible
        self.reflectance_figure.tight_layout(pad=0.4)
        
        # Redraw
        self.reflectance_canvas.draw_idle()
    
    def setup_cie_plot(self):
        """Set up CIE chart"""
        # Create chart - using smaller size
        self.cie_figure = Figure(figsize=(3.0, 3.0), dpi=100)
        self.cie_canvas = FigureCanvas(self.cie_figure)
        # Remove navigation toolbar
        # self.cie_toolbar = NavigationToolbar(self.cie_canvas, self)
        
        # Create layout and add to view_colorSpace - remove margins for better space utilization
        self.cie_layout = QVBoxLayout(self.ui.view_colorSpace)
        self.cie_layout.setContentsMargins(0, 0, 0, 0)  # Set margins to 0
        self.cie_layout.setSpacing(0)  # Set component spacing to 0
        # self.cie_layout.addWidget(self.cie_toolbar)  # No longer add navigation toolbar
        self.cie_layout.addWidget(self.cie_canvas)
        
        # Change to adaptive size policy, allow chart to scale with container
        self.cie_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Initial drawing
        self.update_cie_plot()
        
        # Listen for resize events to adjust chart
        self.cie_canvas.mpl_connect('resize_event', self._on_cie_resize)
    
    def _on_cie_resize(self, event):
        """Handle CIE chart resize event"""
        # Adjust chart layout to ensure labels are visible
        self.cie_figure.tight_layout(pad=0.4)
        # Redraw
        self.cie_canvas.draw_idle()
    
    def setup_results_table(self):
        """Set up results table"""
        # Set table headers
        self.ui.table_results.setColumnCount(6)  # Increase to 6 columns, add color column
        self.ui.table_results.setHorizontalHeaderLabels([
            "CLR", "File Name", "x", "y", "sRGB Linear", "sRGB Gamma"
        ])
        
        # Get table header
        header = self.ui.table_results.horizontalHeader()
        
        # Set column resize mode
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # Color column adjustable
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)  # Filename column adjustable
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)  # x column
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)  # y column
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)  # sRGB Linear column
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)  # sRGB Gamma column
        
        # Set initial column widths - adapt to larger font
        self.ui.table_results.setColumnWidth(0, 30)   # Reduce color column width
        self.ui.table_results.setColumnWidth(1, 120)  # Reduce filename column width
        self.ui.table_results.setColumnWidth(2, 65)   # Reduce x column width
        self.ui.table_results.setColumnWidth(3, 65)   # Reduce y column width
        self.ui.table_results.setColumnWidth(4, 140)  # Reduce sRGB Linear column width
        self.ui.table_results.setColumnWidth(5, 140)  # Reduce sRGB Gamma column width
        
        # Set row height
        self.ui.table_results.verticalHeader().setDefaultSectionSize(20)  # Adjust row height to 20 pixels (more compact)
        self.ui.table_results.verticalHeader().setVisible(False)  # Hide vertical header
        
        # Set table style
        self.ui.table_results.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                font-size: 9pt;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 2px;
                font-size: 9pt;
                border: 1px solid #d0d0d0;
            }
            QTableWidget::item {
                padding: 2px;
            }
        """)
        
        # Set table properties
        self.ui.table_results.setAlternatingRowColors(True)
        self.ui.table_results.setSortingEnabled(True)
        self.ui.table_results.setSelectionBehavior(self.ui.table_results.SelectionBehavior.SelectRows)
        
        # Set initial column width adjustment
        QTimer.singleShot(100, self.adjust_table_columns)
    
    def connect_menu_actions(self):
        """Connect menu actions"""
        # File menu
        self.ui.actionImport.triggered.connect(self.open_import_dialog)
        self.ui.actionExport.triggered.connect(self.open_export_dialog)
        self.ui.actionPlot.triggered.connect(self.open_plot_dialog)
        self.ui.actionSettings.triggered.connect(self.open_settings_dialog)
        
        # Ensure Settings menu item displays correctly on macOS
        self.ui.actionSettings.setMenuRole(QAction.MenuRole.NoRole)
        
        # Edit menu
        self.ui.actionCopy_all_data.triggered.connect(self.copy_all_data)
        self.ui.actionClear.triggered.connect(self.clear_data)
        
        # Create illuminant submenu
        illuminant_menu = QMenu("Illuminant", self)
        self.ui.menu_edit.addMenu(illuminant_menu)
        
        # Add illuminant options
        self.illuminant_actions = {}
        for illuminant in ['D65', 'D50', 'A', 'E']:  # Add 'E' illuminant
            action = QAction(illuminant, self)
            action.setCheckable(True)
            action.setData(illuminant)
            if illuminant == self.settings['general']['illuminant']:
                action.setChecked(True)
            action.triggered.connect(self.change_illuminant)
            illuminant_menu.addAction(action)
            self.illuminant_actions[illuminant] = action
        
        # Create Gamut submenu
        gamut_menu = QMenu("Gamut", self)
        self.ui.menu_edit.addMenu(gamut_menu)
        
        # Add Gamut options
        self.gamut_actions = {}
        for gamut in ['None', 'sRGB', 'Adobe RGB', 'HTC VIVE Pro Eye', 'Meta Oculus Quest 1', 'Meta Oculus Quest 2', 'Meta Oculus Rift']:
            action = QAction(gamut, self)
            action.setCheckable(True)
            action.setData(gamut)
            if gamut == self.settings['general']['gamut']:
                action.setChecked(True)
            action.triggered.connect(self.change_gamut)
            gamut_menu.addAction(action)
            self.gamut_actions[gamut] = action
        
        # Help menu
        self.ui.actionAbout.triggered.connect(self.open_about_dialog)
        self.ui.actionManual.triggered.connect(self.open_manual)
    
    def connect_button_actions(self):
        """Connect button events"""
        self.ui.pushButton_show_Reflections_Data.clicked.connect(self.show_reflectance_data)
        self.ui.pushButton_copydata.clicked.connect(self.copy_table_data)
        self.ui.pushButton_show_CIE_Data.clicked.connect(self.show_cie_data)
        # Modify button text
        self.ui.pushButton_show_CIE_Data.setText("Show CIE Diagram")
    
    def get_settings_file_path(self):
        """Get absolute path of settings file (using user data directory)"""
        # Get user data directory
        if sys.platform == 'darwin':  # macOS
            user_data_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'Aleksameter')
        elif sys.platform == 'win32':  # Windows
            user_data_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'Aleksameter')
        else:  # Linux and other platforms
            user_data_dir = os.path.join(os.path.expanduser('~'), '.aleksameter')
        
        # Ensure directory exists
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
        
        # Complete settings file path
        settings_file = os.path.join(user_data_dir, "app_settings.json")
        print(f"Settings file path: {settings_file}")
        return settings_file
    
    def load_settings(self):
        """Load settings"""
        try:
            settings_file = self.get_settings_file_path()
            
            # Check if file exists and is not empty
            if os.path.exists(settings_file) and os.path.getsize(settings_file) > 0:
                with open(settings_file, 'r') as f:
                    loaded_settings = json.loads(f.read())
                
                # Get default settings as base
                default_settings = self.get_default_settings()
                
                # Create new settings dictionary starting from defaults
                complete_settings = default_settings.copy()
                
                # Override defaults with loaded settings
                for category in loaded_settings:
                    if category in complete_settings:
                        complete_settings[category].update(loaded_settings[category])
                    else:
                        complete_settings[category] = loaded_settings[category]
                
                # Apply complete settings
                self.settings = complete_settings
                print(f"Settings loaded from {settings_file}")
            else:
                print(f"Settings file {settings_file} does not exist or is empty, using default settings")
                # Use default settings
                self.settings = self.get_default_settings()
                # Create default settings file
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {str(e)}")
            import traceback
            traceback.print_exc()
            # Use default settings and create settings file
            self.settings = self.get_default_settings()
            self.save_settings()
    
    def save_settings(self):
        """Save settings"""
        try:
            settings_file = self.get_settings_file_path()
            
            # Ensure directory exists
            settings_dir = os.path.dirname(settings_file)
            if not os.path.exists(settings_dir):
                os.makedirs(settings_dir)
                
            with open(settings_file, 'w') as f:
                f.write(json.dumps(self.settings, indent=4))
            print(f"Settings saved to {settings_file}")
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def get_default_settings(self):
        """Get default settings"""
        return {
            'general': {
                'illuminant': 'D65',  # D65 is default illuminant
                'rgb_values': '0 ... 1',  # RGB values default to 0-1 decimals
                'rho_lambda': 0.989,  # rho_lambda defaults to 0.989
                'gamut': 'None'  # Default to not show gamut
            },
            'plot': {
                'reflectance_width': 1600,  # Set width to 1600
                'reflectance_height': 800,  # Set height to 800
                'cie_width': 900,  # Set width to 900
                'cie_height': 900,  # Set height to 900
                'reflectance_title': 'Reflectance Spectra of Measured Samples',
                'cie_title': 'CIE Chromaticity Diagram',
                'reflectance_show_title': True,
                'cie_show_title': True,
                'reflectance_show_legend': True,
                'cie_show_legend': True,
                'reflectance_color': '#1f77b4',  # Default blue
                
                # Add font size settings
                'reflectance_font_size': 'Medium',  # Default medium font size
                'cie_font_size': 'Medium',  # Default medium font size
                
                # Export chart font settings
                'export_font_family': 'Arial',
                'export_title_size': 12,
                'export_axis_label_size': 10,
                'export_tick_label_size': 8,
                'export_legend_size': 9,
                
                # Font scaling ratios for different DPIs
                'export_dpi_scaling': {
                    '150': 1.0,  # No scaling at 150DPI
                    '300': 0.9,  # Reduce 10% at 300DPI
                    '600': 0.8   # Reduce 20% at 600DPI
                }
            },
            'export': {
                'separator': 'Point',
                'copy_header': 'Yes',
                'default_directory': os.path.expanduser('~'),
                'default_format': 'xlsx',
                'include_header': True,
                'decimal_places': 6,
                'last_directory': os.path.expanduser('~'),
                'last_plot_directory': os.path.expanduser('~')
            },
            'import': {
                'default_directory': os.path.expanduser('~'),
                'black_reference_directory': os.path.expanduser('~'),
                'white_reference_directory': os.path.expanduser('~'),
                'measurement_directory': os.path.expanduser('~')
            },
            'plot_export': {
                'dpi_index': 1,  # Default 300 DPI (index 1)
                'format_index': 0,  # Default PNG format (index 0)
                'export_reflectance': True,
                'export_cie': True
            },
            'export_dialog': {
                'format_index': 0,  # Default Excel format (index 0)
                'export_rho': True,
                'export_color': True
            }
        }
    
    def open_import_dialog(self):
        """Open import dialog"""
        dialog = ImportDialog(self)
        result = dialog.exec()
        
        print(f"Import dialog result: {result}")
        
        # In PySide6, QDialog.Accepted value is 1
        if result == 1:  # QDialog.Accepted
            # Get import data
            import_data = dialog.get_selected_data()
            
            # Process data
            self.process_imported_data(import_data)
            
            # Show log message
            print(f"Import dialog accepted, processing data...")
        else:
            print("Import dialog cancelled")
            
    def process_imported_data(self, import_data):
        """Process imported data"""
        if not import_data or not 'mode' in import_data:
            print("Invalid import data, missing processing mode")
            QMessageBox.warning(self, "Warning", "Invalid import data. Please try again.")
            return
        
        mode = import_data['mode']
        black_reference_path = import_data.get('black_reference', '')
        white_reference_path = import_data.get('white_reference', '')
        measurement_paths = import_data.get('measurements', [])
        
        print(f"\n====== Processing Import Data ======")
        print(f"Mode: {mode}")
        print(f"Black reference file: {black_reference_path}")
        print(f"White reference file: {white_reference_path}")
        print(f"Number of measurement files: {len(measurement_paths)}")
        
        if not measurement_paths:
            QMessageBox.warning(self, "Warning", "No measurement files selected.")
            return
        
        # Reset data
        self.reset_data()
        
        # Set rho_lambda value from settings
        rho_lambda = self.settings['general']['rho_lambda']
        self.color_calculator.set_rho_lambda(rho_lambda)
        print(f"Set rho_lambda value to: {rho_lambda}")
        
        # Set illuminant type from settings
        illuminant = self.settings['general']['illuminant']
        self.color_calculator.set_illuminant(illuminant)
        print(f"Set light source type to: {illuminant}")
        
        # Set calibration mode
        if mode == "Aleksameter" and black_reference_path and white_reference_path:
            print(f"Aleksameter mode: Using black and white reference calibration")
            
            # Load black and white reference data
            black_ref = self.load_data_from_file(black_reference_path)
            white_ref = self.load_data_from_file(white_reference_path)
            
            if black_ref is None or white_ref is None:
                error_msg = "Cannot load reference files."
                print(f"Error: {error_msg}")
                QMessageBox.warning(self, "Warning", error_msg)
                return
                
            # Check if reference data is valid
            if 'wavelengths' not in black_ref or 'values' not in black_ref or 'wavelengths' not in white_ref or 'values' not in white_ref:
                error_msg = "Invalid reference file format."
                print(f"Error: {error_msg}")
                QMessageBox.warning(self, "Warning", error_msg)
                return
                
            # Set calibration mode
            print("Setting calibration mode...")
            self.color_calculator.set_calibration_mode(True, black_ref['values'], white_ref['values'])
            
            # Save black/white reference data for subsequent recalculation
            self.data['black_reference'] = black_ref
            self.data['white_reference'] = white_ref
        else:
            # Generic mode, no calibration used
            print(f"Generic mode: No calibration used")
            self.color_calculator.set_calibration_mode(False)
        
        # Load measurement data
        measurements = []
        self.data['file_names'] = []  # Clear filename list
        
        for path in measurement_paths:
            try:
                print(f"Loading measurement file: {os.path.basename(path)}")
                # Load data from file
                data = self.load_data_from_file(path)
                
                if data is None:
                    print(f"  Error: Unable to load file {path}")
                    continue
                    
                if 'wavelengths' not in data or 'values' not in data:
                    print(f"  Error: Invalid file format {path}")
                    continue
                
                print(f"  Successfully loaded: {len(data['wavelengths'])}data points, range: {min(data['wavelengths']):.1f}-{max(data['wavelengths']):.1f} nm")
                measurements.append(data)
                self.data['file_names'].append(os.path.basename(path))
                
                # Save original measurement data
                file_name = os.path.basename(path)
                self.data['raw_measurements'][file_name] = {
                    'values': data['values'].copy(),
                    'wavelengths': data['wavelengths'].copy()
                }
            except Exception as e:
                error_msg = f"Error loading file {path}: {str(e)}"
                print(f"Error: {error_msg}")
                QMessageBox.warning(self, "Warning", error_msg)
        
        if not measurements:
            QMessageBox.warning(self, "Warning", "No valid measurement files.")
            return
        
        print(f"Processing {len(measurements)} measurement files...")
        
        # Process each measurement data
        for i, measurement in enumerate(measurements):
            try:
                file_name = self.data['file_names'][i]
                wavelengths = measurement['wavelengths']
                values = measurement['values']
                
                # Save original wavelength data from first measurement
                if i == 0 and wavelengths is not None and len(wavelengths) > 0:
                    self.data['original_wavelengths'] = np.array(wavelengths)
                    print(f"Saved original wavelength data: range={min(wavelengths):.1f}-{max(wavelengths):.1f} nm, "
                          f"points={len(wavelengths)}, step={wavelengths[1]-wavelengths[0]:.1f}nm")
                
                print(f"\nProcessing measurement {i+1}/{len(measurements)} measurement: {file_name}")
                print(f"  wavelength range: {min(wavelengths):.1f}-{max(wavelengths):.1f} nm")
                print(f"  Number of data points: {len(wavelengths)}")
                
                # Calculate color parameters
                result = self.color_calculator.process_measurement(values, wavelengths)
                
                if result is None:
                    print(f"  Error: Processing failed, no result returned")
                    continue
                
                # Store reflectance data
                if 'reflectance' in result:
                    # Save complete result dictionary including original and 1nm step data
                    self.data['reflectance'][file_name] = result
                else:
                    print(f"  Warning: Result does not contain reflectance data")
                
                # Store results
                if 'xy' in result and 'rgb_linear' in result and 'rgb_gamma' in result and 'hex_color' in result:
                    self.data['results'].append({
                        'file_name': file_name,
                        'x': result['xy'][0],
                        'y': result['xy'][1],
                        'rgb_linear': result['rgb_linear'],
                        'rgb_gamma': result['rgb_gamma'],
                        'hex_color': result['hex_color']
                    })
                    
                    print(f"  Calculation result: xy coordinates=({result['xy'][0]:.4f}, {result['xy'][1]:.4f}), color={result['hex_color']}")
                else:
                    print(f"  Warning: Result missing necessary color data")
            
            except Exception as e:
                error_msg = f"Processing file {file_name} error: {str(e)}"
                print(f"Error: {error_msg}")
                import traceback
                traceback.print_exc()
                QMessageBox.warning(self, "Error", error_msg)
        
        if not self.data['results']:
            QMessageBox.warning(self, "Warning", "Unable to calculate any results.")
            return
            
        # Update interface
        print("Updating interface...")
        try:
            self.update_reflectance_plot()
            self.update_cie_plot()
            self.update_results_table()
            
            # Update extended CIE chart window (if open)
            if self.cie_dialog is not None and self.cie_dialog.isVisible():
                print("Updating extended CIE chart window...")
                self.update_expanded_cie_plot()
            
            # Show success message
            QMessageBox.information(self, "Import Complete", 
                                f"Successfully processed {len(self.data['results'])}/{len(measurements)} measurement files.")
                                
            # Enable Export and Plot menu options
            self.update_menu_state(True)
            
            # If reflectance data dialog is open, update its content
            if self.reflectance_dialog is not None and self.reflectance_dialog.isVisible():
                try:
                    displayed_wavelengths = self.data['original_wavelengths'] if self.data['original_wavelengths'] is not None else self.data['wavelengths']
                    
                    # Prepare dataset dictionary, correctly extract reflectance data
                    processed_datasets = {}
                    for name, reflectance_data in self.data['reflectance'].items():
                        # Check data format
                        if isinstance(reflectance_data, dict):
                            # Prioritize 1nm step data
                            if 'reflectance_1nm' in reflectance_data and len(reflectance_data['reflectance_1nm']) > 0:
                                processed_datasets[name] = reflectance_data['reflectance_1nm']
                            # Otherwise use original reflectance data
                            elif 'reflectance' in reflectance_data:
                                processed_datasets[name] = reflectance_data['reflectance']
                        else:
                            # Old format: direct data array
                            processed_datasets[name] = reflectance_data
                    
                    # Update dialog
                    self.reflectance_dialog.update_data(displayed_wavelengths, processed_datasets)
                    print("Reflectance data dialog updated")
                except Exception as e:
                    print(f"Error updating reflectance data dialog: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
        except Exception as e:
            error_msg = f"Update interface error: {str(e)}"
            print(f"Error: {error_msg}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Error", error_msg)
    
    def load_data_from_file(self, file_path):
        """Load data from file"""
        try:
            # Choose different loading methods based on file extension
            ext = os.path.splitext(file_path)[1].lower()
            
            # Process CSV files (specifically for example format)
            if ext == '.csv':
                print(f"Loading CSV file: {file_path}")
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                # Find where data section starts
                data_start_index = -1
                for i, line in enumerate(lines):
                    if line.startswith("Wavelength [nm],"):
                        data_start_index = i + 1
                        break
                
                if data_start_index >= 0:
                    print(f"Found data section at line{data_start_index}")
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
                        wavelengths_np = np.array(wavelengths)
                        values_np = np.array(values)
                        
                        # Print wavelength information
                        if len(wavelengths) > 1:
                            step = wavelengths[1] - wavelengths[0]
                            print(f"Extracted{len(wavelengths)}data points")
                            print(f"wavelength range: {wavelengths[0]}-{wavelengths[-1]}nm, step: {step}nm")
                            
                            # Check if wavelength is uniform
                            diff = np.diff(wavelengths_np)
                            if not np.allclose(diff, step, rtol=1e-3):
                                print("Warning: Wavelength step is not uniform!")
                                print(f"Min step: {np.min(diff)}nm, Max step: {np.max(diff)}nm")
                            
                            # Check value range
                            print(f"Value range: {np.min(values_np)}-{np.max(values_np)}")
                        
                        return {
                            'wavelengths': wavelengths_np,
                            'values': values_np
                        }
                
                # If above parsing fails, try regular CSV parsing
                print("Trying regular CSV parsing method...")
                try:
                    data = np.genfromtxt(file_path, delimiter=',', skip_header=1, names=True)
                    if data.size > 0:
                        # Try to find wavelength and value columns
                        col_names = data.dtype.names
                        wavelength_col = None
                        value_col = None
                        
                        # Try to match column names
                        for col in col_names:
                            col_lower = col.lower()
                            if 'wave' in col_lower or 'lambda' in col_lower or 'nm' in col_lower:
                                wavelength_col = col
                            elif 'value' in col_lower or 'reflectance' in col_lower or 'intensity' in col_lower:
                                value_col = col
                        
                        # If can't find suitable column names, use first two columns
                        if wavelength_col is None and len(col_names) > 0:
                            wavelength_col = col_names[0]
                        if value_col is None and len(col_names) > 1:
                            value_col = col_names[1]
                        
                        if wavelength_col and value_col:
                            wavelengths_np = data[wavelength_col]
                            values_np = data[value_col]
                            
                            # Print wavelength information
                            if len(wavelengths_np) > 1:
                                step = wavelengths_np[1] - wavelengths_np[0]
                                print(f"Using columns '{wavelength_col}' and '{value_col}'")
                                print(f"wavelength range: {wavelengths_np[0]}-{wavelengths_np[-1]}nm, step: {step}nm")
                                print(f"Value range: {np.min(values_np)}-{np.max(values_np)}")
                            
                            return {
                                'wavelengths': wavelengths_np,
                                'values': values_np
                            }
                except Exception as e:
                    print(f"Regular CSV parsing failed: {e}")
            
            # If other file type or CSV parsing failed
            print(f"Unsupported file type: {ext}")
            return None
            
        except Exception as e:
            print(f"Error loading file: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def update_reflectance_plot(self):
        """Update reflectance chart"""
        # Clear chart
        self.reflectance_figure.clear()
        
        # Create subplot
        ax = self.reflectance_figure.add_subplot(111)
        
        # Set title (based on settings)
        show_title = self.settings['plot'].get('reflectance_show_title', True)
        title_text = self.settings['plot'].get('reflectance_title', "Reflectance Spectra of Measured Samples")
        
        # Only show title when settings indicate to show
        if show_title:
            ax.set_title(title_text, fontsize=10)
        
        # Set other basic properties
        ax.set_xlabel("Wavelength (nm)", fontsize=8)  # Restore to original size
        ax.set_ylabel("$\\rho$", fontsize=8)  # Restore to original size
        ax.tick_params(axis='both', which='major', labelsize=7)  # Restore to original size
        
        # Set X-axis range
        ax.set_xlim(380, 780)
        
        # Set fixed tick positions including 50nm intervals and edge values
        tick_positions = [380, 400, 450, 500, 550, 600, 650, 700, 750, 780]
        ax.xaxis.set_major_locator(ticker.FixedLocator(tick_positions))
        
        # Enable grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Check if there's data to plot
        if self.data['reflectance']:
            max_reflectance = 0
            
            # Plot reflectance data
            for file_name, result_data in self.data['reflectance'].items():
                # Get wavelength and reflectance data
                if 'reflectance_1nm' in result_data and 'wavelengths_1nm' in result_data:
                    wavelengths = result_data['wavelengths_1nm']
                    reflectance = result_data['reflectance_1nm']
                else:
                    wavelengths = result_data['wavelengths'] if 'wavelengths' in result_data else self.data['wavelengths']
                    reflectance = result_data['reflectance']
                
                # Update maximum reflectance value
                if len(reflectance) > 0:
                    max_reflectance = max(max_reflectance, np.max(reflectance))
                
                # Handle data length mismatch
                if len(wavelengths) != len(reflectance):
                    try:
                        # Perform interpolation
                        source_wavelengths = np.linspace(wavelengths[0], wavelengths[-1], len(reflectance))
                        interp_func = interp.interp1d(source_wavelengths, reflectance, bounds_error=False, fill_value="extrapolate")
                        reflectance = interp_func(wavelengths)
                    except Exception as e:
                        print(f"Interpolation failed")
                        continue
                
                # Plot curve
                ax.plot(wavelengths, reflectance, label=file_name)
            
            # Adaptively adjust Y-axis range
            if max_reflectance > 0:
                if max_reflectance > 1.0:
                    # If reflectance > 1.0, set appropriate upper limit
                    ax.set_ylim(0, max_reflectance * 1.05)
                elif max_reflectance < 0.1:
                    # If max reflectance is very small, use more suitable upper limit
                    ax.set_ylim(0, max_reflectance * 1.5)
                else:
                    # If reflectance between 0.1-1.0, use standard setting
                    ax.set_ylim(0, min(1.05, max_reflectance * 1.2))
            else:
                # If no valid data, use default range
                ax.set_ylim(0, 1.05)
            
            # Add legend (if multiple curves)
            if len(self.data['reflectance']) > 1:
                # Decide whether to show legend based on settings
                show_legend = self.settings['plot'].get('reflectance_show_legend', True)
                if show_legend:
                    ax.legend(fontsize=7)
                    print("Show reflectance chart legend")
                else:
                    print("Reflectance chart legend has been set to not display")
            else:
                print("Only one curve, no need to display legend")
        else:
            # Use default range when no data
            ax.set_ylim(0, 1.05)
        
        # Adjust bottom margin to ensure X-axis labels show
        self.reflectance_figure.subplots_adjust(bottom=0.2)
        
        # Adjust chart layout to accommodate title show/hide state
        self.reflectance_figure.tight_layout(pad=0.4)
        
        # Refresh chart
        self.reflectance_canvas.draw()
    
    def update_cie_plot(self):
        """Update CIE chart using colour library to draw colored chromaticity diagram"""
        # Clear chart
        self.cie_figure.clear()
        
        # Create subplot
        ax = self.cie_figure.add_subplot(111)
        
        # Set default font size - restore original font size settings
        tick_size = 8
        label_size = 9
        wavelength_label_size = 6  # Use smaller font for wavelength labels
        
        # Check if there's data to plot
        has_data = len(self.data['results']) > 0
        
        # Enable axis background settings to ensure grid is behind all elements
        ax.set_axisbelow(True)
        
        try:
            # Disable warning messages
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # First draw colored background of chromaticity diagram
                plot_chromaticity_diagram_colours(
                    axes=ax,
                    diagram_colours="RGB",  # Use RGB color
                    method="CIE 1931",  # Use CIE 1931 method
                    standalone=False,  # Not standalone plotting
                    title=False,  # Don't use default title
                    bounding_box=(0, 0.8, 0, 0.9)  # Restore original settings
                )
                
                # Get spectral locus data points
                cmfs = colour.colorimetry.MSDS_CMFS['CIE 1931 2 Degree Standard Observer']
                XYZ = cmfs.values
                xy = colour.XYZ_to_xy(XYZ)
                wavelengths = cmfs.wavelengths
                
                # Create wavelength to coordinate mapping
                wavelength_dict = {wl: (x, y) for wl, (x, y) in zip(wavelengths, xy)}
                
                # Define wavelength range we want to mark (460-620nm, every 20nm)
                custom_wavelength_labels = list(range(460, 640, 20))
                
                # Create smooth boundary lines - use more interpolation points for smoother effect
                # Use scipy interpolation method
                from scipy.interpolate import interp1d
                
                # Create closed spectral locus point list (head-to-tail connection)
                # Spectral locus line
                x_locus = np.append(xy[..., 0], xy[0, 0])
                y_locus = np.append(xy[..., 1], xy[0, 1])
                
                # Create parameterized coordinates for interpolation
                t = np.linspace(0, 1, len(x_locus))
                
                # Create interpolation functions
                fx = interp1d(t, x_locus, kind='cubic')
                fy = interp1d(t, y_locus, kind='cubic')
                
                # Generate denser points for interpolation to make curves smoother
                t_new = np.linspace(0, 1, 1000)
                x_smooth = fx(t_new)
                y_smooth = fy(t_new)
                
                # Draw smooth spectral boundary lines with high zorder
                ax.plot(
                    x_smooth, 
                    y_smooth, 
                    color='black', 
                    linewidth=1.0,
                    solid_capstyle='round',
                    zorder=10
                )
                
                # Purple line - connect highest and lowest wavelength points
                purple_line = np.vstack([
                    [xy[-1, 0], xy[-1, 1]],  # Highest wavelength points
                    [xy[0, 0], xy[0, 1]]      # Lowest wavelength points
                ])
                
                # Draw purple line with dashed style
                ax.plot(
                    purple_line[:, 0], 
                    purple_line[:, 1], 
                    color='black', 
                    linewidth=1.0,
                    linestyle='--',
                    zorder=10
                )
                
                # Manually draw gamut ensuring use of thin black lines
                gamut = self.settings['general']['gamut']
                
                # Draw gamut boundaries - define corresponding vertices based on selected gamut
                if gamut == 'None':
                    # Don't draw gamut
                    pass
                elif gamut == 'sRGB':
                    # sRGB gamut vertices
                    r = (0.64, 0.33)
                    g = (0.30, 0.60)
                    b = (0.15, 0.06)
                elif gamut == 'Adobe RGB':
                    # Adobe RGB gamut vertices
                    r = (0.64, 0.33)
                    g = (0.21, 0.71)
                    b = (0.15, 0.06)
                elif gamut == 'HTC VIVE Pro Eye':
                    # HTC VIVE Pro Eye gamut vertices (precise values)
                    r = (0.6585, 0.3407)
                    g = (0.2326, 0.7119)
                    b = (0.1431, 0.0428)
                elif gamut == 'Meta Oculus Quest 1':
                    # Meta Oculus Quest 1 gamut vertices (precise values)
                    r = (0.6596, 0.3396)
                    g = (0.2395, 0.7069)
                    b = (0.1452, 0.0531)
                elif gamut == 'Meta Oculus Quest 2':
                    # Meta Oculus Quest 2 gamut vertices (precise values)
                    r = (0.6364, 0.3305)
                    g = (0.3032, 0.5938)
                    b = (0.1536, 0.0632)
                elif gamut == 'Meta Oculus Rift':
                    # Meta Oculus Rift gamut vertices (precise values)
                    r = (0.6690, 0.3300)
                    g = (0.2545, 0.7015)
                    b = (0.1396, 0.0519)
                else:
                    # Default to sRGB
                    r = (0.64, 0.33)
                    g = (0.30, 0.60)
                    b = (0.15, 0.06)
                
                # Only create and draw gamut polygon when gamut is not 'None'
                if gamut != 'None':
                    # Create closed polygon point list
                    x_points = [r[0], g[0], b[0], r[0]]
                    y_points = [r[1], g[1], b[1], r[1]]
                    
                    # Draw gamut boundary and add labels
                    ax.plot(x_points, y_points, 'k-', linewidth=1.5, label=gamut)
                
                # Draw currently used illuminant points
                illuminant = self.settings['general']['illuminant']
                
                # Common illuminant xy coordinates
                illuminant_coords = {
                    'D65': (0.3128, 0.3290),
                    'D50': (0.3457, 0.3585),
                    'A': (0.4476, 0.4074),
                    'E': (1/3, 1/3)  # Equal energy illuminant at (1/3, 1/3)
                }
                
                # Remove all possibly remaining marker points and text annotations (keep this code)
                for child in ax.get_children():
                    # Remove text annotations (wavelength numbers)
                    if hasattr(child, 'get_text') and child.get_text() and child.get_text().isdigit():
                        child.remove()
                    # Remove point markers, but not data points
                    if hasattr(child, 'get_marker') and child.get_marker() not in [None, 'None', ''] and child.get_zorder() < 30:
                        child.remove()
                
                # Draw illuminant points after removing marker points
                if illuminant in illuminant_coords:
                    # Get illuminant coordinates
                    x_illum, y_illum = illuminant_coords[illuminant]
                    
                    # Draw illuminant points using small hollow black points
                    ax.plot(x_illum, y_illum, 'o', color='black', markersize=4, markerfacecolor='none', markeredgewidth=0.8, zorder=50)
                    
                    # Add annotation at upper right of illuminant points with transparent background
                    ax.annotate(
                        f"{illuminant}",
                        (x_illum + 0.02, y_illum + 0.02),  # Offset ensures annotation is at upper right of points
                        fontsize=wavelength_label_size,  # Same font size as wavelength labels
                        color='black',
                        ha='left',  # Left align
                        va='bottom',  # Bottom align
                        zorder=50
                    )
                
                # Add 460-620nm wavelength marks on CIE boundary, ensure compact and beautiful
                for wl in custom_wavelength_labels:
                    if wl in wavelength_dict:
                        x, y = wavelength_dict[wl]
                        
                        # Get direction vector from point position to center point (1/3, 1/3)
                        center = np.array([1/3, 1/3])
                        point = np.array([x, y])
                        direction = point - center
                        
                        # Normalize and extend direction vector
                        direction = direction / np.linalg.norm(direction)
                        
                        # Adjust offset for specific wavelengths
                        if wl == 460:
                            # For 460nm, move upper left to avoid exceeding boundary
                            offset = np.array([-0.02, 0.02])
                        elif wl == 540:
                            # For 540nm, move more to upper right
                            offset = np.array([0.07, 0.03])
                        elif wl == 620:
                            # For 620nm, move more to upper right
                            offset = np.array([0.03, 0.05])
                        else:
                            # Other wavelengths use standard offset
                            offset = direction * 0.015
                        
                        # Draw small points
                        ax.plot(x, y, 'o', color='black', markersize=2, zorder=15)
                        
                        # Determine text alignment
                        h_align = 'left' if direction[0] > 0 else 'right'
                        v_align = 'bottom' if direction[1] > 0 else 'top'
                        
                        # Add wavelength labels with smaller font
                        ax.annotate(
                            f"{wl}",
                            (x + offset[0], y + offset[1]),
                            fontsize=wavelength_label_size,
                            color='black',
                            ha=h_align,
                            va=v_align,
                            zorder=15,
                            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.1')
                        )
                
        except Exception as e:
            # If colour library drawing fails, fallback to original method
            print(f"Colour library drawing failed, fallback to original method: {e}")
            self.draw_cie_boundary(ax)
        
        # Set title and axis labels
        # Set title (based on settings)
        show_title = self.settings['plot'].get('cie_show_title', True)
        title_text = self.settings['plot'].get('cie_title', "CIE 1931 Chromaticity Diagram")
        
        if show_title:
            ax.set_title(title_text, fontsize=label_size)
        
        ax.set_xlabel("x", fontsize=label_size)
        ax.set_ylabel("y", fontsize=label_size)
        
        # Set axis range - restore original range
        ax.set_xlim(0, 0.8)
        ax.set_ylim(0, 0.9)
        
        # Ensure coordinate axes show ticks (regardless of data availability)
        # X-axis ticks
        ax.set_xticks(np.arange(0, 0.9, 0.1))
        ax.tick_params(axis='x', which='major', labelsize=tick_size)
        
        # Y-axis ticks
        ax.set_yticks(np.arange(0, 1.0, 0.1))
        ax.tick_params(axis='y', which='major', labelsize=tick_size)
        
        # Always disable grid, ignore grid_enabled value in settings
        ax.grid(False)
        
        # If no data, skip subsequent steps
        if not has_data:
            # Adjust layout to ensure labels are visible
            self.cie_figure.tight_layout(pad=0.4)
            self.cie_canvas.draw()
            return
        
        # Draw chromaticity coordinate points
        print(f"Plotting {len(self.data['results'])} CIE coordinates")
        for result in self.data['results']:
            x, y = result['x'], result['y']
            hex_color = result['hex_color']
            file_name = result['file_name']
            print(f"  Plotting point: {file_name} at ({x:.4f}, {y:.4f})")
            # Set data points same size as illuminant points, use solid points, add labels for legend display
            ax.plot(x, y, 'o', color=hex_color, markersize=4, markeredgecolor='black', 
                   markeredgewidth=0.8, zorder=100, label=file_name)
        
        # Decide whether to show legend based on settings - including measurement points and gamut
        show_legend = self.settings['plot'].get('cie_show_legend', True)
        if show_legend:
            # Get legend object and set smaller font size
            legend = ax.legend(fontsize=6, loc='upper right', frameon=True,
                            bbox_to_anchor=(1.0, 1.0))
            if legend is not None:
                # Set legend box properties
                legend.set_frame_on(True)
                legend.set_title('')  # Remove legend title
                # Adjust legend size
                legend._legend_box.align = "right"
        else:
            # If set to not show legend, remove any existing legend
            legend = ax.get_legend()
            if legend is not None:
                legend.remove()
        
        # Adjust layout - use tight_layout instead of fixed adjustment parameters for better container adaptation
        self.cie_figure.tight_layout(pad=0.4)
        
        # Refresh canvas
        self.cie_canvas.draw()
    
    def draw_cie_boundary(self, ax):
        """Draw CIE 1931 chromaticity diagram boundary"""
        # Use simplified CIE 1931 chromaticity diagram boundary points
        boundary_x = [0.1740, 0.0000, 0.0000, 0.0332, 0.0648, 0.0919, 0.1390, 0.1738, 0.2080, 0.2586, 0.3230, 0.3962, 0.4400, 0.4699, 0.4999, 0.5140, 0.5295, 0.5482, 0.5651, 0.5780, 0.5832, 0.5800, 0.5672, 0.5314, 0.4649, 0.3652, 0.2615, 0.1740]
        boundary_y = [0.0049, 0.0000, 0.0100, 0.0380, 0.0650, 0.0910, 0.2080, 0.2737, 0.3344, 0.4077, 0.4964, 0.5574, 0.5800, 0.5888, 0.5991, 0.6039, 0.6089, 0.6128, 0.6150, 0.6160, 0.6160, 0.6155, 0.6123, 0.6030, 0.5657, 0.4679, 0.2624, 0.0049]
        
        # Draw boundary
        ax.plot(boundary_x, boundary_y, 'k-')
        
        # Fill range
        ax.fill(boundary_x, boundary_y, alpha=0.1, color='gray')
        
        # Draw white point
        ax.plot(0.3127, 0.3290, 'ko', markersize=6, label='D65')
        
        # Draw sRGB gamut (manually define vertices)
        srgb_r = (0.64, 0.33)
        srgb_g = (0.30, 0.60)
        srgb_b = (0.15, 0.06)
        srgb_x = [srgb_r[0], srgb_g[0], srgb_b[0], srgb_r[0]]
        srgb_y = [srgb_r[1], srgb_g[1], srgb_b[1], srgb_r[1]]
        ax.plot(srgb_x, srgb_y, 'r--', label=self.settings['general']['gamut'])
        
        # Set grid with default value check
        grid_enabled = True  # Default enable grid
        if 'plot' in self.settings:
            grid_enabled = self.settings['plot'].get('grid', True)
        ax.grid(grid_enabled)
    
    def update_results_table(self):
        """Update results table"""
        # Clear table
        self.ui.table_results.setRowCount(0)
        
        # Check if there's data to display
        if not self.data['results']:
            print("No results to display in table")
            return
        
        # Fill results
        print(f"Updating table with {len(self.data['results'])} results")
        
        # Get RGB value format settings
        rgb_format = self.settings['general']['rgb_values']
        
        for i, result in enumerate(self.data['results']):
            row_position = self.ui.table_results.rowCount()
            self.ui.table_results.insertRow(row_position)
            
            # Add color column
            color_item = QTableWidgetItem()
            color_item.setBackground(QColor(result['hex_color']))
            self.ui.table_results.setItem(row_position, 0, color_item)
            
            # Add filename
            file_item = QTableWidgetItem(result['file_name'])
            self.ui.table_results.setItem(row_position, 1, file_item)
            
            # Add x coordinate
            x_item = QTableWidgetItem(f"{result['x']:.6f}")
            x_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.ui.table_results.setItem(row_position, 2, x_item)
            
            # Add y coordinate
            y_item = QTableWidgetItem(f"{result['y']:.6f}")
            y_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.ui.table_results.setItem(row_position, 3, y_item)
            
            # Add linear sRGB
            rgb_linear = result['rgb_linear']
            rgb_linear_str = f"({rgb_linear[0]:.4f}, {rgb_linear[1]:.4f}, {rgb_linear[2]:.4f})"
            rgb_linear_item = QTableWidgetItem(rgb_linear_str)
            rgb_linear_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.ui.table_results.setItem(row_position, 4, rgb_linear_item)
            
            # Add gamma-corrected sRGB, format according to settings
            rgb_gamma = result['rgb_gamma']
            
            if rgb_format == '0 ... 255':
                # Format to 0-255 range
                r_gamma = rgb_gamma[0] * 255
                g_gamma = rgb_gamma[1] * 255
                b_gamma = rgb_gamma[2] * 255
                rgb_gamma_str = f"({int(r_gamma) if r_gamma <= 255 else 255}, {int(g_gamma) if g_gamma <= 255 else 255}, {int(b_gamma) if b_gamma <= 255 else 255})"
            else:  # '0 ... 1'
                # Keep 0-1 range
                rgb_gamma_str = f"({rgb_gamma[0]:.4f}, {rgb_gamma[1]:.4f}, {rgb_gamma[2]:.4f})"
            
            rgb_gamma_item = QTableWidgetItem(rgb_gamma_str)
            rgb_gamma_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.ui.table_results.setItem(row_position, 5, rgb_gamma_item)
        
        # Adjust table column widths
        self.adjust_table_columns()
        
        print("Table updated successfully")
    
    def open_export_dialog(self):
        """Open export dialog"""
        if not self.data['results']:
            QMessageBox.warning(self, "Warning", "No data to export.")
            return
        
        dialog = ExportDialog(self.data, self.settings, self)
        # Execute dialog directly
        dialog.exec()
        # Dialog handles export logic internally
    
    def open_plot_dialog(self):
        """Open plot export dialog"""
        # Check if there's data available for export
        if not hasattr(self, 'reflectance_figure') or not hasattr(self, 'cie_figure'):
            QMessageBox.warning(self, "Warning", "No charts available.")
            return
        
        # Create and show plot export dialog
        dialog = PlotDialog(self.data, self.settings, self)
        dialog.exec()
    
    def open_settings_dialog(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self, self.settings)
        if dialog.exec():
            # If user clicks "OK", update settings (but preserve those not in dialog)
            new_settings = dialog.get_settings()
            
            # Update existing settings rather than complete replacement
            for category in new_settings:
                if category in self.settings:
                    self.settings[category].update(new_settings[category])
                else:
                    self.settings[category] = new_settings[category]
            
            # Save settings
            self.save_settings()
            # Apply settings
            self.apply_settings()
            # If necessary, recalculate results
            self.recalculate_results()
    
    def apply_settings(self):
        """Apply settings"""
        # Apply illuminant settings
        illuminant = self.settings['general']['illuminant']
        self.color_calculator.set_illuminant(illuminant)
        
        # Apply rho_lambda setting
        rho_lambda = self.settings['general']['rho_lambda']
        self.color_calculator.set_rho_lambda(rho_lambda)
        print(f"Apply rho_lambda setting: {rho_lambda}")
        
        # Update menu selection state
        if hasattr(self, 'illuminant_actions'):
            for name, action in self.illuminant_actions.items():
                action.setChecked(name == illuminant)
        
        # Apply gamut settings
        gamut = self.settings['general']['gamut']
        if hasattr(self, 'gamut_actions'):
            for name, action in self.gamut_actions.items():
                action.setChecked(name == gamut)
        
        # Regardless of data availability, immediately update reflectance and CIE charts to apply new title and display settings
        if hasattr(self, 'reflectance_canvas'):
            print("Immediately update reflectance chart to apply new settings...")
            
            # First save current size
            if hasattr(self, 'reflectance_figure'):
                orig_size = self.reflectance_figure.get_size_inches()
                
            # Update chart
            self.update_reflectance_plot()
            
            # Ensure layout adapts (especially important for title show/hide)
            if hasattr(self, 'reflectance_figure'):
                # Apply tight_layout to ensure all elements are visible and well-laid-out
                self.reflectance_figure.tight_layout(pad=0.4)
                # Reset to original size to prevent size drift
                if 'orig_size' in locals():
                    self.reflectance_figure.set_size_inches(orig_size)
                # Force complete redraw
                self.reflectance_canvas.draw()
            
        # Update CIE chart display to ensure illuminant points display correctly
        if hasattr(self, 'cie_canvas'):
            self.update_cie_plot()
            
        # If extended CIE chart window is open, also update it
        if hasattr(self, 'cie_dialog') and self.cie_dialog is not None and self.cie_dialog.isVisible():
            print("Update extended CIE chart to apply new settings...")
            self.update_expanded_cie_plot()
        
        # Check if calculation results already exist, if so and no recalculation needed, directly update table
        if self.data['results'] and self.settings['general'].get('rgb_values') is not None:
            # If only RGB format changed, no recalculation needed, just update table
            self.update_results_table()
        
        # Only recalculate when original data exists and setting changes require recalculation
        if self.data['raw_measurements'] and (illuminant != self.color_calculator.illuminant or 
                                             rho_lambda != self.color_calculator.rho_lambda):
            print("Setting changes require recalculating color values...")
            self.recalculate_results()
        else:
            print("No need to recalculate data")
    
    def recalculate_results(self):
        """Recalculate all results using original measurement data"""
        if not self.data['raw_measurements']:
            print("No original measurement data, cannot recalculate")
            return
        
        # Clear current results
        self.data['results'] = []
        
        # Ensure resetting calibration mode (if calibration was used before)
        if 'black_reference' in self.data and 'white_reference' in self.data:
            black_ref = self.data['black_reference']
            white_ref = self.data['white_reference']
            self.color_calculator.set_calibration_mode(True, black_ref['values'], white_ref['values'])
            print("Resetting calibration mode")
        
        # Recalculate each dataset
        for file_name, raw_data in self.data['raw_measurements'].items():
            # Get wavelength and measurement values from original measurement data
            wavelengths = raw_data['wavelengths']
            values = raw_data['values']
            
            print(f"Recalculating using original measurement data:'{file_name}': wavelength range={wavelengths[0]}-{wavelengths[-1]}nm, "
                  f"points={len(wavelengths)}, step={wavelengths[1]-wavelengths[0]}nm")
            
            # Calculate color parameters
            result = self.color_calculator.process_measurement(values, wavelengths)
            
            # Update stored reflectance data
            self.data['reflectance'][file_name] = result
            
            # Store results
            self.data['results'].append({
                'file_name': file_name,
                'x': result['xy'][0],
                'y': result['xy'][1],
                'rgb_linear': result['rgb_linear'],
                'rgb_gamma': result['rgb_gamma'],
                'hex_color': result['hex_color']
            })
        
        # Update interface
        self.update_reflectance_plot()
        self.update_cie_plot()
        self.update_results_table()
        
        # Update extended CIE chart window (if open)
        if self.cie_dialog is not None and self.cie_dialog.isVisible():
            print("After recalculation, updating extended CIE chart window...")
            self.update_expanded_cie_plot()
        
        print(f"Successfully recalculated {len(self.data['results'])} results")
    
    def open_about_dialog(self):
        """Open about dialog"""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def get_resource_path(self, relative_path):
        """
        Get absolute path of resource file, suitable for development environment and PyInstaller packaging environment
        
        Parameters:
            relative_path: Relative path
            
        Returns:
            Absolute path
        """
        try:
            # PyInstaller creates temporary folder, stores path in _MEIPASS
            base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
            return os.path.join(base_path, relative_path)
        except Exception as e:
            print(f"Error getting resource path: {str(e)}")
            return relative_path

    def open_manual(self):
        """Open user manual in default browser"""
        import webbrowser
        import os
        
        # Get the path to the user guide HTML file
        user_guide_path = self.get_resource_path("Aleksameter_User_Guide.html")
        
        if os.path.exists(user_guide_path):
            # Convert to file URL for cross-platform compatibility
            file_url = f"file://{os.path.abspath(user_guide_path)}"
            try:
                webbrowser.open(file_url)
                print(f"Opening user guide: {file_url}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open user guide in browser:\n{str(e)}")
        else:
            # Fallback: try to open online version or show error
            QMessageBox.information(
                self, 
                "User Guide", 
                "User guide file not found. Please ensure Aleksameter_User_Guide.html is in the application directory."
            )
    
    def change_illuminant(self):
        """Change illuminant settings"""
        action = self.sender()
        if not action.isChecked():
            # Prevent deselection
            action.setChecked(True)
            return
        
        # Get selected illuminant
        illuminant = action.data()
        
        # Update selection state of other illuminant options
        for name, act in self.illuminant_actions.items():
            if name != illuminant:
                act.setChecked(False)
        
        # Update settings
        self.settings['general']['illuminant'] = illuminant
        self.color_calculator.set_illuminant(illuminant)
        
        # Update CIE chart display to ensure illuminant points display correctly
        self.update_cie_plot()
        
        # Recalculate and update display
        self.recalculate_results()
        
        print(f"Switched light source to: {illuminant}")
    
    def change_gamut(self):
        """Change gamut settings"""
        action = self.sender()
        if not action.isChecked():
            # Prevent deselection
            action.setChecked(True)
            return
        
        # Get selected gamut
        gamut = action.data()
        
        # Update selection state of other gamut options
        for name, act in self.gamut_actions.items():
            if name != gamut:
                act.setChecked(False)
        
        # Update settings
        self.settings['general']['gamut'] = gamut
        
        # Currently no need to recalculate, but may need to update display
        self.update_cie_plot()
        
        # If extended CIE chart window is open, also update it
        if self.cie_dialog is not None and self.cie_dialog.isVisible():
            self.update_expanded_cie_plot()
    
    def copy_all_data(self):
        """Copy all data to clipboard"""
        if not self.data['results']:
            QMessageBox.warning(self, "Warning", "No data to copy.")
            return
        
        # Get RGB value format settings
        rgb_format = self.settings['general']['rgb_values']
        
        # Build table data string
        text = "File Name\tx\ty\tsRGB linear\tsRGB gamma\tHex Color\n"
        
        for result in self.data['results']:
            rgb_linear = result['rgb_linear']
            rgb_gamma = result['rgb_gamma']
            
            # Format RGB gamma values according to settings
            if rgb_format == '0 ... 255':
                # Format to 0-255 range
                r_gamma = rgb_gamma[0] * 255
                g_gamma = rgb_gamma[1] * 255
                b_gamma = rgb_gamma[2] * 255
                rgb_gamma_str = f"({int(r_gamma) if r_gamma <= 255 else 255}, {int(g_gamma) if g_gamma <= 255 else 255}, {int(b_gamma) if b_gamma <= 255 else 255})"
            else:  # '0 ... 1'
                # Keep 0-1 range
                rgb_gamma_str = f"({rgb_gamma[0]:.4f}, {rgb_gamma[1]:.4f}, {rgb_gamma[2]:.4f})"
            
            row = [
                result['file_name'],
                f"{result['x']:.6f}",
                f"{result['y']:.6f}",
                f"({rgb_linear[0]:.4f}, {rgb_linear[1]:.4f}, {rgb_linear[2]:.4f})",
                rgb_gamma_str,
                result['hex_color']
            ]
            
            text += "\t".join(row) + "\n"
        
        # Copy to clipboard
        QApplication.clipboard().setText(text)
        
        # Show prompt
        QMessageBox.information(self, "Copy", "Data copied to clipboard.")
    
    def copy_table_data(self):
        """Copy table data to clipboard, excluding color column"""
        if self.ui.table_results.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "No data to copy.")
            return
        
        # Build table data string
        text = ""
        
        # Add headers, skip color column
        headers = []
        for col in range(1, self.ui.table_results.columnCount()):
            headers.append(self.ui.table_results.horizontalHeaderItem(col).text())
        text += "\t".join(headers) + "\n"
        
        # Add data rows, skip color column
        for row in range(self.ui.table_results.rowCount()):
            row_data = []
            for col in range(1, self.ui.table_results.columnCount()):
                item = self.ui.table_results.item(row, col)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            text += "\t".join(row_data) + "\n"
        
        # Copy to clipboard
        QApplication.clipboard().setText(text)
        
        # Show prompt
        QMessageBox.information(self, "Copy", "Table data copied to clipboard (excluding color column).")
    
    def clear_data(self):
        """Clear all data"""
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Clear",  # Window title
            "Are you sure you want to clear all data? This action cannot be undone.",  # Message
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,  # Button options
            QMessageBox.StandardButton.No  # Default button
        )

        if reply == QMessageBox.StandardButton.Yes:
            print("User confirmed clearing data")
            self.reset_data()
            self.update_reflectance_plot()
            self.update_cie_plot()
            self.ui.table_results.setRowCount(0)
            self.update_menu_state(False)  # Disable Export and Plot
            
            # If reflectance data dialog is open, close it
            if self.reflectance_dialog is not None and self.reflectance_dialog.isVisible():
                self.reflectance_dialog.close()
                self.reflectance_dialog = None
            
            # If CIE chart window is open, close it
            if self.cie_dialog is not None and self.cie_dialog.isVisible():
                self.cie_dialog.close()
                self.cie_dialog = None
                
            QMessageBox.information(self, "Data Cleared", "All data has been successfully cleared.")  # Success message
        else:
            print("User cancelled clearing data")
    
    def show_reflectance_data(self):
        """Show reflectance data"""
        if not self.data['reflectance']:
            QMessageBox.warning(self, "Warning", "No reflectance data to show.")
            return
        
        # Prioritize original wavelength data (usually 1nm intervals)
        wavelengths = self.data['original_wavelengths'] if self.data['original_wavelengths'] is not None else self.data['wavelengths']
        
        # Print wavelength information
        if len(wavelengths) > 1:
            print(f"Display reflectance data using wavelength: range={wavelengths[0]:.1f}-{wavelengths[-1]:.1f}nm, "
                  f"points={len(wavelengths)}, step={wavelengths[1]-wavelengths[0]:.1f}nm")
        
        # Create dataset dictionary
        datasets = {}
        for name, reflectance_data in self.data['reflectance'].items():
            print(f"Processing dataset '{name}'...")
            
            # Check data format, to adapt to both new and old structures
            if isinstance(reflectance_data, dict):
                # New format: dictionary structure
                # Prioritize 1nm step data(reflectance_1nm) for display
                if 'reflectance_1nm' in reflectance_data and len(reflectance_data['reflectance_1nm']) > 0:
                    reflectance = reflectance_data['reflectance_1nm']
                    wavelen = reflectance_data['wavelengths_1nm'] if 'wavelengths_1nm' in reflectance_data else wavelengths
                    print(f"Using 1nm step data for display: {len(reflectance)}points")
                # Otherwise use original reflectance data
                elif 'reflectance' in reflectance_data:
                    reflectance = reflectance_data['reflectance']
                    wavelen = reflectance_data['wavelengths'] if 'wavelengths' in reflectance_data else wavelengths
                    print(f"Using original reflectance data for display: {len(reflectance)}points")
                else:
                    print(f"Warning: Dataset'{name}'format invalid, skipping")
                    continue
            else:
                # Old format: direct data array
                reflectance = reflectance_data
                wavelen = wavelengths
                print(f"Using old format data for display: {len(reflectance)}points")
            
            # Check length matching
            if len(wavelen) != len(reflectance):
                print(f"Warning: Wavelength and reflectance length mismatch: wavelength={len(wavelen)}, reflectance={len(reflectance)}")
                
                # If wavelen is not the wavelength we need, resampling is required
                if np.array_equal(wavelen, wavelengths):
                    print("Wavelength arrays match but data lengths inconsistent, data may be corrupted")
                    datasets[name] = reflectance  # Use data directly, may display incorrectly
                else:
                    print("Wavelength arrays don't match, trying resampling...")
                    try:
                        # Use provided wavelength and target wavelength for interpolation
                        interp_func = interp.interp1d(
                            wavelen, 
                            reflectance, 
                            bounds_error=False, 
                            fill_value="extrapolate"
                        )
                        
                        # Resample reflectance data to match target wavelength array
                        resampled_reflectance = interp_func(wavelengths)
                        datasets[name] = resampled_reflectance
                        print(f"Resampling completed: {len(reflectance)} -> {len(resampled_reflectance)} points")
                    except Exception as e:
                        print(f"Resampling failed: {str(e)}")
                        # If resampling failed, create zero array same length as target wavelength
                        datasets[name] = np.zeros_like(wavelengths)
                        print("Created zero-filled array as replacement")
            else:
                # Lengths match, use directly
                datasets[name] = reflectance
                print(f"Data lengths match, using directly: {len(reflectance)}points")
        
        if not datasets:
            QMessageBox.warning(self, "Warning", "No valid reflectance data to show.")
            return
        
        # Check if dialog already exists
        if self.reflectance_dialog is None or not self.reflectance_dialog.isVisible():
            # Create new dialog
            self.reflectance_dialog = ReflectanceDataDialog(wavelengths, datasets, self)
            # Use show() instead of exec() to make dialog non-modal
            self.reflectance_dialog.show()
        else:
            # Update existing dialog data
            self.reflectance_dialog.update_data(wavelengths, datasets)
    
    def on_window_resize(self, event):
        """Adjust table column widths when window size changes"""
        # Call parent class resizeEvent
        super().resizeEvent(event)
        
        # Re-adjust table column widths
        self.adjust_table_columns()
    
    def adjust_table_columns(self):
        """Adjust table column widths to fit content and window size"""
        if not hasattr(self.ui, 'table_results') or self.ui.table_results.columnCount() == 0:
            return
        
        # Get total table width
        table_width = self.ui.table_results.width()
        
        # Get table header
        header = self.ui.table_results.horizontalHeader()
        
        # Color column width
        color_width = 25  # Reduce color column width
        
        # First calculate actual width needed for filename column (based on content)
        max_filename_width = 0
        filename_padding = 15  # Reduce padding around filename
        
        # Get font metrics to calculate text width
        font_metrics = self.ui.table_results.fontMetrics()
        
        # Calculate header width
        header_text = self.ui.table_results.horizontalHeaderItem(1).text()
        header_width = font_metrics.horizontalAdvance(header_text) + filename_padding
        
        # Calculate maximum width of all filenames
        for row in range(self.ui.table_results.rowCount()):
            item = self.ui.table_results.item(row, 1)
            if item is not None:
                text_width = font_metrics.horizontalAdvance(item.text()) + filename_padding
                max_filename_width = max(max_filename_width, text_width)
        
        # Take maximum of header and content width
        filename_width = max(max_filename_width, header_width, 80)  # At least 80 pixels
                
        # Calculate fixed space needed for other columns
        fixed_width = color_width
        for col in [2, 3, 4, 5]:  # x, y, sRGB Linear, sRGB Gamma columns
            if col == 2 or col == 3:  # x and y columns
                width = max(60, header.sectionSize(col))  # Ensure x and y columns are at least 60 pixels
            else:  # RGB columns
                width = max(120, header.sectionSize(col))  # At least 120 pixels
            fixed_width += width
        
        # Check if filename column width would exceed available space
        available_width = table_width - fixed_width - 5  # Subtract 5 pixels as buffer
        if filename_width > available_width and available_width >= 80:
            # If exceeds available space but available space is enough for basic content, use available space
            filename_width = available_width
        
        # Set color column width, allow adaptive
        color_section_size = header.sectionSize(0)
        if color_section_size > color_width:
            # If user adjusted width, use user-set width
            self.ui.table_results.setColumnWidth(0, color_section_size)
        else:
            # Otherwise use default width
            self.ui.table_results.setColumnWidth(0, color_width)
        
        # Set filename column width
        self.ui.table_results.setColumnWidth(1, filename_width)
        
        # Set other column widths
        self.ui.table_results.setColumnWidth(2, max(60, header.sectionSize(2)))  # x column
        self.ui.table_results.setColumnWidth(3, max(60, header.sectionSize(3)))  # y column
        self.ui.table_results.setColumnWidth(4, max(120, header.sectionSize(4)))  # sRGB Linear column
        self.ui.table_results.setColumnWidth(5, max(120, header.sectionSize(5)))  # sRGB Gamma column

    def update_menu_state(self, has_data):
        """Update menu state"""
        if hasattr(self, 'ui'):
            self.ui.actionExport.setEnabled(has_data)
            self.ui.actionPlot.setEnabled(has_data)

    def show_cie_data(self):
        """Show enlarged view of CIE chromaticity diagram instead of data table"""
        # No longer check for data, directly show CIE chart
        
        # Check if dialog already exists
        if self.cie_dialog is None or not self.cie_dialog.isVisible():
            # Create a new dialog window
            self.cie_dialog = QDialog(self)
            self.cie_dialog.setWindowTitle("CIE Chromaticity Diagram")
            self.cie_dialog.resize(900, 900)  # Increase size from 600x600 to 900x900
            
            # Get parent window position and size
            parent_geometry = self.geometry()
            parent_x = parent_geometry.x()
            parent_y = parent_geometry.y()
            parent_width = parent_geometry.width()
            
            # Place window to the right of main window
            self.cie_dialog.setGeometry(parent_x + parent_width + 10, parent_y, 900, 900)  # Update size
            
            # Create layout
            layout = QVBoxLayout(self.cie_dialog)
            
            # Create figure and canvas - increase size
            self.cie_expanded_figure = Figure(figsize=(10, 10), dpi=100)  # Increase from 8x8 to 10x10
            self.cie_expanded_canvas = FigureCanvas(self.cie_expanded_figure)
            
            # Add canvas to layout
            layout.addWidget(self.cie_expanded_canvas)
            
            # Update CIE chart
            self.update_expanded_cie_plot()
            
            # Show non-modal dialog
            self.cie_dialog.show()
        else:
            # If dialog already exists, update chart
            self.update_expanded_cie_plot()
            # Ensure window is visible
            self.cie_dialog.show()
            self.cie_dialog.raise_()
    
    def update_expanded_cie_plot(self):
        """Update expanded CIE chart"""
        if not hasattr(self, 'cie_expanded_figure') or not hasattr(self, 'cie_expanded_canvas'):
            return
            
        # Clear chart
        self.cie_expanded_figure.clear()
        
        # Create subplot
        ax = self.cie_expanded_figure.add_subplot(111)
        
        # Set font size - adjust for high resolution
        title_size = 12
        label_size = 10
        tick_size = 9
        wavelength_label_size = 8
        annotation_size = 8
        legend_size = 9
        
        # Use same plotting logic as main window, but adjust some parameters for clarity
        try:
            # Disable warning messages
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # First draw colored background of chromaticity diagram
                plot_chromaticity_diagram_colours(
                    axes=ax,
                    diagram_colours="RGB",  # Use RGB color
                    method="CIE 1931",  # Use CIE 1931 method
                    standalone=False,  # Not standalone plotting
                    title=False,  # Don't use default title
                    bounding_box=(0, 0.8, 0, 0.9)  # Restore original settings
                )
                
                # Get spectral locus data points
                cmfs = colour.colorimetry.MSDS_CMFS['CIE 1931 2 Degree Standard Observer']
                XYZ = cmfs.values
                xy = colour.XYZ_to_xy(XYZ)
                wavelengths = cmfs.wavelengths
                
                # Create wavelength to coordinate mapping
                wavelength_dict = {wl: (x, y) for wl, (x, y) in zip(wavelengths, xy)}
                
                # Define wavelength range we want to mark (460-620nm, every 20nm)
                custom_wavelength_labels = list(range(460, 640, 20))
                
                # Create smooth boundary lines
                from scipy.interpolate import interp1d
                
                # Spectral locus line
                x_locus = np.append(xy[..., 0], xy[0, 0])
                y_locus = np.append(xy[..., 1], xy[0, 1])
                
                # Create parameterized coordinates
                t = np.linspace(0, 1, len(x_locus))
                
                # Create interpolation functions
                fx = interp1d(t, x_locus, kind='cubic')
                fy = interp1d(t, y_locus, kind='cubic')
                
                # Generate denser points
                t_new = np.linspace(0, 1, 1000)
                x_smooth = fx(t_new)
                y_smooth = fy(t_new)
                
                # Draw spectral boundary lines
                ax.plot(
                    x_smooth, 
                    y_smooth, 
                    color='black', 
                    linewidth=1.2,  # Slightly thicker
                    solid_capstyle='round',
                    zorder=10
                )
                
                # Purple line
                purple_line = np.vstack([
                    [xy[-1, 0], xy[-1, 1]],
                    [xy[0, 0], xy[0, 1]]
                ])
                
                # Draw purple line
                ax.plot(
                    purple_line[:, 0], 
                    purple_line[:, 1], 
                    color='black', 
                    linewidth=1.2,  # Slightly thicker
                    linestyle='--',
                    zorder=10
                )
                
                # Draw gamut
                gamut = self.settings['general']['gamut']
                
                # Define corresponding vertices based on selected gamut
                if gamut == 'None':
                    pass
                elif gamut == 'sRGB':
                    r = (0.64, 0.33)
                    g = (0.30, 0.60)
                    b = (0.15, 0.06)
                elif gamut == 'Adobe RGB':
                    r = (0.64, 0.33)
                    g = (0.21, 0.71)
                    b = (0.15, 0.06)
                elif gamut == 'HTC VIVE Pro Eye':
                    r = (0.6585, 0.3407)
                    g = (0.2326, 0.7119)
                    b = (0.1431, 0.0428)
                elif gamut == 'Meta Oculus Quest 1':
                    r = (0.6596, 0.3396)
                    g = (0.2395, 0.7069)
                    b = (0.1452, 0.0531)
                elif gamut == 'Meta Oculus Quest 2':
                    r = (0.6364, 0.3305)
                    g = (0.3032, 0.5938)
                    b = (0.1536, 0.0632)
                elif gamut == 'Meta Oculus Rift':
                    r = (0.6690, 0.3300)
                    g = (0.2545, 0.7015)
                    b = (0.1396, 0.0519)
                else:
                    # Default to sRGB
                    r = (0.64, 0.33)
                    g = (0.30, 0.60)
                    b = (0.15, 0.06)
                
                # Draw gamut polygon
                if gamut != 'None':
                    x_points = [r[0], g[0], b[0], r[0]]
                    y_points = [r[1], g[1], b[1], r[1]]
                    
                    # Draw gamut boundary and add labels
                    ax.plot(x_points, y_points, 'k-', linewidth=1.5, label=gamut)
                
                # Draw illuminantpoints
                illuminant = self.settings['general']['illuminant']
                
                # Common illuminant coordinates
                illuminant_coords = {
                    'D65': (0.3128, 0.3290),
                    'D50': (0.3457, 0.3585),
                    'A': (0.4476, 0.4074),
                    'E': (1/3, 1/3)
                }
                
                # Draw current illuminant points
                if illuminant in illuminant_coords:
                    x_illum, y_illum = illuminant_coords[illuminant]
                    
                    ax.plot(x_illum, y_illum, 'o', color='black', markersize=6, 
                           markerfacecolor='none', markeredgewidth=1.2, zorder=50)
                    
                    # Add illuminant annotation
                    ax.annotate(
                        f"{illuminant}",
                        (x_illum + 0.02, y_illum + 0.02),
                        fontsize=annotation_size,
                        color='black',
                        ha='left',
                        va='bottom',
                        zorder=50
                    )
                
                # Add wavelength marks
                for wl in custom_wavelength_labels:
                    if wl in wavelength_dict:
                        x, y = wavelength_dict[wl]
                        
                        # Calculate offset direction
                        center = np.array([1/3, 1/3])
                        point = np.array([x, y])
                        direction = point - center
                        
                        # Normalize direction vector
                        direction = direction / np.linalg.norm(direction)
                        
                        # Adjust offset for specific wavelengths
                        if wl == 460:
                            offset = np.array([-0.02, 0.02])
                        elif wl == 540:
                            offset = np.array([0.07, 0.03])
                        elif wl == 620:
                            offset = np.array([0.03, 0.05])
                        else:
                            offset = direction * 0.015
                        
                        # Draw wavelength points
                        ax.plot(x, y, 'o', color='black', markersize=3, zorder=15)
                        
                        # Determine text alignment
                        h_align = 'left' if direction[0] > 0 else 'right'
                        v_align = 'bottom' if direction[1] > 0 else 'top'
                        
                        # Add wavelength labels
                        ax.annotate(
                            f"{wl}",
                            (x + offset[0], y + offset[1]),
                            fontsize=wavelength_label_size,
                            color='black',
                            ha=h_align,
                            va=v_align,
                            zorder=15,
                            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.1')
                        )
                        
                # Only draw data points when data exists
                if self.data['results']:
                    # Draw data points - use larger points for easy viewing on large chart
                    for result in self.data['results']:
                        x, y = result['x'], result['y']
                        hex_color = result['hex_color']
                        file_name = result['file_name']
                        # Increase point size for large view, use labels for legend
                        ax.plot(x, y, 'o', color=hex_color, markersize=8, markeredgecolor='black', 
                              markeredgewidth=1.2, zorder=100, label=file_name)
                
                # Decide whether to show legend based on settings - including measurement points and gamut
                show_legend = self.settings['plot'].get('cie_show_legend', True)
                if show_legend:
                    # Get legend object and set smaller font size
                    legend = ax.legend(fontsize=legend_size, loc='upper right', frameon=True,
                                    bbox_to_anchor=(1.0, 1.0))
                    if legend is not None:
                        # Set legend box properties
                        legend.set_frame_on(True)
                        legend.set_title('')  # Remove legend title
                        # Adjust legend size
                        legend._legend_box.align = "right"
                else:
                    # If set to not show legend, remove any existing legend
                    legend = ax.get_legend()
                    if legend is not None:
                        legend.remove()
                
        except Exception as e:
            print(f"Error drawing expanded CIE chart: {e}")
            # Fallback to simplified drawing
            self.draw_simplified_cie_boundary(ax)
        
        # Set title and axis labels - get title settings from settings
        show_title = self.settings['plot'].get('cie_show_title', True)
        title_text = self.settings['plot'].get('cie_title', "CIE 1931 Chromaticity Diagram")
        
        if show_title:
            ax.set_title(title_text, fontsize=title_size)
        
        ax.set_xlabel("x", fontsize=label_size)
        ax.set_ylabel("y", fontsize=label_size)
        
        # Set axis range
        ax.set_xlim(0, 0.8)
        ax.set_ylim(0, 0.9)
        
        # Set axis ticks
        ax.set_xticks(np.arange(0, 0.9, 0.1))
        ax.tick_params(axis='x', which='major', labelsize=tick_size)
        
        # Y-axis ticks
        ax.set_yticks(np.arange(0, 1.0, 0.1))
        ax.tick_params(axis='y', which='major', labelsize=tick_size)
        
        # Disable grid
        ax.grid(False)
        
        # Adjust layout
        self.cie_expanded_figure.tight_layout()
        
        # Update canvas
        self.cie_expanded_canvas.draw()
    
    def draw_simplified_cie_boundary(self, ax):
        """Draw simplified boundary for expanded CIE chart (backup method)"""
        # Use simplified CIE boundary points
        boundary_x = [0.1740, 0.0000, 0.0000, 0.0332, 0.0648, 0.0919, 0.1390, 0.1738, 0.2080, 0.2586, 0.3230, 0.3962, 0.4400, 0.4699, 0.4999, 0.5140, 0.5295, 0.5482, 0.5651, 0.5780, 0.5832, 0.5800, 0.5672, 0.5314, 0.4649, 0.3652, 0.2615, 0.1740]
        boundary_y = [0.0049, 0.0000, 0.0100, 0.0380, 0.0650, 0.0910, 0.2080, 0.2737, 0.3344, 0.4077, 0.4964, 0.5574, 0.5800, 0.5888, 0.5991, 0.6039, 0.6089, 0.6128, 0.6150, 0.6160, 0.6160, 0.6155, 0.6123, 0.6030, 0.5657, 0.4679, 0.2624, 0.0049]
        
        # Draw boundary
        ax.plot(boundary_x, boundary_y, 'k-', linewidth=1.5)
        
        # Fill range
        ax.fill(boundary_x, boundary_y, alpha=0.1, color='gray')
        
        # Draw illuminant
        illuminant = self.settings['general']['illuminant']
        # Common illuminant coordinates
        illuminant_coords = {
            'D65': (0.3128, 0.3290),
            'D50': (0.3457, 0.3585),
            'A': (0.4476, 0.4074),
            'E': (1/3, 1/3)
        }
        
        if illuminant in illuminant_coords:
            x_illum, y_illum = illuminant_coords[illuminant]
            ax.plot(x_illum, y_illum, 'o', color='black', markersize=6, 
                   markerfacecolor='none', markeredgewidth=1.2, zorder=50)
        
        # Draw gamut (if any)
        gamut = self.settings['general']['gamut']
        if gamut != 'None':
            # Define corresponding vertices based on selected gamut
            if gamut == 'sRGB':
                r = (0.64, 0.33)
                g = (0.30, 0.60)
                b = (0.15, 0.06)
            elif gamut == 'Adobe RGB':
                r = (0.64, 0.33)
                g = (0.21, 0.71)
                b = (0.15, 0.06)
            elif gamut == 'HTC VIVE Pro Eye':
                r = (0.6585, 0.3407)
                g = (0.2326, 0.7119)
                b = (0.1431, 0.0428)
            elif gamut == 'Meta Oculus Quest 1':
                r = (0.6596, 0.3396)
                g = (0.2395, 0.7069)
                b = (0.1452, 0.0531)
            elif gamut == 'Meta Oculus Quest 2':
                r = (0.6364, 0.3305)
                g = (0.3032, 0.5938)
                b = (0.1536, 0.0632)
            elif gamut == 'Meta Oculus Rift':
                r = (0.6690, 0.3300)
                g = (0.2545, 0.7015)
                b = (0.1396, 0.0519)
            else:
                # Default to sRGB
                r = (0.64, 0.33)
                g = (0.30, 0.60)
                b = (0.15, 0.06)
                
            # Create closed polygon point list
            x_points = [r[0], g[0], b[0], r[0]]
            y_points = [r[1], g[1], b[1], r[1]]
            
            # Draw gamut boundary and add labels
            ax.plot(x_points, y_points, 'k-', linewidth=1.5, label=gamut)
        
        # Draw data points - use labels instead of direct annotation
        for result in self.data['results']:
            x, y = result['x'], result['y']
            hex_color = result['hex_color']
            file_name = result['file_name']
            ax.plot(x, y, 'o', color=hex_color, markersize=8, markeredgecolor='black', 
                   markeredgewidth=1.2, zorder=100, label=file_name)
        
        # Decide whether to show legend based on settings
        show_legend = self.settings['plot'].get('cie_show_legend', True)
        if show_legend:
            # Add legend
            legend = ax.legend(fontsize=8, loc='upper right', frameon=True)
            if legend is not None:
                legend.set_frame_on(True)
                legend.set_title('')
        else:
            # Don't show legend
            legend = ax.get_legend()
            if legend is not None:
                legend.remove()
                
        # Set title (get settings from settings)
        show_title = self.settings['plot'].get('cie_show_title', True)
        title_text = self.settings['plot'].get('cie_title', "CIE 1931 Chromaticity Diagram")
        
        if show_title:
            ax.set_title(title_text, fontsize=12)
    
    def resizeEvent(self, event):
        """Handle window resize event, adjust UI elements"""
        super().resizeEvent(event)
        self.adjust_table_columns()
        
        # Refresh chart
        if hasattr(self, 'reflectance_canvas'):
            self.reflectance_canvas.draw()
        if hasattr(self, 'cie_canvas'):
            self.cie_canvas.draw()
        
        # Trigger window resize event
        if hasattr(self, 'reflectance_canvas') or hasattr(self, 'cie_canvas'):
            self.on_window_resize(event)
    
    def closeEvent(self, event):
        """
        Handle application close event, ensure all user settings are saved
        """
        # Save all current settings to config file
        self.save_settings()
        
        # Call parent class closeEvent to handle default close behavior
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())