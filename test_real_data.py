import numpy as np
import matplotlib.pyplot as plt
from color_calculator import ColorCalculator

def test_with_real_data():
    # 创建计算器对象
    calculator = ColorCalculator()
    
    # 创建波长数据（1nm步长）
    wavelengths = np.arange(380, 781, 1)
    print(f'波长范围: {wavelengths[0]}-{wavelengths[-1]} nm, 步长: {wavelengths[1]-wavelengths[0]} nm')
    
    # 创建模拟的测量数据 - 使用接近实际情况的值
    # 基础值大约在0.002-0.05之间，600nm附近的值稍低
    values = np.random.uniform(0.02, 0.05, len(wavelengths))
    
    # 在波长598-629 nm区间（索引218-250）设置较低的值，模拟实际情况
    values[218:250] = np.random.uniform(0.002, 0.005, 250-218)
    print(f'创建模拟测量数据: 普通区域范围≈0.02-0.05, 区间{wavelengths[218]}-{wavelengths[249]} nm范围≈0.002-0.005')
    
    # 创建真实情况下的黑白参考
    # 黑参考通常有一些噪声，在0.001-0.01之间
    black_ref = np.random.uniform(0.001, 0.01, len(wavelengths))
    
    # 白参考通常比测量值高，在0.03-0.07之间
    white_ref = np.random.uniform(0.03, 0.07, len(wavelengths))
    
    print(f'黑参考范围: {np.min(black_ref):.6f}-{np.max(black_ref):.6f}')
    print(f'白参考范围: {np.min(white_ref):.6f}-{np.max(white_ref):.6f}')
    print(f'测量数据范围: {np.min(values):.6f}-{np.max(values):.6f}')
    
    # 检查特定波长范围的值
    critical_region = values[218:250]
    normal_region = np.concatenate([values[:218], values[250:]])
    black_critical = black_ref[218:250]
    white_critical = white_ref[218:250]
    
    print(f'\n临界区域({wavelengths[218]}-{wavelengths[249]} nm)统计:')
    print(f'  测量值: 最小={np.min(critical_region):.6f}, 最大={np.max(critical_region):.6f}, 平均={np.mean(critical_region):.6f}')
    print(f'  黑参考: 最小={np.min(black_critical):.6f}, 最大={np.max(black_critical):.6f}, 平均={np.mean(black_critical):.6f}')
    print(f'  白参考: 最小={np.min(white_critical):.6f}, 最大={np.max(white_critical):.6f}, 平均={np.mean(white_critical):.6f}')
    
    print(f'\n正常区域统计:')
    print(f'  测量值: 最小={np.min(normal_region):.6f}, 最大={np.max(normal_region):.6f}, 平均={np.mean(normal_region):.6f}')

    # 设置校准模式
    calculator.set_calibration_mode(True, black_ref, white_ref)
    
    # 计算反射率
    print("\n===== 计算反射率 =====")
    reflectance = calculator.calculate_reflectance(values, wavelengths)
    
    # 分析反射率结果
    reflectance_critical = reflectance[218:250]
    reflectance_normal = np.concatenate([reflectance[:218], reflectance[250:]])
    
    print(f'\n计算后反射率统计:')
    print(f'  临界区域: 最小={np.min(reflectance_critical):.6f}, 最大={np.max(reflectance_critical):.6f}, '
          f'平均={np.mean(reflectance_critical):.6f}, 为0的点数={np.sum(reflectance_critical == 0)}')
    print(f'  正常区域: 最小={np.min(reflectance_normal):.6f}, 最大={np.max(reflectance_normal):.6f}, '
          f'平均={np.mean(reflectance_normal):.6f}, 为1的点数={np.sum(reflectance_normal == 1)}')
    
    # 手动计算一个临界点的反射率
    critical_idx = 220
    m = values[critical_idx]
    b = black_ref[critical_idx]
    w = white_ref[critical_idx]
    
    # MATLAB公式
    manual_reflectance = (m - b) / (w - b) * w / m * 1.0
    
    print(f'\n手动计算波长{wavelengths[critical_idx]} nm的反射率:')
    print(f'  测量值={m:.6f}, 黑参考={b:.6f}, 白参考={w:.6f}')
    print(f'  (m-b)/(w-b) = {(m-b)/(w-b):.6f}')
    print(f'  w/m = {w/m:.6f}')
    print(f'  (m-b)/(w-b)*w/m = {manual_reflectance:.6f}')
    print(f'  实际计算值 = {reflectance[critical_idx]:.6f}')
    
    if manual_reflectance < 0:
        print(f'  警告: 手动计算得到负反射率，这将被设置为0')
    elif manual_reflectance > 1:
        print(f'  警告: 手动计算得到大于1的反射率，这将被裁剪为1')
    
    # 分析可能的负反射率情况
    print("\n===== 分析负反射率出现的条件 =====")
    # 反射率公式: (m-b)/(w-b) * w/m
    # 当 (m-b)/(w-b) < 0 时，反射率为负
    # 这发生在 m<b (测量值小于黑参考) 或 w<b (白参考小于黑参考) 时
    # 当 w/m 非常大 (m很小) 时，可能导致反射率很大
    
    # 检查所有点是否有测量值小于黑参考的情况
    m_less_than_b = values < black_ref
    count_m_less_than_b = np.sum(m_less_than_b)
    if count_m_less_than_b > 0:
        print(f'发现 {count_m_less_than_b} 个测量值小于黑参考的点，这可能导致负反射率')
        problematic_indices = np.where(m_less_than_b)[0]
        for idx in problematic_indices[:5]:  # 只显示前5个
            print(f'  波长 {wavelengths[idx]} nm: 测量值={values[idx]:.6f}, 黑参考={black_ref[idx]:.6f}')
    else:
        print('未发现测量值小于黑参考的点')
    
    # 检查临界区域的情况
    critical_m_less_than_b = critical_region < black_critical
    count_critical_m_less_than_b = np.sum(critical_m_less_than_b)
    if count_critical_m_less_than_b > 0:
        print(f'临界区域中有 {count_critical_m_less_than_b} 个测量值小于黑参考的点')
    
    # 检查 white-black 接近0的情况（分母接近0）
    w_minus_b_small = np.abs(white_ref - black_ref) < 0.005
    count_w_minus_b_small = np.sum(w_minus_b_small)
    if count_w_minus_b_small > 0:
        print(f'发现 {count_w_minus_b_small} 个白参考与黑参考差值很小的点，这可能导致计算不稳定')
    
    # 绘制测量数据、黑白参考和计算的反射率
    plt.figure(figsize=(15, 10))
    
    # 绘制测量数据和黑白参考
    plt.subplot(2, 1, 1)
    plt.plot(wavelengths, values, 'b-', label='测量数据')
    plt.plot(wavelengths, black_ref, 'k--', label='黑参考')
    plt.plot(wavelengths, white_ref, 'r--', label='白参考')
    plt.xlabel('波长 (nm)')
    plt.ylabel('光谱辐照度')
    plt.title('测量数据和参考数据')
    plt.grid(True)
    plt.axvspan(wavelengths[218], wavelengths[249], color='yellow', alpha=0.3, label='临界区域')
    plt.legend()
    
    # 绘制计算的反射率
    plt.subplot(2, 1, 2)
    plt.plot(wavelengths, reflectance, 'g-', label='计算的反射率')
    plt.xlabel('波长 (nm)')
    plt.ylabel('反射率')
    plt.title('计算的反射率')
    plt.grid(True)
    plt.axvspan(wavelengths[218], wavelengths[249], color='yellow', alpha=0.3, label='临界区域')
    plt.axhline(y=0, color='r', linestyle='--', label='反射率=0')
    plt.axhline(y=1, color='b', linestyle='--', label='反射率=1')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('real_data_test.png')
    print('\n已保存图表到 real_data_test.png')
    
    # 结论
    print("\n===== 结论 =====")
    print("1. MATLAB公式 (m-b)/(w-b)*w/m 在某些情况下可能产生负反射率或超过1的反射率")
    print("2. 负反射率通常发生在 m<b（测量值小于黑参考）或 (w-b)很小 的情况")
    print("3. 程序中的处理方式是将负反射率设置为0，将超过1的反射率裁剪为1")
    print("4. 这解释了为什么某些波长区域（如598-629 nm）的反射率在最终结果中为0")

if __name__ == "__main__":
    test_with_real_data() 