import numpy as np
import scipy.interpolate as interp
import os
import json
import re
import csv
import sys

class ColorCalculator:
    """
    Color calculator class, used to calculate color coordinates and sRGB values from reflectance data
    """
    
    def __init__(self):
        """
        Initialize color calculator
        """
        print("Initializing ColorCalculator...")
        
        # 加载CIE数据
        self.cie_1931 = self.load_cie_data_from_csv()
        print(f"CIE data: {len(self.cie_1931['wavelengths'])} points, "
              f"step: {self.cie_1931['wavelengths'][1] - self.cie_1931['wavelengths'][0]}nm")
        
        # 加载光源数据
        self.illuminants = self.load_illuminants()
        self.illuminant = 'D65'  # 默认使用D65光源
        for illuminant_name in self.illuminants.keys():
            print(f"Illuminant {illuminant_name}: {len(self.illuminants[illuminant_name])} points")
        
        # 设置默认波长范围
        self.wavelengths = np.arange(380, 781, 5)  # 380-780nm，5nm步长
        
        # 设置默认参数
        self.calibration_mode = None
        self.black_reference = None
        self.white_reference = None
        self.rho_lambda = 1.0
        
        print("ColorCalculator initialization completed")
    
    def get_resource_path(self, relative_path):
        """
        获取资源文件的绝对路径，适用于开发环境和PyInstaller打包环境
        
        Parameters:
            relative_path: 相对路径
            
        Returns:
            绝对路径
        """
        try:
            # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
            base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
            return os.path.join(base_path, relative_path)
        except Exception as e:
            print(f"Error getting resource path: {str(e)}")
            return relative_path
    
    def load_cie_data_from_csv(self):
        """
        Load CIE standard observer data from xyzBar.csv
        
        Returns:
            cie_1931: Dictionary containing wavelengths, x, y, z values
        """
        csv_path = self.get_resource_path("xyzBar.csv")
        
        if not os.path.exists(csv_path):
            print(f"Warning: xyzBar.csv file does not exist: {csv_path}")
            print("Using built-in CIE data")
            return self.load_cie_data()
        
        try:
            wavelengths = []
            x_values = []
            y_values = []
            z_values = []
            
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)  # Skip header row
                
                for row in reader:
                    if len(row) >= 4:
                        wavelengths.append(float(row[0]))
                        x_values.append(float(row[1]))
                        y_values.append(float(row[2]))
                        z_values.append(float(row[3]))
            
            if len(wavelengths) == 0:
                print("Warning: No data in CSV file")
                return self.load_cie_data()
            
            print(f"Successfully loaded CIE data from CSV: {len(wavelengths)} points, "
                  f"wavelength range: {wavelengths[0]}-{wavelengths[-1]}nm, "
                  f"x range: {min(x_values):.6f}-{max(x_values):.6f}, "
                  f"y range: {min(y_values):.6f}-{max(y_values):.6f}, "
                  f"z range: {min(z_values):.6f}-{max(z_values):.6f}")
            
            cie_1931 = {
                'wavelengths': np.array(wavelengths),
                'x': np.array(x_values),
                'y': np.array(y_values),
                'z': np.array(z_values)
            }
            
            return cie_1931
            
        except Exception as e:
            print(f"Error loading CIE data from CSV: {str(e)}")
            print("Using built-in CIE data")
            return self.load_cie_data()
    
    def load_illuminants(self):
        """
        Load standard light source data
        
        Returns:
            illuminants: Dictionary of different standard light sources
        """
        # First try to load from CSV file
        csv_path = self.get_resource_path("stdIllum.csv")
        
        if os.path.exists(csv_path):
            try:
                # Load standard light source data from CSV
                wavelengths = []
                illuminant_a = []
                illuminant_d65 = []
                illuminant_d50 = []
                
                with open(csv_path, 'r') as f:
                    reader = csv.reader(f)
                    header = next(reader)  # Get header
                    
                    # Check header, determine column indices
                    source_indices = {}
                    for i, name in enumerate(header):
                        name = name.strip().upper()
                        if name == 'WAVELENGTH':
                            continue
                        elif name == 'A':
                            source_indices['A'] = i
                        elif name == 'D65':
                            source_indices['D65'] = i
                        elif name == 'D50':
                            source_indices['D50'] = i
                    
                    # Read data
                    for row in reader:
                        if len(row) >= max(source_indices.values()) + 1:
                            wavelengths.append(float(row[0]))
                            for source, idx in source_indices.items():
                                if source == 'A':
                                    illuminant_a.append(float(row[idx]))
                                elif source == 'D65':
                                    illuminant_d65.append(float(row[idx]))
                                elif source == 'D50':
                                    illuminant_d50.append(float(row[idx]))
                
                # Check if all data is successfully loaded
                if len(wavelengths) == 0:
                    print("Warning: No wavelength data in CSV file, using built-in light source data")
                    return self.load_default_illuminants()
                
                # Check wavelength step
                wavelength_step = wavelengths[1] - wavelengths[0]
                expected_step = 1.0  # Expect CSV file to be 1nm step
                
                # Create light source dictionary
                illuminants = {}
                
                # Add A light source
                if len(illuminant_a) > 0:
                    illuminants['A'] = np.array(illuminant_a)
                    print(f"Loaded A light source: {len(illuminant_a)} points, range: {min(illuminant_a):.6f}-{max(illuminant_a):.6f}")
                
                # Add D65 light source
                if len(illuminant_d65) > 0:
                    illuminants['D65'] = np.array(illuminant_d65)
                    print(f"Loaded D65 light source: {len(illuminant_d65)} points, range: {min(illuminant_d65):.6f}-{max(illuminant_d65):.6f}")
                
                # Add D50 light source
                if len(illuminant_d50) > 0:
                    illuminants['D50'] = np.array(illuminant_d50)
                    print(f"Loaded D50 light source: {len(illuminant_d50)} points, range: {min(illuminant_d50):.6f}-{max(illuminant_d50):.6f}")
                
                # Calculate uniform light source E (all wavelengths power equal)
                if 'E' not in illuminants:
                    illuminants['E'] = np.ones(len(wavelengths))
                    print(f"Created uniform light source E: {len(illuminants['E'])} points")
                
                # Check if at least one light source is loaded
                if len(illuminants) == 0:
                    print("Warning: Unable to load any light source from CSV, using built-in light source data")
                    return self.load_default_illuminants()
                
                # If CIE data is 5nm step, but light source data is 1nm step, need to resample
                if self.cie_1931['wavelengths'][1] - self.cie_1931['wavelengths'][0] == 5 and wavelength_step == 1:
                    print(f"CSV light source data is {wavelength_step}nm step, but CIE data is 5nm step, resample light source data")
                    cie_wavelengths = self.cie_1931['wavelengths']
                    for source in illuminants.keys():
                        # Create original light source wavelength array
                        source_wavelengths = np.array(wavelengths)
                        # Resample to CIE wavelengths
                        illuminants[source] = np.interp(
                            cie_wavelengths, 
                            source_wavelengths, 
                            illuminants[source],
                            left=0, right=0
                        )
                
                return illuminants
                
            except Exception as e:
                print(f"Error loading light source data from CSV: {str(e)}")
                print("Using built-in light source data")
                return self.load_default_illuminants()
        else:
            print(f"Light source CSV file does not exist: {csv_path}")
            print("Using built-in light source data")
            return self.load_default_illuminants()
    
    def calculate_xyz(self, reflectance, wavelengths, use_matlab_compatible=True):
        """
        Calculate CIE XYZ values (interface function)
        
        Parameters:
            reflectance: Reflectance data
            wavelengths: Wavelength corresponding to reflectance data
            use_matlab_compatible: Whether to use calculation method compatible with MATLAB (default True)
            
        Returns:
            CIE XYZ three values
        """
        if use_matlab_compatible:
            return self.calculate_xyz_matlab_compatible(reflectance, wavelengths)
        else:
            return self.calculate_xyz_standard(reflectance, wavelengths) 