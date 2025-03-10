#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的颜色计算函数
特别检查反射率计算和sRGB计算与MATLAB版本的一致性
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from color_calculator import ColorCalculator

# 测试数据目录
MATLAB_DATA_DIR = "Matlab_Input/Import_Sample"
OUTPUT_DIR = "test_calculation_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_csv_data(file_path):
    """加载CSV数据文件，特别处理MATLAB导出的CSV格式"""
    print(f"加载文件: {os.path.basename(file_path)}")
    
    try:
        # 首先尝试确定文件中的数据行
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # 查找数据开始行 - MATLAB导出的CSV文件通常在前53行包含元数据
        data_start_line = 0
        for i, line in enumerate(lines):
            if i > 50 and ',' in line:  # 假设数据行包含逗号
                try:
                    # 尝试将第一列转换为浮点数
                    parts = line.strip().split(',')
                    float(parts[0])
                    data_start_line = i
                    break
                except:
                    continue
        
        if data_start_line == 0:
            print(f"  无法确定数据开始行")
            return None, None
            
        print(f"  从第 {data_start_line+1} 行开始读取数据")
        
        # 从确定的行开始读取数值数据
        wavelengths = []
        values = []
        
        for line in lines[data_start_line:]:
            if ',' in line:
                try:
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        wavelength = float(parts[0])
                        value = float(parts[1])
                        wavelengths.append(wavelength)
                        values.append(value)
                except Exception as e:
                    # 跳过无法解析的行
                    pass
        
        # 转换为numpy数组
        wavelengths = np.array(wavelengths, dtype=np.float64)
        values = np.array(values, dtype=np.float64)
        
        if len(wavelengths) == 0:
            print(f"  未能提取有效数据")
            return None, None
            
        print(f"  成功加载: {len(wavelengths)}个数据点, 波长范围 {wavelengths.min():.1f}-{wavelengths.max():.1f} nm")
        return wavelengths, values
    except Exception as e:
        print(f"  加载文件出错: {str(e)}")
        return None, None

def test_reflectance_calculation():
    """测试反射率计算函数"""
    print("\n===== 测试反射率计算 =====")
    
    # 1. 加载黑白参考和测量数据
    black_file = os.path.join(MATLAB_DATA_DIR, "black.csv")
    white_file = os.path.join(MATLAB_DATA_DIR, "white.csv")
    
    if not os.path.isfile(black_file) or not os.path.isfile(white_file):
        print("找不到黑白参考文件")
        return
    
    black_wl, black_val = load_csv_data(black_file)
    white_wl, white_val = load_csv_data(white_file)
    
    if black_wl is None or white_wl is None:
        print("无法加载黑白参考数据")
        return
    
    # 2. 创建测试数据
    print("\n测试简单数据的反射率计算:")
    
    # 创建测试计算器
    calculator = ColorCalculator()
    
    # 设置简单的测试数据
    test_wavelengths = np.linspace(380, 780, 401)
    
    # 情况1: 普通测量数据
    print("\n情况1: 普通测量数据")
    test_measurement = np.linspace(0.01, 0.5, 401)  # 普通测量值
    test_black = np.ones(401) * 0.01  # 黑参考
    test_white = np.ones(401) * 0.8   # 白参考
    
    # 计算反射率
    calculator.set_calibration_mode(True, test_black, test_white)
    reflectance = calculator.calculate_reflectance(test_measurement, test_wavelengths)
    
    # 绘制结果
    plt.figure(figsize=(10, 6))
    plt.plot(test_wavelengths, reflectance)
    plt.title("测试数据反射率计算 - 情况1: 普通测量数据")
    plt.xlabel("波长 (nm)")
    plt.ylabel("反射率")
    plt.grid(True)
    plt.savefig(os.path.join(OUTPUT_DIR, "reflectance_test1.png"))
    plt.close()
    
    # 情况2: 包含一些测量值小于黑参考的数据，会产生负反射率
    print("\n情况2: 包含可能产生负反射率的数据")
    test_measurement2 = np.linspace(0.005, 0.5, 401)  # 部分值小于黑参考
    
    # 计算反射率
    calculator.set_calibration_mode(True, test_black, test_white)
    reflectance2 = calculator.calculate_reflectance(test_measurement2, test_wavelengths)
    
    # 绘制结果
    plt.figure(figsize=(10, 6))
    plt.plot(test_wavelengths, reflectance2)
    plt.title("测试数据反射率计算 - 情况2: 可能产生负反射率的数据")
    plt.xlabel("波长 (nm)")
    plt.ylabel("反射率")
    plt.grid(True)
    plt.savefig(os.path.join(OUTPUT_DIR, "reflectance_test2.png"))
    plt.close()
    
    # 情况3: 使用真实数据
    print("\n情况3: 使用真实数据")
    
    # 选择一个测量文件
    measurement_files = [f for f in os.listdir(MATLAB_DATA_DIR) 
                        if f.endswith('.csv') and f not in ['black.csv', 'white.csv']]
    
    if not measurement_files:
        print("找不到测量文件")
        return
    
    measurement_file = os.path.join(MATLAB_DATA_DIR, measurement_files[0])
    meas_wl, meas_val = load_csv_data(measurement_file)
    
    if meas_wl is None:
        print("无法加载测量数据")
        return
    
    # 计算反射率
    calculator.set_calibration_mode(True, black_val, white_val)
    reflectance3 = calculator.calculate_reflectance(meas_val, meas_wl)
    
    # 绘制结果
    plt.figure(figsize=(10, 6))
    plt.plot(meas_wl, reflectance3)
    plt.title(f"真实数据反射率计算 - {os.path.basename(measurement_file)}")
    plt.xlabel("波长 (nm)")
    plt.ylabel("反射率")
    plt.grid(True)
    plt.savefig(os.path.join(OUTPUT_DIR, "reflectance_real.png"))
    plt.close()
    
    return reflectance3, meas_wl

