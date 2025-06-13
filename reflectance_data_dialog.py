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
        Initialize reflectance data dialog.
        
        Parameters:
            wavelengths: List of wavelength values
            datasets: Dictionary of dataset names and values
            parent: Parent window
        """
        super().__init__(parent)
        self.setWindowTitle("Reflectance Data")
        
        # Get parent window position and size
        parent_geometry = parent.geometry()
        parent_width = parent_geometry.width()
        parent_height = parent_geometry.height()
        parent_x = parent_geometry.x()
        parent_y = parent_geometry.y()
        
        # Set window position to the right of parent window, narrow and tall shape
        dialog_width = 400  # Set fixed width
        dialog_height = parent_height  # Same height as parent window
        self.setGeometry(parent_x + parent_width + 10, parent_y, dialog_width, dialog_height)
        
        # Store data
        self.wavelengths = wavelengths
        self.datasets = datasets
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  # Set more suitable margins
        
        # Create table
        self.table = QTableWidget()
        self.setup_table_style()  # Set table style
        self.populate_table()
        layout.addWidget(self.table)
        
        # Create button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Create copy button
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(self.copy_button)
        
        # Add button layout to main layout
        button_container = QWidget()
        button_container.setLayout(button_layout)
        layout.addWidget(button_container)
        
        # Set dialog flags to allow interaction with main window
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
    
    def setup_table_style(self):
        """Set table style, consistent with main window table"""
        # Set row height
        self.table.verticalHeader().setDefaultSectionSize(22)  # Adjust row height to 22 pixels
        self.table.verticalHeader().setVisible(False)  # Hide vertical header
        
        # Set table style
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
        
        # Set table properties
        self.table.setAlternatingRowColors(True)  # Alternating row colors
        self.table.setSortingEnabled(False)  # Disable sorting, consistent with main table
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
    
    def populate_table(self):
        """
        Populate table data.
        """
        # Set number of columns (Lambda + number of datasets)
        num_columns = 1 + len(self.datasets)
        self.table.setColumnCount(num_columns)
        
        # Set number of rows (number of wavelengths)
        num_rows = len(self.wavelengths)
        self.table.setRowCount(num_rows)
        
        # Set headers, remove .csv suffix from filenames
        headers = ["Lambda (nm)"]
        for filename in self.datasets.keys():
            # Remove filename suffix
            display_name = filename
            if display_name.lower().endswith('.csv'):
                display_name = display_name[:-4]
            headers.append(display_name)
        
        self.table.setHorizontalHeaderLabels(headers)
        
        # Fill wavelength data, don't show decimal places
        for row, wavelength in enumerate(self.wavelengths):
            # Display wavelength as integer
            wavelength_item = QTableWidgetItem(f"{int(wavelength)}")
            wavelength_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 0, wavelength_item)
            
            # Fill reflectance data for each dataset
            for col, (dataset_name, dataset_values) in enumerate(self.datasets.items(), start=1):
                if row < len(dataset_values):
                    value_item = QTableWidgetItem(f"{dataset_values[row]:.6f}")
                    value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.table.setItem(row, col, value_item)
        
        # Initial setup of wavelength column width
        self.table.setColumnWidth(0, 85)
        
        # Set column widths - initial setup
        self.adjust_columns()
    
    def update_data(self, wavelengths, datasets):
        """Update table data, used to refresh when main window data changes"""
        try:
            # Safely update data
            self.wavelengths = wavelengths
            self.datasets = datasets
            
            print(f"Updating reflectance data dialog: {len(wavelengths)} wavelengths, {len(datasets)} datasets")
            
            # Check if each dataset length matches wavelength length
            for name, values in datasets.items():
                if len(values) != len(wavelengths):
                    print(f"Warning: Dataset '{name}' length ({len(values)}) doesn't match wavelength length ({len(wavelengths)})")
            
            # Re-populate table
            self.populate_table()
            print("Reflectance data dialog updated successfully")
        except Exception as e:
            print(f"Error updating reflectance data dialog: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def adjust_columns(self):
        """Adjust column widths to fit content and window size"""
        # Get total table width
        table_width = self.table.width()
        num_data_columns = len(self.datasets)
        
        if num_data_columns > 0:
            # Fixed width for wavelength column
            wavelength_column_width = 85  # Reduced from 100 to 85 pixels
            self.table.setColumnWidth(0, wavelength_column_width)
            
            # Distribute remaining space evenly among other columns
            remaining_width = table_width - wavelength_column_width - 20  # Subtract 20 for scrollbar and margin buffer
            if remaining_width > 0 and num_data_columns > 0:
                data_column_width = max(100, remaining_width // num_data_columns)
                
                for col in range(1, self.table.columnCount()):
                    self.table.setColumnWidth(col, data_column_width)
    
    def copy_to_clipboard(self):
        """
        Copy table data to clipboard.
        """
        clipboard = QApplication.clipboard()
        
        # Build text representation of table data
        text = ""
        
        # Add headers
        headers = []
        for col in range(self.table.columnCount()):
            headers.append(self.table.horizontalHeaderItem(col).text())
        text += "\t".join(headers) + "\n"
        
        # Add data rows
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            text += "\t".join(row_data) + "\n"
        
        # Set clipboard content
        clipboard.setText(text)
    
    def resizeEvent(self, event):
        """Window resize event"""
        super().resizeEvent(event)
        # Adjust column widths
        self.adjust_columns()
        
    def showEvent(self, event):
        """Window show event"""
        super().showEvent(event)
        # Adjust column widths after window is shown
        QTimer.singleShot(100, self.adjust_columns) 