"""
测试超出范围值的处理
"""
import numpy as np
from color_calculator import ColorCalculator

def main():
    # 初始化颜色计算器
    calculator = ColorCalculator()
    
    # 测试数据
    rgb_linear = np.array([1.1356, 0.38769, 0.0])
    
    print("===== 测试超出范围值处理 =====")
    print(f"线性RGB值: {rgb_linear}")
    
    # 计算Gamma校正
    rgb_gamma = calculator.linear_to_gamma_rgb(rgb_linear)
    print(f"Gamma校正RGB值: {rgb_gamma}")
    
    # 生成Hex颜色
    # 注意：直接使用原始rgb_gamma生成hex颜色，会在内部被裁剪
    hex_color = calculator.rgb_to_hex(rgb_gamma)
    print(f"Hex颜色值: {hex_color}")
    
    # 模拟表格显示格式化
    rgb_linear_str = f"({rgb_linear[0]:.4f}, {rgb_linear[1]:.4f}, {rgb_linear[2]:.4f})"
    rgb_gamma_str = f"({rgb_gamma[0]:.4f}, {rgb_gamma[1]:.4f}, {rgb_gamma[2]:.4f})"
    
    print(f"\n模拟表格显示:")
    print(f"线性RGB显示: {rgb_linear_str}")
    print(f"Gamma RGB显示: {rgb_gamma_str}")
    
    # 手动创建用于显示的颜色值
    display_gamma = np.clip(rgb_gamma, 0, 1)
    display_hex = '#{:02X}{:02X}{:02X}'.format(
        int(display_gamma[0] * 255),
        int(display_gamma[1] * 255),
        int(display_gamma[2] * 255)
    )
    
    print(f"\n用于UI显示的裁剪值:")
    print(f"裁剪的Gamma RGB: {display_gamma}")
    print(f"对应的Hex颜色: {display_hex}")
    
    print("\n总结:")
    print("1. 线性RGB值 [1.1356, 0.38769, 0.0] 被正确转换为")
    print("2. Gamma校正值 [1.0574, 0.6559, 0.0000]，超出范围值不被裁剪")
    print("3. 但为了UI显示目的，需要临时裁剪到[0,1]范围，这就是您看到1.0000而不是1.0574的原因")

if __name__ == "__main__":
    main() 