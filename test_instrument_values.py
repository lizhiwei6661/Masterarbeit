import numpy as np
import os
import matplotlib.pyplot as plt
from color_calculator import ColorCalculator

def main():
    """测试仪器值与计算值的对比"""
    print("=" * 50)
    print("测试仪器值与计算值对比")
    print("=" * 50)
    
    # 创建ColorCalculator实例
    calculator = ColorCalculator()
    
    # 设置使用与MATLAB一致的rho_lambda值
    calculator.set_rho_lambda(0.989)
    print(f"设置rho_lambda值为0.989，与MATLAB一致")
    
    # 设置校准模式为Aleksameter
    calculator.set_calibration_mode("aleksameter")
    
    # 数据目录
    data_dir = "Matlab_Input/Import_Sample"
    
    # 加载黑参考和白参考
    black_file = os.path.join(data_dir, "black.csv")
    white_file = os.path.join(data_dir, "white.csv")
    
    black_wavelengths, black_data = calculator.load_measurement_data(black_file)
    white_wavelengths, white_data = calculator.load_measurement_data(white_file)
    
    if black_wavelengths is None or white_wavelengths is None:
        print("无法加载黑/白参考数据")
        return
    
    # 设置参考数据
    calculator.set_calibration_mode("aleksameter", black_ref=black_data, white_ref=white_data)
    
    # 测试文件
    test_files = [
        "tu-berlin00004.csv",
        "tu-berlin00006.csv",
        "tu-berlin00007.csv"
    ]
    
    # 收集结果
    results = []
    
    # 处理每个测试文件
    for test_file in test_files:
        file_path = os.path.join(data_dir, test_file)
        print("\n" + "=" * 30)
        print(f"处理文件: {test_file}")
        print("=" * 30)
        
        # 提取仪器值
        instrument_values = calculator.extract_instrument_values(file_path)
        if instrument_values is not None:
            print(f"成功提取仪器值: ({instrument_values[0]:.6f}, {instrument_values[1]:.6f})")
        else:
            print("未找到仪器值")
        
        # 使用get_xy_coordinates函数获取xy坐标
        # 先使用计算值
        calc_xy, calc_source = calculator.get_xy_coordinates(file_path, use_instrument_values=False)
        # 再使用仪器值
        inst_xy, inst_source = calculator.get_xy_coordinates(file_path, use_instrument_values=True)
        
        print(f"计算值: ({calc_xy[0]:.6f}, {calc_xy[1]:.6f}) [来源: {calc_source}]")
        print(f"仪器值: ({inst_xy[0]:.6f}, {inst_xy[1]:.6f}) [来源: {inst_source}]")
        
        # 收集结果
        results.append({
            'file': test_file,
            'calc_x': calc_xy[0],
            'calc_y': calc_xy[1],
            'inst_x': inst_xy[0],
            'inst_y': inst_xy[1],
            'calc_source': calc_source,
            'inst_source': inst_source
        })
        
        # 绘制色度图，显示计算值和仪器值
        plt.figure(figsize=(10, 10))
        
        # 绘制CIE 1931色度图轮廓
        cie_x = np.array([0.1740, 0.0050, 0.0030, 0.0110, 0.0760, 0.1580, 0.2800, 0.4500, 0.6400, 0.7600, 0.8500, 0.9050, 0.9100, 0.8700, 0.8300, 0.7930, 0.7440, 0.6260, 0.5100, 0.3730, 0.2060])
        cie_y = np.array([0.0050, 0.0050, 0.0200, 0.0880, 0.3400, 0.7300, 0.9540, 0.9950, 0.9200, 0.7000, 0.4900, 0.3100, 0.1300, 0.0390, 0.0168, 0.0082, 0.0039, 0.0080, 0.0190, 0.0500, 0.0490])
        
        plt.plot(cie_x, cie_y, 'k-')
        plt.plot([cie_x[-1], cie_x[0]], [cie_y[-1], cie_y[0]], 'k-')
        
        # 绘制计算值
        plt.plot(calc_xy[0], calc_xy[1], 'ro', markersize=10, label=f'计算值 ({calc_xy[0]:.4f}, {calc_xy[1]:.4f})')
        
        # 绘制仪器值
        plt.plot(inst_xy[0], inst_xy[1], 'bo', markersize=10, label=f'仪器值 ({inst_xy[0]:.4f}, {inst_xy[1]:.4f})')
        
        # 连接两个点
        plt.plot([calc_xy[0], inst_xy[0]], [calc_xy[1], inst_xy[1]], 'g--', label='差异')
        
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title(f'色度坐标对比 - {test_file}')
        plt.legend()
        plt.grid(True)
        plt.axis('equal')
        plt.xlim(0, 0.8)
        plt.ylim(0, 0.9)
        
        # 保存图表
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(os.path.join(output_dir, f"{os.path.splitext(test_file)[0]}_xy_comparison.png"))
        plt.close()
    
    # 保存结果到文本文件
    output_file = os.path.join("test_output", "xy_comparison_results.txt")
    with open(output_file, 'w') as f:
        f.write("文件,计算x,计算y,仪器x,仪器y,计算来源,仪器来源\n")
        for result in results:
            f.write(f"{result['file']},{result['calc_x']:.6f},{result['calc_y']:.6f},{result['inst_x']:.6f},{result['inst_y']:.6f},{result['calc_source']},{result['inst_source']}\n")
    
    print(f"\n结果已保存到 {output_file}")
    print("\n测试完成。")

if __name__ == "__main__":
    main() 