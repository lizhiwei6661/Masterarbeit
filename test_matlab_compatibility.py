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
        # 尝试直接使用pandas读取，跳过前53行元数据
        df = pd.read_csv(file_path, header=None, skiprows=53)
        if df.shape[1] >= 2:
            wavelengths = df.iloc[:, 0].values
            data = df.iloc[:, 1].values
            print(f"成功读取CSV文件: {file_path}")
            print(f"数据范围: {wavelengths[0]}-{wavelengths[-1]}nm, {len(wavelengths)}个点")
            return wavelengths, data
        else:
            raise ValueError(f"CSV文件格式错误: 至少需要2列数据 (波长和值)")
    except Exception as e:
        print(f"读取CSV文件失败: {str(e)}")
        return None, None

def main():
    """主函数，测试与MATLAB的兼容性"""
    print("=" * 50)
    print("测试与MATLAB的XYZ计算兼容性")
    print("=" * 50)
    
    # 创建ColorCalculator实例
    calculator = ColorCalculator()
    
    # 设置使用与MATLAB一致的rho_lambda值
    calculator.set_rho_lambda(0.989)
    print(f"设置rho_lambda值为0.989，与MATLAB一致")
    
    # 设置校准模式为Aleksameter
    calculator.set_calibration_mode("aleksameter")
    
    # 数据目录
    data_dir = "Matlab_Input/Import_Sample"  # 修改为实际的数据目录
    
    # 加载黑参考和白参考
    black_file = os.path.join(data_dir, "black.csv")
    white_file = os.path.join(data_dir, "white.csv")
    
    black_wavelengths, black_data = load_csv_data(black_file)
    white_wavelengths, white_data = load_csv_data(white_file)
    
    # 设置参考数据
    calculator.set_calibration_mode("aleksameter", black_ref=black_data, white_ref=white_data)
    
    # 测试文件
    test_files = [
        "tu-berlin00004.csv",
        "tu-berlin00006.csv",
        "tu-berlin00007.csv"
    ]
    
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
        
        # 绘制反射率曲线
        plt.figure(figsize=(10, 6))
        plt.plot(wavelengths, reflectance)
        plt.xlabel('波长 (nm)')
        plt.ylabel('反射率')
        plt.title(f'反射率曲线 - {test_file}')
        plt.grid(True)
        
        # 保存图表
        output_dir = "test_output"  # 修改为实际的输出目录
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(os.path.join(output_dir, f"{os.path.splitext(test_file)[0]}_reflectance.png"))
        plt.close()
        
    print("\n计算完成。")

if __name__ == "__main__":
    main() 