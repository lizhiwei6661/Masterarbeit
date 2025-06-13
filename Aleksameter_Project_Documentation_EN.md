# Aleksameter Reflectance Calculation Tool - Comprehensive Project Documentation

## Project Overview

Aleksameter is a professional spectral reflectance measurement and color analysis tool built with PySide6/Qt6, designed for processing spectral measurement data and performing precise color calculations. The software supports multiple measurement devices and data formats, capable of performing CIE colorimetric analysis and sRGB color space conversions.

**Version**: 1.0.0  
**Build Date**: 2024  
**License**: Copyright © 2024 All rights reserved  
**Platform Support**: macOS (Intel/Apple Silicon), Windows, Linux

## Technical Architecture

### Core Technology Stack
- **GUI Framework**: PySide6 (Qt6)
- **Data Processing**: NumPy, SciPy, Pandas
- **Visualization**: Matplotlib  
- **Color Science**: colour-science library
- **File Processing**: openpyxl (Excel), CSV, JSON
- **Packaging**: PyInstaller (cross-platform), py2app (macOS)

### Project Structure

```
├── app.py                      # Main program entry point
├── mainwindow.py               # Main window controller (2266 lines)
├── color_calculator.py         # Color calculation core module (1323 lines)
├── import_dialog.py            # Data import dialog (788 lines)
├── export_dialog.py            # Data export dialog (696 lines)
├── plot_dialog.py              # Plot export dialog (566 lines)
├── settings_dialog.py          # Settings dialog (432 lines)
├── reflectance_data_dialog.py  # Reflectance data viewer dialog (217 lines)
├── cie_data_dialog.py          # CIE chromaticity data viewer dialog (271 lines)
├── about_dialog.py             # About dialog (60 lines)
├── ui_files/                   # Qt Designer UI files
│   ├── form.ui                 # Main window UI
│   ├── Import.ui               # Import dialog UI
│   ├── Settings.ui             # Settings dialog UI
│   ├── export_dialog.ui        # Export dialog UI
│   └── plot_dialog.ui          # Plot export dialog UI
├── ui_*.py                     # Generated Python UI files
├── requirements.txt            # Python dependencies
├── setup.py                    # py2app packaging configuration
├── Aleksameter_mac_arm64.spec  # PyInstaller packaging configuration
├── make_dmg.sh                 # macOS DMG creation script
├── app_settings.json           # Default application settings
├── font_settings.json          # Font configuration settings
├── xyzBar.csv                  # CIE 1931 standard observer data
├── stdIllum.csv                # Standard illuminant data
└── Import_Sample/              # Sample data files for testing
```

## Core Modules

### 1. Data Import Module (import_dialog.py)

#### 1.1 Device Mode Support
- **Aleksameter Mode**: 
  - Requires calibration procedure: Must import black reference and white reference data first (CSV format only)
  - Calibration workflow: Black reference → White reference → Measurement data
  - Supports reference data swapping functionality
  - Real-time preview of imported data curves

- **General Mode**:
  - No calibration required: Direct import of measurement data (CSV format only)
  - Suitable for pre-calibrated data or standardized data
  - Calibration-related features are disabled

#### 1.2 Data Format Support
- **CSV files (.csv)** - Only supported format
- Automatic recognition of data structure and wavelength range
- Supports various CSV format variants and encodings
- Expected format: `Wavelength [nm], Sample1, Sample2, ...`

#### 1.3 Import Features
- Batch file selection and processing
- Data integrity validation
- Real-time chart preview (displays up to 3 files)
- Smart directory memory functionality
- Select all/deselect all shortcuts

### 2. Main Window Display (mainwindow.py)

#### 2.1 Three-Panel Layout

**Upper Panel - Reflectance Chart**:
- Displays reflectance spectral curves for all imported files
- X-axis: Wavelength (380-780nm)
- Y-axis: Reflectance (0-1)
- Supports legend show/hide functionality
- Customizable title and font size
- Interactive navigation without toolbar

**Lower Left Panel - CIE Chromaticity Diagram**:
- CIE 1931 chromaticity diagram
- Displays chromaticity coordinates of measured samples
- Supports multiple color gamut overlays (sRGB, Adobe RGB, HTC VIVE Pro Eye, etc.)
- Illuminant display (D65, D50, A, E)
- Real-time color plotting

**Lower Right Panel - Color Data Table**:
- Color preview column with actual calculated colors
- Filename column
- CIE x, y chromaticity coordinates
- sRGB Linear values (0-1)
- sRGB Gamma values (0-255)
- Copy to clipboard functionality

#### 2.2 Interactive Features
- Data copy to clipboard functionality
- Data clearing with confirmation dialog
- Chart zoom and navigation
- Real-time data updates
- Adaptive window resizing
- Multi-platform settings management

### 3. Color Calculation Engine (color_calculator.py)