def test_srgb_calculation(reflectance=None, wavelengths=None):
    """测试sRGB计算函数"""
    print("\n===== 测试sRGB计算 =====")
    
    calculator = ColorCalculator()
    
    if reflectance is None or wavelengths is None:
        # 创建测试数据
        wavelengths = np.linspace(380, 780, 401)
        
        # 情况1: 标准白色 (反射率全为1)
        reflectance = np.ones(401)
        
    # 计算XYZ值
    xyz = calculator.calculate_xyz(reflectance, wavelengths)
    print(f"XYZ值: {xyz}")
    
    # 计算xy色度坐标
    xy = calculator.xyz_to_xy(xyz)
    print(f"xy色度坐标: {xy}")
    
    # 计算线性RGB值
    rgb_linear = calculator.xyz_to_linear_rgb(xyz)
    print(f"线性RGB值: {rgb_linear}")
    
    # 计算gamma校正后的RGB值
    rgb_gamma = calculator.linear_to_gamma_rgb(rgb_linear)
    print(f"gamma校正后的RGB值: {rgb_gamma}")
    
    # 转换为16进制色彩代码
    hex_color = calculator.rgb_to_hex(rgb_gamma)
    print(f"16进制色彩代码: {hex_color}")
    
    # 绘制颜色方块
    plt.figure(figsize=(3, 3))
    plt.axes([0, 0, 1, 1], frameon=False)
    plt.fill([0, 1, 1, 0], [0, 0, 1, 1], color=rgb_gamma)
    plt.axis('off')
    plt.savefig(os.path.join(OUTPUT_DIR, "color_test.png"))
    plt.close()

def main():
    """主函数"""
    print("====== 颜色计算测试 ======")
    
    # 测试反射率计算
    reflectance, wavelengths = test_reflectance_calculation()
    
    # 测试sRGB计算
    test_srgb_calculation(reflectance, wavelengths)
    
    print("\n测试完成! 结果保存在:", OUTPUT_DIR)

if __name__ == "__main__":
    main() 