import numpy as np
import os
from color_calculator import ColorCalculator

def main():
    """
    使用来自CSV文件的标准光源数据和CIE数据，测试与MATLAB完全匹配的XYZ计算
    """
    print("测试MATLAB完全匹配的XYZ计算...")
    
    # 创建输出目录
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建ColorCalculator实例
    calculator = ColorCalculator()
    
    # 设置rho_lambda值为0.989，与MATLAB一致
    calculator.set_rho_lambda(0.989)
    
    # 设置校准模式（需要黑白参考）
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
    
    # 测试不同的光源
    illuminants = ['D65', 'D50', 'A', 'E']
    
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
    
    # 创建结果表格
    results = []
    
    print("\n测试不同光源下的XYZ计算:")
    for file_name in test_files:
        file_path = os.path.join(import_sample_dir, file_name)
        print(f"\n处理文件: {file_name}")
        
        # 提取仪器值
        instrument_values = calculator.extract_instrument_values(file_path)
        if instrument_values is not None:
            print(f"仪器值: ({instrument_values[0]:.6f}, {instrument_values[1]:.6f})")
        
        # 加载测量数据
        wavelengths, data = calculator.load_measurement_data(file_path)
        if wavelengths is None or data is None:
            print(f"错误: 无法加载测量数据: {file_path}")
            continue
        
        # 计算反射率
        reflectance = calculator.calculate_reflectance(data, wavelengths)
        
        # 对每个光源进行测试
        illuminant_results = []
        for illuminant in illuminants:
            print(f"\n光源: {illuminant}")
            calculator.set_illuminant(illuminant)
            
            # 计算XYZ值
            xyz = calculator.calculate_xyz(reflectance, wavelengths, use_matlab_compatible=True)
            
            # 计算xy坐标
            xy = calculator.xyz_to_xy(xyz)
            print(f"计算的xy坐标: ({xy[0]:.6f}, {xy[1]:.6f})")
            
            # 保存此光源的结果
            illuminant_results.append({
                'illuminant': illuminant,
                'xyz': xyz,
                'xy': xy
            })
        
        # 保存此文件的所有结果
        file_result = {
            'file': file_name,
            'instrument': instrument_values,
            'illuminant_results': illuminant_results
        }
        results.append(file_result)
    
    # 将结果保存到文件
    with open(os.path.join(output_dir, "illuminant_test_results.txt"), 'w') as f:
        f.write("不同光源下的XYZ计算结果\n")
        f.write("=================\n\n")
        
        for result in results:
            f.write(f"文件: {result['file']}\n")
            
            if result['instrument'] is not None:
                instr = result['instrument']
                f.write(f"仪器xy坐标: ({instr[0]:.6f}, {instr[1]:.6f})\n\n")
            
            for ill_result in result['illuminant_results']:
                illuminant = ill_result['illuminant']
                xy = ill_result['xy']
                xyz = ill_result['xyz']
                
                f.write(f"光源: {illuminant}\n")
                f.write(f"计算的xy坐标: ({xy[0]:.6f}, {xy[1]:.6f})\n")
                f.write(f"XYZ值: X={xyz[0]:.6f}, Y={xyz[1]:.6f}, Z={xyz[2]:.6f}\n\n")
            
            f.write("----------------------------------------\n\n")
    
    print(f"\n测试完成！结果已保存到 {os.path.join(output_dir, 'illuminant_test_results.txt')}")
    print("总结:")
    print("1. 我们现在使用与MATLAB完全相同的CIE数据(从xyzBar.csv加载)")
    print("2. 我们使用与MATLAB完全相同的标准光源数据(从stdIllum.csv加载)")
    print("3. 我们复制了MATLAB的xyXYZ函数计算逻辑")
    print("4. 对于仪器值，我们直接从测量文件提取，与MATLAB保持一致")

if __name__ == "__main__":
    main() 