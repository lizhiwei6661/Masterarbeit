"""
测试特定线性RGB值的gamma校正
"""
import numpy as np
from color_calculator import ColorCalculator

def test_matlab_gamma(rgb_linear):
    """
    使用MATLAB的逻辑实现gamma校正
    """
    sRGBGamma = np.copy(rgb_linear)
    
    for n in range(len(rgb_linear)):
        if rgb_linear[n] <= 0.0031308:
            sRGBGamma[n] = rgb_linear[n] * 12.92
            if rgb_linear[n] < 0:
                sRGBGamma[n] = 0
        else:
            sRGBGamma[n] = 1.055 * (rgb_linear[n] ** (1/2.4)) - 0.055
    
    return sRGBGamma

def main():
    # 初始化颜色计算器
    calculator = ColorCalculator()
    
    # 用户提到的线性RGB值
    rgb_linear = np.array([1.1356, 0.38769, 0])
    
    print(f"测试线性RGB值: {rgb_linear}")
    print("-" * 80)
    
    # 使用我们修改后的Python实现
    rgb_gamma_python = calculator.linear_to_gamma_rgb(rgb_linear)
    print(f"Python实现的Gamma RGB: {rgb_gamma_python}")
    
    # 使用直接复制的MATLAB逻辑
    rgb_gamma_matlab = test_matlab_gamma(rgb_linear)
    print(f"MATLAB逻辑的Gamma RGB: {rgb_gamma_matlab}")
    
    # 比较结果
    diff = rgb_gamma_python - rgb_gamma_matlab
    print(f"差异: {diff}")
    
    # 手动计算每个值的gamma校正结果，以验证
    print("\n手动计算验证:")
    print("-" * 80)
    
    # 第一个值: 1.1356
    v1 = 1.1356
    g1 = 1.055 * (v1 ** (1/2.4)) - 0.055
    print(f"1.1356 -> {g1}")
    
    # 第二个值: 0.38769
    v2 = 0.38769
    g2 = 1.055 * (v2 ** (1/2.4)) - 0.055
    print(f"0.38769 -> {g2}")
    
    # 第三个值: 0
    v3 = 0
    g3 = 12.92 * v3
    print(f"0 -> {g3}")
    
    # 综合结果
    expected = np.array([g1, g2, g3])
    print(f"\n期望的Gamma RGB: {expected}")
    
    print("\n你可能需要手动将这些值与MATLAB结果进行比较")
    print("如果python中的gamma校正计算与期望值不匹配，我们可能需要调整实现")

if __name__ == "__main__":
    main() 