"""
直接测试给定线性RGB值的Gamma校正
"""
import numpy as np
from color_calculator import ColorCalculator

def main():
    # 初始化颜色计算器
    calculator = ColorCalculator()
    
    # 直接设置线性RGB值
    rgb_linear = np.array([1.1356, 0.38769, 0.0])
    
    print(f"输入线性RGB值: {rgb_linear}")
    
    # 使用我们的方法计算Gamma校正
    rgb_gamma = calculator.linear_to_gamma_rgb(rgb_linear)
    print(f"Python实现计算的Gamma RGB值: {rgb_gamma}")
    
    # 手动计算Gamma校正
    gamma_corrected = []
    for val in rgb_linear:
        if val <= 0.0031308:
            gamma = 12.92 * val
            if val < 0:
                gamma = 0
        else:
            gamma = 1.055 * (val ** (1/2.4)) - 0.055
        gamma_corrected.append(gamma)
    
    print(f"手动计算的Gamma RGB值: {gamma_corrected}")
    
    # 计算差异
    diff = rgb_gamma - np.array(gamma_corrected)
    print(f"差异: {diff}")
    
    # 计算预期的表格输出格式
    rgb_gamma_str = f"({rgb_gamma[0]:.4f}, {rgb_gamma[1]:.4f}, {rgb_gamma[2]:.4f})"
    print(f"表格中显示的值应该是: {rgb_gamma_str}")
    
    # 直接创建模拟显示样式
    display_gamma = np.clip(rgb_gamma, 0, 1)
    display_str = f"({display_gamma[0]:.4f}, {display_gamma[1]:.4f}, {display_gamma[2]:.4f})"
    print(f"如果裁剪到[0,1]范围，显示的值将是: {display_str}")

if __name__ == "__main__":
    main() 