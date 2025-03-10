import numpy as np
import matplotlib.pyplot as plt
from color_calculator import ColorCalculator

def debug_reflectance_calculation():
    # 创建计算器对象
    calculator = ColorCalculator()
    
    # 创建波长数据（1nm步长）
    wavelengths = np.arange(380, 781, 1)
    print(f'波长范围: {wavelengths[0]}-{wavelengths[-1]} nm, 步长: {wavelengths[1]-wavelengths[0]} nm')
    
    # 创建更接近实际的测试数据
    # 创建测试样本：在598-629 nm区间（索引218-250）设置为0.5，其他为0.7
    values = np.ones_like(wavelengths) * 0.7
    values[218:250] = 0.5
    print(f'创建测试数据: 区间{wavelengths[218]}-{wavelengths[249]} nm设置为0.5，其他为0.7')
    
    # 创建更接近实际的黑白参考
    black_ref = np.ones_like(wavelengths) * 0.2
    white_ref = np.ones_like(wavelengths) * 0.9
    
    # 设置校准模式
    calculator.set_calibration_mode(True, black_ref, white_ref)
    print(f'使用黑参考值: {black_ref[0]}，白参考值: {white_ref[0]}')
    
    # 手动一步步计算反射率，打印中间结果
    print("\n===== 手动计算反射率 =====")
    
    # 取出特定波长点进行计算
    idx1 = 220  # 在区域1中（value=0.5）
    idx2 = 300  # 在其他区域（value=0.7）
    
    measurement1 = values[idx1]
    measurement2 = values[idx2]
    black1 = black_ref[idx1]
    black2 = black_ref[idx2]
    white1 = white_ref[idx1]
    white2 = white_ref[idx2]
    
    # 打印输入数据
    print(f"区域1 (λ={wavelengths[idx1]} nm): 测量值={measurement1}, 黑参考={black1}, 白参考={white1}")
    print(f"区域2 (λ={wavelengths[idx2]} nm): 测量值={measurement2}, 黑参考={black2}, 白参考={white2}")
    
    # 计算(data-black)/(white-black)部分
    part1_1 = (measurement1 - black1) / (white1 - black1)
    part1_2 = (measurement2 - black2) / (white2 - black2)
    
    print(f"区域1: (data-black)/(white-black) = ({measurement1}-{black1})/({white1}-{black1}) = {part1_1}")
    print(f"区域2: (data-black)/(white-black) = ({measurement2}-{black2})/({white2}-{black2}) = {part1_2}")
    
    # 计算white/data部分
    part2_1 = white1 / measurement1
    part2_2 = white2 / measurement2
    
    print(f"区域1: white/data = {white1}/{measurement1} = {part2_1}")
    print(f"区域2: white/data = {white2}/{measurement2} = {part2_2}")
    
    # 完整公式
    rho_lambda = 1.0  # 假设rho_lambda=1.0
    reflectance1 = part1_1 * part2_1 * rho_lambda
    reflectance2 = part1_2 * part2_2 * rho_lambda
    
    print(f"区域1: 完整公式 = {part1_1} * {part2_1} * {rho_lambda} = {reflectance1}")
    print(f"区域2: 完整公式 = {part1_2} * {part2_2} * {rho_lambda} = {reflectance2}")
    
    # 使用Python的实现计算反射率
    print("\n===== 使用ColorCalculator计算反射率 =====")
    reflectance = calculator.calculate_reflectance(values, wavelengths)
    
    # 检查计算结果
    print(f"区域1实际计算得到的反射率: {reflectance[idx1]}")
    print(f"区域2实际计算得到的反射率: {reflectance[idx2]}")
    
    # 检查区域1的反射率是否为负
    if reflectance1 < 0:
        print(f"警告: 区域1的预期反射率为负值 ({reflectance1})，这与观察到的结果一致，它会被设置为0")
    
    # 检查区域2的反射率是否超过1
    if reflectance2 > 1:
        print(f"警告: 区域2的预期反射率超过1 ({reflectance2})，这与观察到的结果一致，它会被裁剪为1")
    
    # 寻找计算中的可能错误
    print("\n===== 检查MATLAB公式和实现 =====")
    # MATLAB公式: (data - black)./(white-black).*white./data*rho_Nlambda
    
    # 检查part1计算
    python_part1_1 = (measurement1 - black1) / (white1 - black1)
    matlab_part1_1 = (measurement1 - black1) / (white1 - black1)
    print(f"Part1 (区域1): Python={python_part1_1}, MATLAB={matlab_part1_1}, 是否一致: {np.isclose(python_part1_1, matlab_part1_1)}")
    
    # 检查part2计算
    python_part2_1 = white1 / measurement1
    matlab_part2_1 = white1 / measurement1
    print(f"Part2 (区域1): Python={python_part2_1}, MATLAB={matlab_part2_1}, 是否一致: {np.isclose(python_part2_1, matlab_part2_1)}")
    
    # 检查完整公式计算
    python_full_1 = python_part1_1 * python_part2_1 * rho_lambda
    matlab_full_1 = matlab_part1_1 * matlab_part2_1 * rho_lambda
    print(f"完整公式 (区域1): Python={python_full_1}, MATLAB={matlab_full_1}, 是否一致: {np.isclose(python_full_1, matlab_full_1)}")
    
    # 检查是否有可能是公式理解错误
    # MATLAB中这个公式是 (data - black)./(white-black).*white./data*rho_Nlambda
    # 但有可能是 ((data - black)./(white-black)).*white./data*rho_Nlambda
    # 或者是 (data - black)./((white-black).*white)./data*rho_Nlambda
    # 或者是 (data - black)./(white-black).*(white./data)*rho_Nlambda
    
    alternate_formula1 = (measurement1 - black1) / (white1 - black1) * (white1 / measurement1) * rho_lambda
    alternate_formula2 = (measurement1 - black1) / ((white1 - black1) * white1) / measurement1 * rho_lambda
    alternate_formula3 = (measurement1 - black1) / (white1 - black1) * white1 / measurement1 * rho_lambda
    
    print(f"\n可能的公式1: (data-black)/(white-black)*(white/data)*rho_lambda = {alternate_formula1}")
    print(f"可能的公式2: (data-black)/((white-black)*white)/data*rho_lambda = {alternate_formula2}")
    print(f"可能的公式3: (data-black)/(white-black)*white/data*rho_lambda = {alternate_formula3} (当前使用)")
    
    # 检查是否需要调整公式
    if alternate_formula1 < 0 or alternate_formula2 < 0 or alternate_formula3 < 0:
        print("警告: 使用当前测试数据，至少有一个公式产生负反射率")
    else:
        print("注意: 使用当前测试数据，所有公式都产生正反射率值")
    
    # 检查MATLAB公式的推导
    print("\n===== MATLAB公式的物理含义 =====")
    print("公式: (data - black)./(white-black).*white./data*rho_Nlambda")
    print("1. (data - black) = 去除背景噪声后的信号")
    print("2. (white - black) = 背景噪声校正后的参考白色信号")
    print("3. (data - black)/(white - black) = 相对于参考白的比例")
    print("4. white/data = 白色参考与测量数据的比值")
    print("   这一项在物理上有些奇怪，因为通常reflectance = measurement/white")
    print("   但这个公式使用了white/data，可能在某些情况下导致负值或极大值")
    
    # 绘制手动计算的反射率曲线
    print("\n===== 生成手动计算的反射率曲线 =====")
    manual_reflectance = np.zeros_like(wavelengths, dtype=float)
    
    # 对每个波长点手动计算反射率
    for i in range(len(wavelengths)):
        m = values[i]
        b = black_ref[i]
        w = white_ref[i]
        
        # 使用当前公式计算
        factor1 = (m - b) / (w - b)
        factor2 = w / m
        manual_reflectance[i] = factor1 * factor2 * rho_lambda
    
    # 检查负值和超出1的值
    negative_count = np.sum(manual_reflectance < 0)
    over_one_count = np.sum(manual_reflectance > 1)
    
    print(f"手动计算得到 {negative_count} 个负反射率值和 {over_one_count} 个超过1的反射率值")
    
    # 绘制原始反射率曲线（未裁剪负值和超过1的值）
    plt.figure(figsize=(12, 8))
    plt.subplot(2, 1, 1)
    plt.plot(wavelengths, manual_reflectance)
    plt.xlabel('波长 (nm)')
    plt.ylabel('未裁剪的反射率')
    plt.title('手动计算的反射率（未裁剪负值和超过1的值）')
    plt.grid(True)
    plt.axvspan(wavelengths[218], wavelengths[249], color='yellow', alpha=0.3, label='测试区域')
    plt.axhline(y=0, color='r', linestyle='--')
    plt.axhline(y=1, color='g', linestyle='--')
    plt.legend()
    
    # 裁剪后的反射率（负值设为0，超过1的值设为1）
    clipped_reflectance = np.clip(manual_reflectance, 0, 1)
    
    # 绘制裁剪后的反射率曲线
    plt.subplot(2, 1, 2)
    plt.plot(wavelengths, clipped_reflectance)
    plt.xlabel('波长 (nm)')
    plt.ylabel('裁剪后的反射率')
    plt.title('手动计算的反射率（裁剪负值和超过1的值）')
    plt.grid(True)
    plt.axvspan(wavelengths[218], wavelengths[249], color='yellow', alpha=0.3, label='测试区域')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('reflectance_debug.png')
    print("已保存手动计算的反射率曲线图到 reflectance_debug.png")
    
    # 最终结论
    print("\n===== 结论 =====")
    if negative_count > 0 and wavelengths[218] <= 598 <= wavelengths[249]:
        print("1. 测试区域（598-629 nm）中有负反射率值，这些值在计算过程中会被设置为0")
        print("2. 这解释了为什么这个区域的反射率在最终结果中全部为0")
    
    if over_one_count > 0:
        print("3. 其他区域的反射率超过1.0，这些值在计算过程中会被裁剪为1.0")
        print("4. 这解释了为什么其他区域的反射率在最终结果中全部为1.0")
    
    print("\n5. MATLAB公式 (data-black)/(white-black)*white/data*rho_lambda 在某些情况下可能产生负值")
    print("6. 这与观察到的现象一致，在598-629 nm范围的值全部被设置为0")
    
    # 提出可能的解决方案
    print("\n===== 可能的解决方案 =====")
    print("1. 检查MATLAB的代码是否确实使用了这个公式，以及是否有额外的处理步骤")
    print("2. 考虑修改公式或添加额外的约束条件，避免负反射率值")
    print("3. 检查测量数据和校准数据是否正确，可能有异常值导致计算错误")

if __name__ == "__main__":
    debug_reflectance_calculation() 