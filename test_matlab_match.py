import numpy as np
import os
from color_calculator import ColorCalculator

def main():
    """
    测试与MATLAB完全匹配的XYZ计算
    """
    print("测试与MATLAB完全匹配的XYZ计算...")
    
    # 创建输出目录
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建ColorCalculator实例
    calculator = ColorCalculator()
    
    # 设置rho_lambda值为0.989，与MATLAB一致
    calculator.set_rho_lambda(0.989)
    
    # 打印CIE数据信息
    print("\nCIE数据信息:")
    cie_data = calculator.cie_1931
    print(f"数据点数: {len(cie_data['wavelengths'])}")
    print(f"波长范围: {cie_data['wavelengths'][0]}-{cie_data['wavelengths'][-1]}nm")
    print(f"波长步长: {cie_data['wavelengths'][1] - cie_data['wavelengths'][0]}nm")
    
    # 设置校准模式（需要黑白参考）
    matlab_data_dir = "Matlab_Input/data"
    import_sample_dir = "Matlab_Input/Import_Sample"
    black_file = os.path.join(import_sample_dir, "black.csv")
    white_file = os.path.join(import_sample_dir, "white.csv")
    
    # 加载黑白参考数据
    black_wl, black_data = calculator.load_measurement_data(black_file)
    white_wl, white_data = calculator.load_measurement_data(white_file)
    
    if black_data is None or white_data is None:
        print("错误: 无法加载黑白参考数据")
        return
    
    calculator.set_calibration_mode(True, black_data, white_data)
    
    # 处理测试文件
    test_files = [
        "tu-berlin00004.csv",
        "tu-berlin00006.csv",
        "tu-berlin00007.csv"
    ]
    
    # MATLAB参考值（从文件中提取）
    matlab_ref_values = {
        "tu-berlin00004.csv": {"x": 0.3886, "y": 0.3184},
        "tu-berlin00006.csv": {"x": 0.3873, "y": 0.3188},
        "tu-berlin00007.csv": {"x": 0.3900, "y": 0.3198}
    }
    
    results = []
    
    for file_name in test_files:
        file_path = os.path.join(import_sample_dir, file_name)
        
        print(f"\n处理文件: {file_name}")
        
        # 1. 提取仪器值
        instrument_values = calculator.extract_instrument_values(file_path)
        if instrument_values is not None:
            print(f"仪器值: ({instrument_values[0]:.6f}, {instrument_values[1]:.6f})")
        else:
            print("未找到仪器值")
        
        # 2. 加载测量数据
        wavelengths, data = calculator.load_measurement_data(file_path)
        if wavelengths is None or data is None:
            print(f"错误: 无法加载测量数据: {file_path}")
            continue
        
        # 3. 计算反射率
        reflectance = calculator.calculate_reflectance(data, wavelengths)
        
        # 4. 计算XYZ值（使用新的完全匹配MATLAB的方法）
        xyz = calculator.calculate_xyz(reflectance, wavelengths, use_matlab_compatible=True)
        print(f"计算的XYZ值: X={xyz[0]:.6f}, Y={xyz[1]:.6f}, Z={xyz[2]:.6f}")
        
        # 5. 计算xy色度坐标
        xy = calculator.xyz_to_xy(xyz)
        print(f"计算的xy坐标: ({xy[0]:.6f}, {xy[1]:.6f})")
        
        # 6. 比较与MATLAB参考值的差异
        matlab_x = matlab_ref_values[file_name]["x"]
        matlab_y = matlab_ref_values[file_name]["y"]
        
        diff_x = abs(xy[0] - matlab_x)
        diff_y = abs(xy[1] - matlab_y)
        
        print(f"MATLAB参考值: ({matlab_x:.6f}, {matlab_y:.6f})")
        print(f"差异: Δx={diff_x:.6f}, Δy={diff_y:.6f}")
        
        # 7. 验证仪器值与MATLAB参考值是否一致
        if instrument_values is not None:
            inst_x_diff = abs(instrument_values[0] - matlab_x)
            inst_y_diff = abs(instrument_values[1] - matlab_y)
            
            print(f"仪器值与MATLAB参考值的差异: Δx={inst_x_diff:.6f}, Δy={inst_y_diff:.6f}")
            
            if inst_x_diff < 0.0001 and inst_y_diff < 0.0001:
                print("确认：MATLAB参考值与仪器值一致！")
        
        # 保存结果
        result = {
            'file': file_name,
            'calculated': xy,
            'matlab': (matlab_x, matlab_y),
            'instrument': instrument_values,
            'xyz': xyz
        }
        results.append(result)
    
    # 将结果保存到文件
    with open(os.path.join(output_dir, "matlab_match_results.txt"), 'w') as f:
        f.write("MATLAB匹配测试结果\n")
        f.write("=================\n\n")
        
        for result in results:
            f.write(f"文件: {result['file']}\n")
            
            xy = result['calculated']
            f.write(f"计算的xy坐标: ({xy[0]:.6f}, {xy[1]:.6f})\n")
            
            matlab = result['matlab']
            f.write(f"MATLAB参考值: ({matlab[0]:.6f}, {matlab[1]:.6f})\n")
            
            diff_x = abs(xy[0] - matlab[0])
            diff_y = abs(xy[1] - matlab[1])
            f.write(f"差异: Δx={diff_x:.6f}, Δy={diff_y:.6f}\n")
            
            if result['instrument'] is not None:
                inst = result['instrument']
                f.write(f"仪器xy坐标: ({inst[0]:.6f}, {inst[1]:.6f})\n")
            
            xyz = result['xyz']
            f.write(f"XYZ值: X={xyz[0]:.6f}, Y={xyz[1]:.6f}, Z={xyz[2]:.6f}\n\n")
    
    print(f"\n测试完成！结果已保存到 {os.path.join(output_dir, 'matlab_match_results.txt')}")

if __name__ == "__main__":
    main() 