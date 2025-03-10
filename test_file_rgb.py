"""
直接处理tu-berlin00004.csv文件，显示rgb_linear和rgb_gamma值
"""
from color_calculator import ColorCalculator
import os

def main():
    # 初始化颜色计算器
    calculator = ColorCalculator()
    
    # 文件路径
    file_path = "Matlab_Input/Import_Sample/tu-berlin00004.csv"
    black_file = "Matlab_Input/Import_Sample/black.csv"
    white_file = "Matlab_Input/Import_Sample/white.csv"
    
    # 检查文件是否存在
    if not os.path.exists(file_path) or not os.path.exists(black_file) or not os.path.exists(white_file):
        print("文件不存在，请检查路径")
        return
    
    # 加载数据
    wavelengths, values = calculator.load_measurement_data(file_path)
    black_wavelengths, black_values = calculator.load_measurement_data(black_file)
    white_wavelengths, white_values = calculator.load_measurement_data(white_file)
    
    print(f"成功加载测量数据: {len(wavelengths)}点, 范围: {wavelengths[0]}-{wavelengths[-1]}nm")
    
    # 设置校准模式
    calculator.set_calibration_mode(True, black_values, white_values)
    
    # 计算反射率
    reflectance = calculator.calculate_reflectance(values, wavelengths)
    
    # 计算XYZ
    xyz = calculator.calculate_xyz(reflectance, wavelengths)
    print(f"XYZ值: {xyz}")
    
    # 计算xy
    xy = calculator.xyz_to_xy(xyz)
    print(f"xy坐标: {xy}")
    
    # 计算线性RGB
    rgb_linear = calculator.xyz_to_linear_rgb(xyz)
    print(f"线性RGB: {rgb_linear}")
    
    # 计算Gamma RGB
    rgb_gamma = calculator.linear_to_gamma_rgb(rgb_linear)
    print(f"Gamma RGB: {rgb_gamma}")
    
    # 目标值
    target_rgb_linear = [1.1356, 0.38769, 0]
    print(f"目标线性RGB: {target_rgb_linear}")
    
    # 验证差异
    print(f"线性RGB差异: {[rgb_linear[i] - target_rgb_linear[i] for i in range(3)]}")
    
    # 手动计算Gamma校正
    print("\n手动计算Gamma校正:")
    values = rgb_linear.copy()
    gamma_corrected = []
    
    for val in values:
        if val <= 0.0031308:
            gamma = 12.92 * val
            if val < 0:
                gamma = 0
        else:
            gamma = 1.055 * (val ** (1/2.4)) - 0.055
        gamma_corrected.append(gamma)
    
    print(f"手动计算结果: {gamma_corrected}")
    print(f"与自动计算差异: {[gamma_corrected[i] - rgb_gamma[i] for i in range(3)]}")
    
if __name__ == "__main__":
    main() 