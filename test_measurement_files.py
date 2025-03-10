import numpy as np
import os
from color_calculator import ColorCalculator

def main():
    """
    测试使用CSV加载的CIE数据处理实际测量文件
    """
    print("测试使用CSV加载的CIE数据处理实际测量文件...")
    
    # 创建输出目录
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建ColorCalculator实例
    calculator = ColorCalculator()
    
    # 设置rho_lambda值为0.989，与MATLAB一致
    calculator.set_rho_lambda(0.989)
    
    # 设置校准模式（需要黑白参考）
    matlab_data_dir = "Matlab_Input/data"
    black_file = os.path.join(matlab_data_dir, "black.csv")
    white_file = os.path.join(matlab_data_dir, "white.csv")
    
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
    
    results = []
    
    for file_name in test_files:
        file_path = os.path.join(matlab_data_dir, file_name)
        
        print(f"\n处理文件: {file_name}")
        
        # 1. 提取仪器值
        instrument_values = calculator.extract_instrument_values(file_path)
        if instrument_values is not None:
            print(f"提取到的仪器值: ({instrument_values[0]:.6f}, {instrument_values[1]:.6f})")
        else:
            print("未找到仪器值")
        
        # 2. 加载测量数据
        wavelengths, data = calculator.load_measurement_data(file_path)
        if wavelengths is None or data is None:
            print(f"错误: 无法加载测量数据: {file_path}")
            continue
        
        print(f"加载的测量数据: {len(wavelengths)}点, 波长范围: {wavelengths[0]}-{wavelengths[-1]}nm")
        
        # 3. 计算反射率
        reflectance = calculator.calculate_reflectance(data, wavelengths)
        print(f"反射率范围: {np.min(reflectance):.4f}-{np.max(reflectance):.4f}")
        
        # 4. 计算XYZ值（使用CSV加载的数据）
        xyz = calculator.calculate_xyz(reflectance, wavelengths, use_matlab_compatible=True)
        print(f"XYZ值: X={xyz[0]:.6f}, Y={xyz[1]:.6f}, Z={xyz[2]:.6f}")
        
        # 5. 计算xy色度坐标
        xy = calculator.xyz_to_xy(xyz)
        print(f"计算的xy坐标: ({xy[0]:.6f}, {xy[1]:.6f})")
        
        # 6. 比较计算值与仪器值
        if instrument_values is not None:
            x_diff = abs(xy[0] - instrument_values[0])
            y_diff = abs(xy[1] - instrument_values[1])
            print(f"与仪器值的差异: Δx={x_diff:.6f}, Δy={y_diff:.6f}")
            
        # 保存结果
        result = {
            'file': file_name,
            'calculated': xy,
            'instrument': instrument_values,
            'xyz': xyz
        }
        results.append(result)
    
    # 将结果保存到文件
    with open(os.path.join(output_dir, "measurement_results.txt"), 'w') as f:
        f.write("测量文件处理结果\n")
        f.write("=================\n\n")
        
        for result in results:
            f.write(f"文件: {result['file']}\n")
            
            xy = result['calculated']
            f.write(f"计算的xy坐标: ({xy[0]:.6f}, {xy[1]:.6f})\n")
            
            if result['instrument'] is not None:
                inst = result['instrument']
                f.write(f"仪器xy坐标: ({inst[0]:.6f}, {inst[1]:.6f})\n")
                
                x_diff = abs(xy[0] - inst[0])
                y_diff = abs(xy[1] - inst[1])
                f.write(f"差异: Δx={x_diff:.6f}, Δy={y_diff:.6f}\n")
            
            xyz = result['xyz']
            f.write(f"XYZ值: X={xyz[0]:.6f}, Y={xyz[1]:.6f}, Z={xyz[2]:.6f}\n\n")
    
    print(f"\n测试完成！结果已保存到 {os.path.join(output_dir, 'measurement_results.txt')}")

if __name__ == "__main__":
    main() 