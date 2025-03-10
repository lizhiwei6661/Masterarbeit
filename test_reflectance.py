import numpy as np
import matplotlib.pyplot as plt
from color_calculator import ColorCalculator

def test_reflectance_calculation():
    # 创建计算器对象
    calculator = ColorCalculator()
    
    # 创建波长数据（1nm步长）
    wavelengths = np.arange(380, 781, 1)
    print(f'波长范围: {wavelengths[0]}-{wavelengths[-1]} nm, 步长: {wavelengths[1]-wavelengths[0]} nm')
    
    # 创建测试数据：在598-629 nm区间（索引218-250）设置为0.5，其他为1.0
    values = np.ones_like(wavelengths)
    values[218:250] = 0.5
    print(f'创建测试数据: 区间{wavelengths[218]}-{wavelengths[249]} nm设置为0.5，其他为1.0')
    
    # 创建测试的黑白参考
    black_ref = np.ones_like(wavelengths) * 0.1
    white_ref = np.ones_like(wavelengths) * 0.8
    
    # 设置校准模式
    calculator.set_calibration_mode(True, black_ref, white_ref)
    print(f'使用黑参考值: {black_ref[0]}，白参考值: {white_ref[0]}')
    
    # 计算反射率
    print("\n===== 计算反射率 =====")
    reflectance = calculator.calculate_reflectance(values, wavelengths)
    
    # 检查特定区域的反射率值
    print("\n===== 反射率结果 =====")
    # 检查索引218-250区域的反射率（应该不同于其他区域）
    print(f'反射率值在{wavelengths[218]}-{wavelengths[249]} nm范围（区域1）:')
    print(reflectance[218:250][:10])
    
    # 检查前面的区域
    print(f'\n反射率值在{wavelengths[208]}-{wavelengths[217]} nm范围（区域1之前）:')
    print(reflectance[208:218])
    
    # 检查后面的区域
    print(f'\n反射率值在{wavelengths[250]}-{wavelengths[259]} nm范围（区域1之后）:')
    print(reflectance[250:260])
    
    # 根据MATLAB公式手动计算预期值
    print("\n===== 使用MATLAB公式手动计算预期值 =====")
    # MATLAB公式: (measurement - black) / (white - black) * white / measurement * rho_lambda
    # 对于区域1（值为0.5的区域）
    expected1 = (0.5 - 0.1) / (0.8 - 0.1) * 0.8 / 0.5 * 1.0
    # 对于其他区域（值为1.0的区域）
    expected2 = (1.0 - 0.1) / (0.8 - 0.1) * 0.8 / 1.0 * 1.0
    
    print(f'区域1（值为0.5）的预期反射率: {expected1}')
    print(f'其他区域（值为1.0）的预期反射率: {expected2}')
    
    # 验证计算是否正确
    if np.allclose(reflectance[218:250], expected1) and np.allclose(reflectance[0:218], expected2) and np.allclose(reflectance[250:], expected2):
        print("\n计算结果正确！")
    else:
        print("\n计算结果与预期不符！")
        
    # 绘制反射率曲线
    plt.figure(figsize=(12, 6))
    plt.plot(wavelengths, reflectance)
    plt.xlabel('波长 (nm)')
    plt.ylabel('反射率')
    plt.title('反射率计算测试')
    plt.grid(True)
    plt.axvspan(wavelengths[218], wavelengths[249], color='yellow', alpha=0.3, label='测试区域（0.5值）')
    plt.legend()
    plt.savefig('reflectance_test.png')
    print("\n已保存反射率曲线图到 reflectance_test.png")
    
    # 分析MATLAB的计算公式各个部分
    print("\n===== MATLAB公式各部分分析 =====")
    # 提取测试值1和值2
    test_value1 = 0.5  # 区域1的值
    test_value2 = 1.0  # 其他区域的值
    
    # MATLAB公式各部分
    part1_1 = (test_value1 - black_ref[0]) / (white_ref[0] - black_ref[0])
    part1_2 = (test_value2 - black_ref[0]) / (white_ref[0] - black_ref[0])
    
    part2_1 = white_ref[0] / test_value1
    part2_2 = white_ref[0] / test_value2
    
    print(f"区域1 (value=0.5): (data-black)/(white-black) = {part1_1}")
    print(f"区域1 (value=0.5): white/data = {part2_1}")
    print(f"区域1 (value=0.5): 完整公式 = {part1_1 * part2_1}")
    
    print(f"其他区域 (value=1.0): (data-black)/(white-black) = {part1_2}")
    print(f"其他区域 (value=1.0): white/data = {part2_2}")
    print(f"其他区域 (value=1.0): 完整公式 = {part1_2 * part2_2}")

if __name__ == "__main__":
    test_reflectance_calculation() 