#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试XYZ计算是否与MATLAB结果一致
使用与MATLAB相同的计算方法，验证结果是否匹配
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from color_calculator import ColorCalculator

# 测试数据目录
MATLAB_DATA_DIR = "Matlab_Input/Import_Sample"
OUTPUT_DIR = "test_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_csv_data(file_path):
    """加载CSV数据文件，特别处理MATLAB导出的CSV格式"""
    print(f"加载文件: {os.path.basename(file_path)}")
    
    try:
        # 首先尝试确定文件中的数据行
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # 查找数据开始行
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
            parts = line.strip().split(',')
            if len(parts) >= 2:
                try:
                    wavelength = float(parts[0])
                    value = float(parts[1])
                    wavelengths.append(wavelength)
                    values.append(value)
                except:
                    continue
        
        if len(wavelengths) == 0:
            print("  未找到有效数据")
            return None, None
            
        print(f"  成功提取 {len(wavelengths)} 个数据点")
        return np.array(wavelengths), np.array(values)
        
    except Exception as e:
        print(f"  加载文件时出错: {str(e)}")
        return None, None

def print_data_info(wavelengths, values, name):
    """打印数据信息"""
    if wavelengths is None or values is None:
        print(f"{name} 数据无效")
        return
        
    print(f"{name} 数据范围: {wavelengths[0]}-{wavelengths[-1]}nm, {len(wavelengths)}点")
    print(f"{name} 数据波长步长: {wavelengths[1]-wavelengths[0]}nm")
    print(f"{name} 数据值范围: {np.min(values):.6e}-{np.max(values):.6e}")

def print_cie_data_info(calculator):
    """打印CIE数据信息"""
    # 检查CIE数据
    cie_wavelengths = calculator.cie_1931['wavelengths']
    cie_x = calculator.cie_1931['x']
    cie_y = calculator.cie_1931['y']
    cie_z = calculator.cie_1931['z']
    
    print(f"CIE 1931观察者函数波长范围: {cie_wavelengths[0]}-{cie_wavelengths[-1]}nm, {len(cie_wavelengths)}点")
    print(f"CIE x值范围: {np.min(cie_x):.4f}-{np.max(cie_x):.4f}")
    print(f"CIE y值范围: {np.min(cie_y):.4f}-{np.max(cie_y):.4f}")
    print(f"CIE z值范围: {np.min(cie_z):.4f}-{np.max(cie_z):.4f}")
    
    # 检查D65光源数据
    illuminant_data = calculator.illuminants['D65']
    print(f"D65光源数据点数: {len(illuminant_data)}")
    print(f"D65光源值范围: {np.min(illuminant_data):.4f}-{np.max(illuminant_data):.4f}")
    
    # 打印特定波长点的值
    check_wavelengths = [380, 400, 500, 600, 700, 780]
    
    print("\n特定波长点的数据:")
    print(f"{'波长(nm)':<10} {'CIE x':<10} {'CIE y':<10} {'CIE z':<10} {'D65':<10}")
    print(f"{'-'*50}")
    
    for wl in check_wavelengths:
        idx = np.where(cie_wavelengths == wl)[0][0]
        print(f"{wl:<10} {cie_x[idx]:<10.4f} {cie_y[idx]:<10.4f} {cie_z[idx]:<10.4f} {illuminant_data[idx]:<10.4f}")

