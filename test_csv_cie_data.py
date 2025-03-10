import numpy as np
import os
from color_calculator import ColorCalculator

def main():
    """
    测试从CSV文件加载的CIE数据
    """
    print("测试从xyzBar.csv加载CIE数据...")
    
    # 创建ColorCalculator实例
    calculator = ColorCalculator()
    
    # 打印CIE数据信息
    cie_data = calculator.cie_1931
    
    print(f"\nCIE数据摘要:")
    print(f"数据点数: {len(cie_data['wavelengths'])}")
    print(f"波长范围: {cie_data['wavelengths'][0]}-{cie_data['wavelengths'][-1]}nm")
    print(f"波长步长: {cie_data['wavelengths'][1] - cie_data['wavelengths'][0]}nm")
    
    print(f"\nx值范围: {np.min(cie_data['x']):.6f}-{np.max(cie_data['x']):.6f}")
    print(f"y值范围: {np.min(cie_data['y']):.6f}-{np.max(cie_data['y']):.6f}")
    print(f"z值范围: {np.min(cie_data['z']):.6f}-{np.max(cie_data['z']):.6f}")
    
    # 打印一些特定波长的值
    sample_wavelengths = [380, 400, 500, 600, 700, 780]
    print("\n特定波长的CIE值:")
    for wl in sample_wavelengths:
        # 找到最接近的波长索引
        idx = np.argmin(np.abs(cie_data['wavelengths'] - wl))
        actual_wl = cie_data['wavelengths'][idx]
        print(f"波长: {actual_wl}nm, x: {cie_data['x'][idx]:.6f}, y: {cie_data['y'][idx]:.6f}, z: {cie_data['z'][idx]:.6f}")
    
    # 测试计算XYZ值
    print("\n测试XYZ计算:")
    # 创建一个均匀反射率为0.5的测试数据
    wavelengths = np.arange(380, 781, 1)  # 1nm步长
    reflectance = np.ones_like(wavelengths) * 0.5  # 反射率均为0.5
    
    # 设置rho_lambda值为0.989，与MATLAB一致
    calculator.set_rho_lambda(0.989)
    
    # 计算XYZ值
    xyz = calculator.calculate_xyz(reflectance, wavelengths)
    print(f"XYZ值: X={xyz[0]:.6f}, Y={xyz[1]:.6f}, Z={xyz[2]:.6f}")
    
    # 计算xy色度坐标
    xy = calculator.xyz_to_xy(xyz)
    print(f"xy色度坐标: x={xy[0]:.6f}, y={xy[1]:.6f}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    main() 