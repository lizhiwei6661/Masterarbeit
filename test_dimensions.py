#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
维度匹配测试脚本
专门用于测试401点测量数据和81点CIE观察者函数之间的维度匹配问题
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from color_calculator import ColorCalculator

# 测试数据路径
MATLAB_DATA_DIR = "Matlab_Input/Import_Sample"

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

def test_dimensions():
    """测试维度匹配问题"""
    print("\n===== 维度匹配测试 =====")
    
    # 1. 加载测试数据
    black_file = os.path.join(MATLAB_DATA_DIR, "black.csv")
    white_file = os.path.join(MATLAB_DATA_DIR, "white.csv")
    measurement_file = os.path.join(MATLAB_DATA_DIR, "tu-berlin00004.csv")
    
    if not os.path.isfile(black_file) or not os.path.isfile(white_file) or not os.path.isfile(measurement_file):
        print("无法找到测试文件")
        return
    
    black_wl, black_val = load_csv_data(black_file)
    white_wl, white_val = load_csv_data(white_file)
    meas_wl, meas_val = load_csv_data(measurement_file)
    
    if black_wl is None or white_wl is None or meas_wl is None:
        print("数据加载失败")
        return
    
    # 2. 输出数据维度
    print("\n数据维度信息:")
    print(f"黑参考: {len(black_wl)}点, 波长范围: {black_wl.min():.1f}-{black_wl.max():.1f} nm")
    print(f"白参考: {len(white_wl)}点, 波长范围: {white_wl.min():.1f}-{white_wl.max():.1f} nm")
    print(f"测量数据: {len(meas_wl)}点, 波长范围: {meas_wl.min():.1f}-{meas_wl.max():.1f} nm")
    
    # 3. 创建计算器实例
    calculator = ColorCalculator()
    
    # 4. 输出CIE标准观察者函数维度
    print("\nCIE标准观察者函数信息:")
    print(f"CIE1931: {len(calculator.cie_1931['wavelengths'])}点, 波长范围: {calculator.cie_1931['wavelengths'].min():.1f}-{calculator.cie_1931['wavelengths'].max():.1f} nm")
    
    # 5. 测试计算过程
    print("\n测试数据处理流程:")
    
    # 设置校准模式
    calculator.set_calibration_mode(True, black_val, white_val)
    
    # 处理测量数据并捕获任何错误
    try:
        print("处理测量数据...")
        result = calculator.process_measurement(meas_val, meas_wl)
        
        if result:
            print("\n计算结果:")
            print(f"XYZ: ({result['xyz'][0]:.6f}, {result['xyz'][1]:.6f}, {result['xyz'][2]:.6f})")
            print(f"xy: ({result['xy'][0]:.6f}, {result['xy'][1]:.6f})")
            print(f"RGB: ({result['rgb_gamma'][0]:.6f}, {result['rgb_gamma'][1]:.6f}, {result['rgb_gamma'][2]:.6f})")
            print(f"颜色: {result['hex_color']}")
            
            # 7. 测试绘图过程
            print("\n测试绘图:")
            try:
                # 保存反射率图 - 测试图形尺寸是否匹配
                plt.figure(figsize=(10, 6))
                plt.plot(meas_wl, result['reflectance'])
                plt.xlabel('波长 (nm)')
                plt.ylabel('反射率')
                plt.title('反射率曲线测试')
                plt.grid(True)
                plt.savefig("test_reflectance.png")
                plt.close()
                print("成功保存反射率图形")
                
                # 检查维度是否匹配
                print(f"绘图数据维度: x={len(meas_wl)}, y={len(result['reflectance'])}")
                if len(meas_wl) != len(result['reflectance']):
                    print("警告: x和y维度不匹配! 需要修复plot函数")
            except Exception as e:
                print(f"绘图过程出错: {str(e)}")
        else:
            print("测量处理失败，未返回结果")
    except Exception as e:
        print(f"处理测量数据时出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dimensions() 