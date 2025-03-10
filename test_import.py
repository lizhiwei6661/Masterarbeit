#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导入功能的简单程序
"""

import os
import sys
import numpy as np
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

def main():
    """主函数"""
    print("\n===== 测试导入功能 =====")
    
    # 1. 加载测试数据
    black_file = os.path.join(MATLAB_DATA_DIR, "black.csv")
    white_file = os.path.join(MATLAB_DATA_DIR, "white.csv")
    test_files = [
        os.path.join(MATLAB_DATA_DIR, "tu-berlin00004.csv"),
        # 添加更多测试文件...
    ]
    
    if not os.path.isfile(black_file) or not os.path.isfile(white_file):
        print("无法找到黑白参考文件")
        return
    
    black_wl, black_val = load_csv_data(black_file)
    white_wl, white_val = load_csv_data(white_file)
    
    if black_wl is None or white_wl is None:
        print("无法加载黑白参考数据")
        return
    
    # 2. 创建计算器并设置校准模式
    calculator = ColorCalculator()
    calculator.set_calibration_mode(True, black_val, white_val)
    
    # 3. 处理每个测试文件
    for test_file in test_files:
        if not os.path.isfile(test_file):
            print(f"无法找到测试文件: {test_file}")
            continue
        
        print(f"\n处理文件: {os.path.basename(test_file)}")
        
        # 加载测量数据
        meas_wl, meas_val = load_csv_data(test_file)
        if meas_wl is None:
            print("无法加载测量数据")
            continue
        
        # 处理测量数据
        try:
            result = calculator.process_measurement(meas_val, meas_wl)
            
            if result:
                print("\n计算结果:")
                print(f"XYZ: ({result['xyz'][0]:.6f}, {result['xyz'][1]:.6f}, {result['xyz'][2]:.6f})")
                print(f"xy: ({result['xy'][0]:.6f}, {result['xy'][1]:.6f})")
                print(f"RGB: ({result['rgb_gamma'][0]:.6f}, {result['rgb_gamma'][1]:.6f}, {result['rgb_gamma'][2]:.6f})")
                print(f"颜色: {result['hex_color']}")
                
                # 创建输出目录
                output_dir = "test_output"
                os.makedirs(output_dir, exist_ok=True)
                
                # 保存反射率图
                base_name = os.path.splitext(os.path.basename(test_file))[0]
                plt.figure(figsize=(10, 6))
                plt.plot(meas_wl, result['reflectance'])
                plt.xlabel('波长 (nm)')
                plt.ylabel('反射率')
                plt.title(f'反射率曲线 - {base_name}')
                plt.grid(True)
                plt.savefig(os.path.join(output_dir, f"{base_name}_reflectance.png"))
                plt.close()
                
                # 保存颜色示例
                plt.figure(figsize=(3, 3))
                plt.axes([0, 0, 1, 1], frameon=False)
                plt.fill([0, 1, 1, 0], [0, 0, 1, 1], color=result['rgb_gamma'])
                plt.axis('off')
                plt.savefig(os.path.join(output_dir, f"{base_name}_color.png"))
                plt.close()
                
                print(f"图像已保存到 {output_dir} 目录")
            else:
                print("处理失败，未返回结果")
        except Exception as e:
            print(f"处理文件出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n测试完成")

if __name__ == "__main__":
    main() 