def test_xyz_calculation():
    """测试XYZ计算与MATLAB的一致性"""
    print("\n===== 测试XYZ计算与MATLAB的一致性 =====")
    
    # 创建计算器对象
    calculator = ColorCalculator()
    
    # 打印CIE数据信息
    print_cie_data_info(calculator)
    
    # 设置rho_lambda值为0.989（与MATLAB一致）
    calculator.set_rho_lambda(0.989)
    print(f"设置rho_lambda值为: {calculator.rho_lambda}")
    
    # 加载黑白参考数据
    black_file = os.path.join(MATLAB_DATA_DIR, "black.csv")
    white_file = os.path.join(MATLAB_DATA_DIR, "white.csv")
    
    black_wavelengths, black_values = load_csv_data(black_file)
    white_wavelengths, white_values = load_csv_data(white_file)
    
    print("\n===== 参考数据信息 =====")
    print_data_info(black_wavelengths, black_values, "黑参考")
    print_data_info(white_wavelengths, white_values, "白参考")
    
    # 设置校准模式
    calculator.set_calibration_mode(True, black_values, white_values)
    
    # 测试文件列表
    test_files = [
        "tu-berlin00004.csv",
        "tu-berlin00006.csv",
        "tu-berlin00007.csv"
    ]
    
    # MATLAB中的参考xy值
    matlab_xy_values = {
        "tu-berlin00004.csv": (0.3886, 0.3184),
        "tu-berlin00006.csv": (0.3459, 0.3149),
        "tu-berlin00007.csv": (0.3404, 0.3147)
    }
    
    # 创建结果表格
    results = []
    
    # 处理每个测试文件
    for test_file in test_files:
        file_path = os.path.join(MATLAB_DATA_DIR, test_file)
        
        # 加载测量数据
        wavelengths, values = load_csv_data(file_path)
        print(f"\n===== 处理文件: {test_file} =====")
        print_data_info(wavelengths, values, "测量数据")
        
        # 计算反射率
        reflectance = calculator.calculate_reflectance(values, wavelengths)
        
        # 手动计算特定波长点（380nm）的反射率值，用于验证
        idx_380 = np.where(wavelengths == 380)[0][0]
        black_380 = black_values[idx_380]
        white_380 = white_values[idx_380]
        measurement_380 = values[idx_380]
        reflectance_380_calc = ((measurement_380 - black_380) / (white_380 - black_380)) * (white_380 / measurement_380) * calculator.rho_lambda
        print(f"\n380nm处的反射率计算验证:")
        print(f"黑参考值: {black_380:.6f}")
        print(f"白参考值: {white_380:.6f}")
        print(f"测量值: {measurement_380:.6f}")
        print(f"计算公式: ((measurement - black) / (white - black)) * (white / measurement) * rho_lambda")
        print(f"手动计算结果: {reflectance_380_calc:.6f}")
        print(f"函数计算结果: {reflectance[idx_380]:.6f}")
        print(f"差异: {abs(reflectance_380_calc - reflectance[idx_380]):.9f}")
        
        # 使用两种方法计算XYZ值
        print("\n=== 使用MATLAB兼容方法计算 ===")
        xyz_matlab = calculator.calculate_xyz(reflectance, wavelengths, use_matlab_compatible=True)
        xy_matlab = calculator.xyz_to_xy(xyz_matlab)
        
        print("\n=== 使用标准方法计算 ===")
        xyz_standard = calculator.calculate_xyz(reflectance, wavelengths, use_matlab_compatible=False)
        xy_standard = calculator.xyz_to_xy(xyz_standard)
        
        # 获取MATLAB参考值
        matlab_xy = matlab_xy_values.get(test_file, (0, 0))
        
        # 计算差异
        diff_x_matlab = abs(xy_matlab[0] - matlab_xy[0])
        diff_y_matlab = abs(xy_matlab[1] - matlab_xy[1])
        diff_x_standard = abs(xy_standard[0] - matlab_xy[0])
        diff_y_standard = abs(xy_standard[1] - matlab_xy[1])
        
        # 打印结果
        print(f"\n=== 结果比较 ===")
        print(f"MATLAB兼容方法: XYZ=({xyz_matlab[0]:.6f}, {xyz_matlab[1]:.6f}, {xyz_matlab[2]:.6f}), xy=({xy_matlab[0]:.6f}, {xy_matlab[1]:.6f})")
        print(f"标准方法: XYZ=({xyz_standard[0]:.6f}, {xyz_standard[1]:.6f}, {xyz_standard[2]:.6f}), xy=({xy_standard[0]:.6f}, {xy_standard[1]:.6f})")
        print(f"MATLAB参考值: xy=({matlab_xy[0]:.6f}, {matlab_xy[1]:.6f})")
        print(f"MATLAB兼容方法差异: Δx={diff_x_matlab:.6f}, Δy={diff_y_matlab:.6f}")
        print(f"标准方法差异: Δx={diff_x_standard:.6f}, Δy={diff_y_standard:.6f}")
        
        # 添加到结果表格
        results.append({
            "文件名": test_file,
            "X_matlab": xyz_matlab[0],
            "Y_matlab": xyz_matlab[1],
            "Z_matlab": xyz_matlab[2],
            "x_matlab": xy_matlab[0],
            "y_matlab": xy_matlab[1],
            "X_standard": xyz_standard[0],
            "Y_standard": xyz_standard[1],
            "Z_standard": xyz_standard[2],
            "x_standard": xy_standard[0],
            "y_standard": xy_standard[1],
            "MATLAB_x": matlab_xy[0],
            "MATLAB_y": matlab_xy[1],
            "Δx_matlab": diff_x_matlab,
            "Δy_matlab": diff_y_matlab,
            "Δx_standard": diff_x_standard,
            "Δy_standard": diff_y_standard
        })
        
    # 将结果保存到CSV文件
    results_df = pd.DataFrame(results)
    results_path = os.path.join(OUTPUT_DIR, "xyz_calculation_comparison.csv")
    results_df.to_csv(results_path, index=False)
    print(f"\n结果已保存到: {results_path}")
    
    return results

if __name__ == "__main__":
    test_xyz_calculation() 