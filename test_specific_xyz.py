"""
测试特定XYZ值的sRGB计算
"""
import os
import sys
import numpy as np
from color_calculator import ColorCalculator

def main():
    # 初始化颜色计算器
    calculator = ColorCalculator()
    
    # 用户提到文件0004的正确计算结果应该是 [1.1356, 0.38769, 0]
    # 我们需要找出对应的XYZ值
    
    # 从文件导入数据（如果可用），或者使用一系列测试值
    test_xyz_values = [
        # 从tu-berlin00004.csv中提取的值（如果不准确，请手动调整）
        [33.0124, 26.9701, 9.9889],   # 这是一个示例值，需要确认
        # 其他测试值
        [35.0, 28.0, 10.0],
        [32.0, 26.0, 9.0],
        [34.0, 27.0, 10.0],
        [33.0, 27.0, 10.0]
    ]
    
    print("测试特定XYZ值:")
    print("-" * 100)
    
    for xyz in test_xyz_values:
        print(f"XYZ值: {xyz}")
        
        # 计算线性RGB
        rgb_linear = calculator.xyz_to_linear_rgb(xyz)
        print(f"线性RGB: {rgb_linear}")
        
        # 计算Gamma RGB
        rgb_gamma = calculator.linear_to_gamma_rgb(rgb_linear)
        print(f"Gamma RGB: {rgb_gamma}")
        print("-" * 50)
    
    # 读取CSV文件
    try:
        from importlib import import_module
        if os.path.exists("data_import.py"):
            data_import = import_module("data_import")
            
            # 尝试导入tu-berlin00004.csv
            file_path = "Matlab_Input/Import_Sample/tu-berlin00004.csv"
            if os.path.exists(file_path):
                print(f"\n从文件导入: {file_path}")
                
                # 使用ColorCalculator的加载函数
                wavelengths, values = calculator.load_measurement_data(file_path)
                
                # 计算XYZ值
                print("计算反射率和XYZ值...")
                
                # 尝试读取黑白参考文件
                black_file = "Matlab_Input/Import_Sample/black.csv"
                white_file = "Matlab_Input/Import_Sample/white.csv"
                
                if os.path.exists(black_file) and os.path.exists(white_file):
                    black_wavelengths, black_values = calculator.load_measurement_data(black_file)
                    white_wavelengths, white_values = calculator.load_measurement_data(white_file)
                    
                    # 设置校准模式
                    calculator.set_calibration_mode(True, black_values, white_values)
                    
                    # 计算反射率
                    reflectance = calculator.calculate_reflectance(values, wavelengths)
                    
                    # 计算XYZ
                    xyz = calculator.calculate_xyz(reflectance, wavelengths)
                    print(f"计算得到的XYZ值: {xyz}")
                    
                    # 计算RGB
                    rgb_linear = calculator.xyz_to_linear_rgb(xyz)
                    print(f"线性RGB: {rgb_linear}")
                    
                    # 计算Gamma RGB
                    rgb_gamma = calculator.linear_to_gamma_rgb(rgb_linear)
                    print(f"Gamma RGB: {rgb_gamma}")
                    
                    # 检查是否与预期结果相符
                    expected = [1.1356, 0.38769, 0]
                    print(f"预期的RGB值: {expected}")
                    difference = np.array(expected) - rgb_linear
                    print(f"差异: {difference}")
                    
                else:
                    print("无法找到黑白参考文件")
    except Exception as e:
        print(f"导入或处理数据时出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n结论:")
    print("请比较输出结果与预期值 [1.1356, 0.38769, 0]")
    print("如果二者接近，则说明修改成功。")

if __name__ == "__main__":
    main() 