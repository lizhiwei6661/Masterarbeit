import numpy as np
import os
from color_calculator import ColorCalculator

def main():
    """
    简化版测试，只测试一个文件
    """
    print("简化测试：使用CSV数据的XYZ计算...")
    
    # 创建ColorCalculator实例
    calculator = ColorCalculator()
    
    # 设置rho_lambda值为0.989，与MATLAB一致
    calculator.set_rho_lambda(0.989)
    print(f"设置rho_lambda值为: {calculator.rho_lambda}")
    
    # 加载黑白参考数据
    import_sample_dir = "Matlab_Input/Import_Sample"
    black_file = os.path.join(import_sample_dir, "black.csv")
    white_file = os.path.join(import_sample_dir, "white.csv")
    
    black_wl, black_data = calculator.load_measurement_data(black_file)
    white_wl, white_data = calculator.load_measurement_data(white_file)
    
    if black_data is None or white_data is None:
        print("错误: 无法加载黑白参考数据")
    else:
        print("成功加载黑白参考数据")
        # 设置校准模式
        calculator.set_calibration_mode(True, black_data, white_data)
        print("已设置校准模式")
    
    # 加载测试文件
    test_file = os.path.join(import_sample_dir, "tu-berlin00004.csv")
    
    # 提取仪器值
    instrument_values = calculator.extract_instrument_values(test_file)
    if instrument_values is not None:
        print(f"仪器值: ({instrument_values[0]:.6f}, {instrument_values[1]:.6f})")
    
    # 加载测量数据
    wavelengths, data = calculator.load_measurement_data(test_file)
    if wavelengths is None or data is None:
        print(f"错误: 无法加载测量数据")
        return
    
    print(f"测量数据: {len(wavelengths)}点, 波长范围: {wavelengths[0]}-{wavelengths[-1]}nm")
    
    # 计算反射率
    reflectance = calculator.calculate_reflectance(data, wavelengths)
    print(f"反射率计算完成")
    
    # 测试不同光源
    for illuminant in ['D65', 'A', 'D50', 'E']:
        calculator.set_illuminant(illuminant)
        print(f"\n光源: {illuminant}")
        
        # 计算XYZ值
        xyz = calculator.calculate_xyz(reflectance, wavelengths, use_matlab_compatible=True)
        print(f"XYZ值: X={xyz[0]:.6f}, Y={xyz[1]:.6f}, Z={xyz[2]:.6f}")
        
        # 计算xy坐标
        xy = calculator.xyz_to_xy(xyz)
        print(f"计算的xy坐标: ({xy[0]:.6f}, {xy[1]:.6f})")
        
        # 比较与仪器值的差异
        if instrument_values is not None:
            x_diff = abs(xy[0] - instrument_values[0])
            y_diff = abs(xy[1] - instrument_values[1])
            print(f"与仪器值的差异: Δx={x_diff:.6f}, Δy={y_diff:.6f}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    main() 