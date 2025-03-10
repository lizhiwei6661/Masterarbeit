import numpy as np
import os
from color_calculator import ColorCalculator

def main():
    """
    测试最终解决方案：使用CSV文件中的CIE数据并优先使用仪器值
    """
    print("测试最终解决方案...")
    
    # 创建输出目录
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建ColorCalculator实例
    calculator = ColorCalculator()
    
    # 打印CIE数据信息
    cie_data = calculator.cie_1931
    print(f"\nCIE数据信息:")
    print(f"数据点数: {len(cie_data['wavelengths'])}")
    print(f"波长范围: {cie_data['wavelengths'][0]}-{cie_data['wavelengths'][-1]}nm")
    print(f"波长步长: {cie_data['wavelengths'][1] - cie_data['wavelengths'][0]}nm")
    
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
    calculator.set_rho_lambda(0.989)  # 与MATLAB一致
    
    # 处理测试文件
    test_files = [
        "tu-berlin00004.csv",
        "tu-berlin00006.csv",
        "tu-berlin00007.csv"
    ]
    
    results = []
    
    print("\n比较仪器值与计算值:")
    print("=" * 60)
    print(f"{'文件名':<20} | {'仪器值':<20} | {'计算值':<20}")
    print("-" * 60)
    
    for file_name in test_files:
        file_path = os.path.join(import_sample_dir, file_name)
        
        # 1. 使用仪器值（默认优先使用仪器值）
        instrument_xy, source_instrument = calculator.get_xy_coordinates(file_path, use_instrument_values=True)
        
        # 2. 使用计算值
        calculated_xy, source_calculated = calculator.get_xy_coordinates(file_path, use_instrument_values=False)
        
        # 打印结果
        instr_str = f"({instrument_xy[0]:.4f}, {instrument_xy[1]:.4f})"
        calc_str = f"({calculated_xy[0]:.4f}, {calculated_xy[1]:.4f})"
        print(f"{file_name:<20} | {instr_str:<20} | {calc_str:<20}")
        
        # 保存结果
        results.append({
            'file': file_name,
            'instrument': instrument_xy,
            'calculated': calculated_xy
        })
    
    print("=" * 60)
    
    # 将结果保存到文件
    with open(os.path.join(output_dir, "final_solution_results.txt"), 'w') as f:
        f.write("最终解决方案测试结果\n")
        f.write("=================\n\n")
        f.write("使用最新的CSV数据源和优先使用仪器值的方案\n\n")
        
        for result in results:
            f.write(f"文件: {result['file']}\n")
            
            instr = result['instrument']
            f.write(f"仪器xy坐标: ({instr[0]:.6f}, {instr[1]:.6f})\n")
            
            calc = result['calculated']
            f.write(f"计算xy坐标: ({calc[0]:.6f}, {calc[1]:.6f})\n")
            
            diff_x = abs(calc[0] - instr[0])
            diff_y = abs(calc[1] - instr[1])
            f.write(f"差异: Δx={diff_x:.6f}, Δy={diff_y:.6f}\n\n")
    
    print(f"\n测试完成！结果已保存到 {os.path.join(output_dir, 'final_solution_results.txt')}")
    print("总结: MATLAB使用仪器值作为xy坐标，而不是通过反射率计算。")
    print("      我们的解决方案提供了两种选择：使用仪器值与MATLAB完全一致，或使用标准计算方法。")

if __name__ == "__main__":
    main() 