#### 3.1 Spectral Processing
- Supports 1nm and 5nm step data
- Automatic wavelength interpolation and resampling
- Black/white reference calibration algorithms
- rho_lambda factor correction (default: 0.989)
- MATLAB-compatible interpolation methods

#### 3.2 Color Science Calculations
- CIE 1931 standard observer functions
- Multiple standard illuminant support (D65, D50, A, E)
- XYZ tristimulus value calculation
- sRGB color space conversion
- Linear RGB and Gamma-corrected RGB calculations
- High-precision numerical computation

#### 3.3 Calibration Algorithm
```
Reflectance = ((Measurement - Black_Reference) × White_Reference) / 
              ((White_Reference - Black_Reference) × Measurement) × rho_lambda
```

### 4. Data Export Module (export_dialog.py)

#### 4.1 Supported Formats
- **Excel (.xlsx)**: Multi-worksheet format with separate sheets for reflectance and color data
- **CSV (.csv)**: Comma-separated values format
- **TXT (.txt)**: Tab-separated text format
- **JSON (.json)**: Structured data format with hierarchical organization

#### 4.2 Export Options
- Reflectance data export (optional)
- Color data export (optional)
- Decimal separator settings (comma/point)
- Header inclusion options
- Decimal places control (1-10 places)
- Custom file path and naming

#### 4.3 Data Organization
- **Reflectance Sheet**: Wavelength column + individual sample reflectance columns
- **Color Sheet**: Filename, x, y coordinates, RGB linear values, RGB gamma values

### 5. Plot Export Module (plot_dialog.py)

#### 5.1 Export Formats
- **PNG (.png)** - High-quality bitmap with transparency support
- **JPEG (.jpg)** - Compressed bitmap for smaller file sizes
- **TIFF (.tif)** - Lossless bitmap format
- **PDF (.pdf)** - Vector format for scalable graphics

#### 5.2 Plot Options
- Reflectance spectrum plot export
- CIE chromaticity diagram export
- Individual or combined export options
- Custom resolution settings (150/300/600 DPI)
- Custom size settings (width/height in pixels)

#### 5.3 Styling and Fonts
- Three font sizes (Small/Medium/Large)
- DPI-adaptive font scaling
- Custom titles and labels
- Legend display control
- Professional color schemes

### 6. Settings Module (settings_dialog.py)

#### 6.1 Three Settings Tabs

**General Tab**:
- rho_lambda value setting (default: 0.989)
- Standard illuminant selection (D65, D50, A, E)
- Color gamut display selection (None, sRGB, Adobe RGB, HTC VIVE Pro Eye, Meta Oculus Quest 1/2, Meta Oculus Rift)
- RGB value display format (0-1 or 0-255)

**Plot Tab**:
- Reflectance plot settings:
  - Width/Height (pixels)
  - DPI settings (150/300/600)
  - Title text customization
  - Title/legend display toggles
  - Font size options
- CIE plot settings:
  - Width/Height (pixels)
  - DPI settings
  - Title text customization
  - Title/legend display toggles
  - Font size options

**Export Tab**:
- Decimal separator selection (Point/Comma)
- Copy header option (Yes/No)
- Default export format
- Decimal places settings
- Directory preferences

#### 6.2 Settings Management
- Settings automatically saved to user directory
- Cross-platform directory management (macOS/Windows/Linux)
- Default settings restoration
- Settings validation and error handling
- JSON-based configuration storage

### 7. Data Viewer Dialogs

#### 7.1 Reflectance Data Dialog (reflectance_data_dialog.py)
- Tabular display of raw reflectance data
- Wavelength column + individual sample data columns
- Copy to clipboard functionality
- Non-modal window for simultaneous operation with main window
- Auto-update synchronized with main window data

#### 7.2 CIE Data Dialog (cie_data_dialog.py)
- Upper section: Interactive CIE chromaticity diagram
- Lower section: Chromaticity data table
- Color preview, coordinate values, RGB value display
- Data copy and export capabilities
- Enhanced visualization options

### 8. Menu System

#### 8.1 File Menu
- **Import...** (Ctrl+O): Open import dialog
- **Export...** (Ctrl+E): Open export dialog  
- **Plot...** (Ctrl+P): Open plot export dialog
- **Settings...** (Ctrl+.): Open settings dialog

#### 8.2 Edit Menu
- **Copy ALL Data** (Ctrl+C): Copy all data to clipboard
- **Clear** (Ctrl+K): Clear all data with confirmation
- **Illuminant Submenu**: D65, D50, A, E (linked to General settings)
- **Gamut Submenu**: None, sRGB, Adobe RGB, VR headsets (linked to General settings)

#### 8.3 Help Menu
- **About...**: Display application information
- **Manual...**: Access user documentation

## Data Workflow

### Typical Workflow Process

1. **Data Import**:
   - Select device mode (Aleksameter/General)
   - For Aleksameter mode: Import black reference → white reference → measurement data
   - For General mode: Direct import of measurement data
   - Preview data curves and confirm import

