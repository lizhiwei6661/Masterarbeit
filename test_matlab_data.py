#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MATLAB数据导入测试脚本
用于测试从MATLAB导出的数据格式的加载和处理
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb
from color_calculator import ColorCalculator

# 设置路径
MATLAB_DATA_DIR = "../Matlab_Input/Import_Sample"
OUTPUT_DIR = "test_results"

def load_csv_data(file_path):
    """
    加载CSV文件中的数据
    
    参数:
        file_path: CSV文件路径
        
    返回:
        (wavelengths, values)元组
    """
    print(f"加载文件: {os.path.basename(file_path)}")
    
    try:
        # 尝试使用pandas加载数据
        df = pd.read_csv(file_path, header=None)
        
        # 简单检查数据格式
        if df.shape[1] >= 2:
            wavelengths = df.iloc[:, 0].values
            values = df.iloc[:, 1].values
            
            # 确保数据是数值型
            wavelengths = np.array(wavelengths, dtype=np.float64)
            values = np.array(values, dtype=np.float64)
            
            print(f"  成功加载: {len(wavelengths)}个数据点, 波长范围 {wavelengths.min():.1f}-{wavelengths.max():.1f} nm")
            return wavelengths, values
        else:
            print(f"  错误: 文件格式无效，应至少包含两列数据")
            return None, None
            
    except Exception as e:
        print(f"  加载文件出错: {str(e)}")
        return None, None

def test_aleksameter_mode(black_file, white_file, measurement_file):
    """
    测试Aleksameter模式
    
    参数:
        black_file: 黑参考文件路径
        white_file: 白参考文件路径
        measurement_file: 测量文件路径
    """
    print("\n======== 测试Aleksameter模式 ========")
    print(f"黑参考: {os.path.basename(black_file)}")
    print(f"白参考: {os.path.basename(white_file)}")
    print(f"测量文件: {os.path.basename(measurement_file)}")
    
    # 1. 加载数据
    black_wl, black_val = load_csv_data(black_file)
    white_wl, white_val = load_csv_data(white_file)
    meas_wl, meas_val = load_csv_data(measurement_file)
    
    if black_wl is None or white_wl is None or meas_wl is None:
        print("数据加载失败，无法继续测试")
        return
    
    # 2. 检查波长匹配
    print("检查波长匹配...")
    
    if not np.array_equal(black_wl, white_wl) or not np.array_equal(black_wl, meas_wl):
        print("  波长数据不匹配，尝试校准...")
        
        # 找到共同的波长范围
        min_wl = max(np.min(black_wl), np.min(white_wl), np.min(meas_wl))
        max_wl = min(np.max(black_wl), np.max(white_wl), np.max(meas_wl))
        
        print(f"  共同波长范围: {min_wl:.1f}-{max_wl:.1f} nm")
        
        # 检查是否有足够的重叠范围
        if min_wl >= max_wl:
            print("  错误: 波长范围没有重叠部分")
            return
    
    # 3. 创建颜色计算器并设置校准模式
    calculator = ColorCalculator()
    calculator.set_calibration_mode(True, black_val, white_val)
    
    # 4. 处理测量数据
    print("\n处理测量数据...")
    result = calculator.process_measurement(meas_val, meas_wl)
    
    # 5. 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 6. 保存结果
    base_name = os.path.splitext(os.path.basename(measurement_file))[0]
    
    # 保存反射率图像
    plt.figure(figsize=(10, 6))
    plt.plot(meas_wl, result['reflectance'])
    plt.xlabel('波长 (nm)')
    plt.ylabel('反射率')
    plt.title(f'反射率曲线 - {base_name}')
    plt.grid(True)
    plt.savefig(os.path.join(OUTPUT_DIR, f"{base_name}_reflectance.png"), dpi=300)
    plt.close()
    
    # 保存色块
    plt.figure(figsize=(3, 3))
    plt.axes([0, 0, 1, 1], frameon=False)
    plt.fill([0, 1, 1, 0], [0, 0, 1, 1], color=result['rgb_gamma'])
    plt.axis('off')
    plt.savefig(os.path.join(OUTPUT_DIR, f"{base_name}_color.png"), dpi=300)
    plt.close()
    
    print("测试结果:")
    print(f"  XYZ: ({result['xyz'][0]:.6f}, {result['xyz'][1]:.6f}, {result['xyz'][2]:.6f})")
    print(f"  xy: ({result['xy'][0]:.6f}, {result['xy'][1]:.6f})")
    print(f"  RGB: ({result['rgb_gamma'][0]:.6f}, {result['rgb_gamma'][1]:.6f}, {result['rgb_gamma'][2]:.6f})")
    print(f"  颜色: {result['hex_color']}")
    
    return result

def main():
    """主函数"""
    print("======== MATLAB数据测试 ========")
    
    # 检查MATLAB数据目录是否存在
    if not os.path.isdir(MATLAB_DATA_DIR):
        print(f"错误: MATLAB数据目录不存在: {MATLAB_DATA_DIR}")
        return
    
    # 寻找黑白参考文件
    black_file = os.path.join(MATLAB_DATA_DIR, "black.csv")
    white_file = os.path.join(MATLAB_DATA_DIR, "white.csv")
    
    if not os.path.isfile(black_file):
        print(f"错误: 黑参考文件不存在: {black_file}")
        return
    
    if not os.path.isfile(white_file):
        print(f"错误: 白参考文件不存在: {white_file}")
        return
    
    # 找到所有测量文件
    measurement_files = []
    for file in os.listdir(MATLAB_DATA_DIR):
        if file.lower().endswith('.csv') and 'black' not in file.lower() and 'white' not in file.lower():
            measurement_files.append(os.path.join(MATLAB_DATA_DIR, file))
    
    if not measurement_files:
        print("错误: 未找到测量文件")
        return
        
    print(f"找到 {len(measurement_files)} 个测量文件")
    
    # 测试每个文件
    for measurement_file in measurement_files:
        test_aleksameter_mode(black_file, white_file, measurement_file)

if __name__ == "__main__":
    main() 