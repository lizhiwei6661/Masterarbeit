import numpy as np
import os
from color_calculator import ColorCalculator

def main():
    """
    测试不同光源对XYZ计算的影响
    """
    print("测试不同光源对XYZ计算的影响...")
    
    # 创建ColorCalculator实例
    calculator = ColorCalculator()
    
    # 设置rho_lambda值为0.989，与MATLAB一致
    calculator.set_rho_lambda(0.989)
    
    # 创建一个简单的反射率数据进行测试
    # 使用均匀反射率0.5的测试样本
    wavelengths = np.arange(380, 781, 1)
    reflectance = np.ones_like(wavelengths) * 0.5
    
    print("\n测试不同光源下的XYZ计算:")
    print("=" * 50)
    print(f"{'光源':<10} | {'X值':<12} | {'Y值':<12} | {'Z值':<12} | {'x值':<12} | {'y值':<12}")
    print("-" * 50)
    
    # 测试所有光源
    for illuminant in ['D65', 'D50', 'A', 'E']:
        # 设置光源
        calculator.set_illuminant(illuminant)
        
        # 计算XYZ值
        xyz = calculator.calculate_xyz(reflectance, wavelengths)
        
        # 计算xy色度坐标
        xy = calculator.xyz_to_xy(xyz)
        
        # 打印结果
        print(f"{illuminant:<10} | {xyz[0]:<12.6f} | {xyz[1]:<12.6f} | {xyz[2]:<12.6f} | {xy[0]:<12.6f} | {xy[1]:<12.6f}")
    
    print("=" * 50)
    print("\n结论:")
    print("1. 不同光源会产生不同的XYZ值和xy色度坐标")
    print("2. 使用D65光源是CIE标准的默认设置")
    print("3. 均匀光源E在所有波长上功率相等")
    print("4. A光源模拟白炽灯光谱")
    print("5. D50光源模拟中午日光")
    
    print("\n测试完成!")

if __name__ == "__main__":
    main() 