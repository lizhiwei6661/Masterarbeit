import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
from color_calculator import ColorCalculator

def load_csv_data(file_path):
    """
    加载CSV文件中的波长和数据
    
    参数:
        file_path: CSV文件路径
        
    返回:
        (wavelengths, data): 波长和数据
    """
    try:
        # 尝试首先确定数据开始行
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        # 查找数据开始行（通常是第54行）
        data_start_line = 53  # 默认值
        for i, line in enumerate(lines):
            if i > 10 and i < 60:  # 在前60行中搜索
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    try:
                        # 尝试将第一列转换为整数（波长值）
                        wavelength = int(parts[0])
                        if wavelength == 380:  # 通常从380nm开始
                            data_start_line = i
                            break
                    except:
                        continue
        
        print(f"从第{data_start_line+1}行开始读取数据")
        
        # 读取数据
        wavelengths = []
        values = []
        
        for line in lines[data_start_line:]:
            parts = line.strip().split(',')
            if len(parts) >= 2:
                try:
                    wavelength = float(parts[0])
                    value = float(parts[1])
                    wavelengths.append(wavelength)
                    values.append(value)
                except:
                    continue
        
        if len(wavelengths) == 0:
            raise ValueError("未找到有效数据")
            
        return np.array(wavelengths), np.array(values)
    
    except Exception as e:
        print(f"读取CSV文件失败: {str(e)}")
        return None, None

def main():
    """主函数，测试XYZ计算"""
    print("=" * 50)
    print("测试XYZ值计算")
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
    
    black_wavelengths, black_data = load_csv_data(black_file)
    white_wavelengths, white_data = load_csv_data(white_file)
    
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
        
        # 加载测量数据
        wavelengths, measurement_data = load_csv_data(file_path)
        
        if wavelengths is None or measurement_data is None:
            print(f"跳过文件 {test_file} 因为无法读取数据")
            continue
        
        # 计算反射率
        reflectance = calculator.calculate_reflectance(measurement_data, wavelengths)
        
        # 验证特定波长处的反射率
        test_wavelength = 380  # nm
        test_index = np.where(wavelengths == test_wavelength)[0][0]
        print(f"波长 {test_wavelength}nm 处的反射率: {reflectance[test_index]:.8f}")
        
        # 计算XYZ值
        xyz = calculator.calculate_xyz(reflectance, wavelengths, use_matlab_compatible=True)
        print(f"XYZ值: {xyz}")
        
        # 计算xy色度坐标
        xy = calculator.xyz_to_xy(xyz)
        print(f"xy色度坐标: ({xy[0]:.6f}, {xy[1]:.6f})")
        
        # MATLAB参考值 - 请替换为MATLAB给出的实际值
        matlab_xy = {
            "tu-berlin00004.csv": [0.3886, 0.3184],
            "tu-berlin00006.csv": [0.3873, 0.3188],
            "tu-berlin00007.csv": [0.3900, 0.3198]
        }
        
        if test_file in matlab_xy:
            ref_xy = matlab_xy[test_file]
            print(f"MATLAB参考xy: ({ref_xy[0]:.6f}, {ref_xy[1]:.6f})")
            print(f"差异: Δx={abs(xy[0]-ref_xy[0]):.6f}, Δy={abs(xy[1]-ref_xy[1]):.6f}")
            
            # 收集结果
            results.append({
                'file': test_file,
                'x_python': xy[0],
                'y_python': xy[1],
                'x_matlab': ref_xy[0],
                'y_matlab': ref_xy[1],
                'delta_x': abs(xy[0] - ref_xy[0]),
                'delta_y': abs(xy[1] - ref_xy[1])
            })
        
        # 绘制反射率曲线
        plt.figure(figsize=(10, 6))
        plt.plot(wavelengths, reflectance)
        plt.xlabel('波长 (nm)')
        plt.ylabel('反射率')
        plt.title(f'反射率曲线 - {test_file}')
        plt.grid(True)
        
        # 保存图表
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(os.path.join(output_dir, f"{os.path.splitext(test_file)[0]}_reflectance.png"))
        plt.close()
    
    # 保存结果到CSV
    if results:
        results_df = pd.DataFrame(results)
        results_file = os.path.join("test_output", "xyz_calculation_results.csv")
        results_df.to_csv(results_file, index=False)
        print(f"\n结果已保存到 {results_file}")
    
    print("\n计算完成。")

if __name__ == "__main__":
    main() 