2. **Data Processing**:
   - Wavelength data standardization and interpolation
   - Reflectance calibration calculation (if applicable)
   - CIE XYZ value calculation
   - sRGB color space conversion

3. **Results Display**:
   - Main window real-time updates in three display areas
   - Reflectance spectrum plot
   - CIE chromaticity diagram
   - Color data table

4. **Data Export**:
   - Select export format and options
   - Reflectance data and/or color data
   - Custom file path and naming

5. **Plot Export**:
   - Select plot type and format
   - Set resolution and dimensions
   - Apply font and style settings

## File Format Specifications

### CSV Input Format
```
Wavelength [nm], Sample1, Sample2, Sample3, ...
380, 0.123456, 0.234567, 0.345678, ...
385, 0.125678, 0.236789, 0.347890, ...
390, 0.127890, 0.238901, 0.349012, ...
...
780, 0.543210, 0.654321, 0.765432, ...
```

### Excel Output Format
- **rho worksheet**: Wavelength column + reflectance data columns
- **color worksheet**: Filename, x, y, RGB linear, RGB gamma columns

## Performance Characteristics

### Data Processing Capabilities
- Supports 1nm precision high-resolution spectral data
- Batch processing of multiple measurement files
- Real-time chart updates and rendering
- Memory-optimized data storage structures
- Efficient interpolation algorithms

### User Interface Responsiveness
- Non-blocking file I/O operations
- Progressive data loading
- Adaptive layout and font scaling
- Cross-platform compatibility (macOS/Windows/Linux)
- Native look and feel integration

## Build and Deployment

### Dependencies
```
PySide6>=6.4.0
numpy>=1.21.0
scipy>=1.7.0
pandas>=1.3.0
matplotlib>=3.4.0
openpyxl>=3.0.0
colour-science (automatically detected)
```

### Packaging Options

#### macOS (py2app)
- Universal binary support (Intel + Apple Silicon)
- DMG creation with application bundle
- Native macOS integration and file associations
- High DPI display support

#### Cross-platform (PyInstaller)
- Single executable generation
- Automatic dependency bundling
- Custom data file inclusion
- Platform-specific optimizations

### Configuration Files
- **app_settings.json**: Application preferences and defaults
- **font_settings.json**: Font configuration for different platforms
- **xyzBar.csv**: CIE 1931 standard observer data (380-780nm, 1nm step)
- **stdIllum.csv**: Standard illuminant spectral power distributions

## Extensibility Design

### Modular Architecture
- Clear MVC separation with well-defined interfaces
- Independent color calculation engine
- Pluggable data format support
- Standardized settings management system
- Event-driven communication between modules

### Future Enhancement Opportunities
- Additional measurement device support
- Other color space conversions (LAB, LUV, etc.)
- Spectral data analysis tools
- Batch processing and automation scripts
- Database integration and project management
- Advanced visualization options
- Real-time measurement integration

## Technical Implementation Details

### Color Science Implementation
- Strict adherence to CIE standards
- High-precision numerical calculations
- MATLAB-compatible algorithm implementation
- Precise interpolation of illuminant and observer functions
- Validation against reference implementations

### Cross-Platform Support
- Adaptive file path handling
- Platform-specific settings directories:
  - macOS: `~/Library/Application Support/Aleksameter/`
  - Windows: `%APPDATA%/Aleksameter/`
  - Linux: `~/.aleksameter/`
- High DPI display support
- Native appearance integration

### Error Handling and Validation
- Comprehensive data validation with detailed error messages
- Automatic data repair and cleaning
- Graceful handling of malformed input files
- User-friendly error reporting
- Debug information and logging capabilities

### Testing and Quality Assurance
- Sample data files for validation (`Import_Sample/` directory)
- Cross-platform testing on macOS, Windows, and Linux
- Performance testing with large datasets
- Color accuracy validation against reference standards

## Version History and Development

### Version 1.0.0 (Current)
- Initial release with full feature set
- Professional GUI with three-panel layout
- Complete color calculation pipeline
- Multiple export formats
- Cross-platform compatibility
- Comprehensive settings management

### Development Background
- Developed as part of a Master's thesis project
- Migration from MATLAB to Python implementation
- Focus on scientific accuracy and usability
- Professional-grade software design principles

## Conclusion

Aleksameter represents a comprehensive, professional-grade spectral reflectance measurement and color analysis tool. It combines modern GUI design with precise color science algorithms and flexible data processing capabilities, providing researchers and engineers with a reliable color measurement solution. The modular architecture and comprehensive feature coverage make it suitable for both daily measurement work and future functional expansion.

The application demonstrates successful migration from MATLAB to Python while maintaining scientific rigor and adding enhanced usability features. Its cross-platform design and professional interface make it accessible to a wide range of users in research and industrial applications. 