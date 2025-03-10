import numpy as np
import os
import matplotlib.pyplot as plt
from color_calculator import ColorCalculator

def main():
    """测试波长匹配函数"""
    print("=" * 50)
    print("测试波长匹配函数")
    print("=" * 50)
    
    # 创建ColorCalculator实例
    calculator = ColorCalculator()
    
    # 获取CIE数据波长（通常是5nm步长）
    cie_wavelengths = calculator.cie_1931['wavelengths']
    print(f"CIE波长: {len(cie_wavelengths)}点, 范围: {cie_wavelengths[0]}-{cie_wavelengths[-1]}nm")
    print(f"CIE波长步长: {cie_wavelengths[1] - cie_wavelengths[0]}nm")
    
    # 创建1nm步长的测试数据
    test_wavelengths = np.arange(380, 781, 1)  # 380-780nm, 1nm步长
    test_data = np.ones_like(test_wavelengths)  # 全部值为1的测试数据
    
    print(f"测试数据: {len(test_wavelengths)}点, 范围: {test_wavelengths[0]}-{test_wavelengths[-1]}nm")
    print(f"测试数据步长: {test_wavelengths[1] - test_wavelengths[0]}nm")
    
    # 测试波长匹配函数
    print("\n测试1: 将1nm步长数据匹配到5nm步长")
    matched_data = calculator.match_wavelength_matlab_style(cie_wavelengths, test_data, test_wavelengths)
    print(f"匹配结果: {len(matched_data)}点")
    
    # 验证结果长度是否与目标波长长度一致
    if len(matched_data) == len(cie_wavelengths):
        print("✓ 匹配成功: 长度一致")
    else:
        print(f"✗ 匹配失败: 长度不一致，预期{len(cie_wavelengths)}，实际{len(matched_data)}")
    
    # 测试反向匹配
    print("\n测试2: 将5nm步长数据匹配到1nm步长")
    test_data_5nm = np.ones_like(cie_wavelengths)
    matched_data_rev = calculator.match_wavelength_matlab_style(test_wavelengths, test_data_5nm, cie_wavelengths)
    print(f"匹配结果: {len(matched_data_rev)}点")
    
    # 验证结果长度是否与目标波长长度一致
    if len(matched_data_rev) == len(test_wavelengths):
        print("✓ 匹配成功: 长度一致")
    else:
        print(f"✗ 匹配失败: 长度不一致，预期{len(test_wavelengths)}，实际{len(matched_data_rev)}")
    
    # 创建更复杂的测试数据
    complex_data = np.sin(np.linspace(0, 2*np.pi, len(test_wavelengths)))  # 正弦波形
    
    # 测试匹配复杂数据
    print("\n测试3: 匹配复杂数据（正弦波）从1nm到5nm")
    matched_complex = calculator.match_wavelength_matlab_style(cie_wavelengths, complex_data, test_wavelengths)
    
    # 绘制匹配结果
    plt.figure(figsize=(12, 6))
    
    # 绘制原始1nm数据（仅显示每5个点以便比较）
    indices_5nm = np.arange(0, len(test_wavelengths), 5)
    plt.plot(test_wavelengths[indices_5nm], complex_data[indices_5nm], 'o', label='原始数据（1nm步长，每5点采样）')
    
    # 绘制匹配后的5nm数据
    plt.plot(cie_wavelengths, matched_complex, 'x-', label='匹配后数据（5nm步长）')
    
    plt.title('波长匹配测试')
    plt.xlabel('波长 (nm)')
    plt.ylabel('值')
    plt.legend()
    plt.grid(True)
    
    # 保存图表
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, "wavelength_matching_test.png"))
    plt.close()
    
    print("\n波长匹配测试完成")

if __name__ == "__main__":
    main() 