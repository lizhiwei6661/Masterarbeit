import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
import os
from color_calculator import ColorCalculator

def main():
    """比较MATLAB和Python中使用的CIE数据"""
    print("=" * 50)
    print("比较MATLAB和Python中使用的CIE数据")
    print("=" * 50)
    
    # 创建ColorCalculator实例
    calculator = ColorCalculator()
    
    # 获取Python中使用的CIE数据
    python_cie_wl = calculator.cie_1931['wavelengths']
    python_cie_x = calculator.cie_1931['x']
    python_cie_y = calculator.cie_1931['y']
    python_cie_z = calculator.cie_1931['z']
    
    print(f"Python中的CIE数据: {len(python_cie_wl)}点")
    print(f"  波长范围: {python_cie_wl[0]}-{python_cie_wl[-1]}nm")
    print(f"  步长: {python_cie_wl[1] - python_cie_wl[0]}nm")
    print(f"  x值范围: {np.min(python_cie_x):.4f}-{np.max(python_cie_x):.4f}")
    print(f"  y值范围: {np.min(python_cie_y):.4f}-{np.max(python_cie_y):.4f}")
    print(f"  z值范围: {np.min(python_cie_z):.4f}-{np.max(python_cie_z):.4f}")
    
    # 加载MATLAB中的xyzBar.mat文件
    xyzbar_path = "Matlab_Input/libraries/xyzBar.mat"
    
    if not os.path.exists(xyzbar_path):
        print(f"错误: {xyzbar_path} 文件不存在!")
        return
    
    try:
        # 加载MATLAB文件
        matlab_data = sio.loadmat(xyzbar_path)
        
        # 输出MATLAB文件的内容
        print("\nMATLAB文件中的键:")
        for key in matlab_data.keys():
            if not key.startswith('__'):  # 跳过内部变量
                print(f"  {key}: 形状={matlab_data[key].shape}, 类型={matlab_data[key].dtype}")
        
        # 提取xyzBar数据
        if 'xyzBar' in matlab_data:
            xyzBar = matlab_data['xyzBar']
            print(f"\nMATLAB中的xyzBar数据: 形状={xyzBar.shape}")
            
            # 假设xyzBar是一个三列的数组，分别对应x, y, z值
            if xyzBar.shape[1] == 3:
                matlab_cie_x = xyzBar[:, 0]
                matlab_cie_y = xyzBar[:, 1]
                matlab_cie_z = xyzBar[:, 2]
                
                # 生成对应的波长数组（假设从380nm开始，间隔5nm）
                if len(xyzBar) == 81:  # 380-780nm，5nm步长
                    matlab_cie_wl = np.arange(380, 781, 5)
                else:
                    # 如果长度不是81，使用自定义波长范围
                    matlab_cie_wl = np.linspace(380, 780, len(xyzBar))
                
                print(f"MATLAB中的CIE数据: {len(matlab_cie_wl)}点")
                print(f"  波长范围: {matlab_cie_wl[0]}-{matlab_cie_wl[-1]}nm")
                print(f"  x值范围: {np.min(matlab_cie_x):.4f}-{np.max(matlab_cie_x):.4f}")
                print(f"  y值范围: {np.min(matlab_cie_y):.4f}-{np.max(matlab_cie_y):.4f}")
                print(f"  z值范围: {np.min(matlab_cie_z):.4f}-{np.max(matlab_cie_z):.4f}")
                
                # 比较特定波长点的值
                for wl in [380, 400, 500, 600, 700, 780]:
                    python_idx = np.where(python_cie_wl == wl)[0][0]
                    matlab_idx = np.where(matlab_cie_wl == wl)[0][0]
                    
                    print(f"\n波长 {wl}nm 处的值:")
                    print(f"  Python: x={python_cie_x[python_idx]:.6f}, y={python_cie_y[python_idx]:.6f}, z={python_cie_z[python_idx]:.6f}")
                    print(f"  MATLAB: x={matlab_cie_x[matlab_idx]:.6f}, y={matlab_cie_y[matlab_idx]:.6f}, z={matlab_cie_z[matlab_idx]:.6f}")
                    print(f"  差异: Δx={abs(python_cie_x[python_idx]-matlab_cie_x[matlab_idx]):.6f}, Δy={abs(python_cie_y[python_idx]-matlab_cie_y[matlab_idx]):.6f}, Δz={abs(python_cie_z[python_idx]-matlab_cie_z[matlab_idx]):.6f}")
                
                # 绘制比较图
                plt.figure(figsize=(15, 10))
                
                # 绘制x值
                plt.subplot(3, 1, 1)
                plt.plot(python_cie_wl, python_cie_x, 'b-', label='Python CIE x')
                plt.plot(matlab_cie_wl, matlab_cie_x, 'r--', label='MATLAB CIE x')
                plt.xlabel('波长 (nm)')
                plt.ylabel('x 值')
                plt.title('CIE 1931 x 函数比较')
                plt.legend()
                plt.grid(True)
                
                # 绘制y值
                plt.subplot(3, 1, 2)
                plt.plot(python_cie_wl, python_cie_y, 'b-', label='Python CIE y')
                plt.plot(matlab_cie_wl, matlab_cie_y, 'r--', label='MATLAB CIE y')
                plt.xlabel('波长 (nm)')
                plt.ylabel('y 值')
                plt.title('CIE 1931 y 函数比较')
                plt.legend()
                plt.grid(True)
                
                # 绘制z值
                plt.subplot(3, 1, 3)
                plt.plot(python_cie_wl, python_cie_z, 'b-', label='Python CIE z')
                plt.plot(matlab_cie_wl, matlab_cie_z, 'r--', label='MATLAB CIE z')
                plt.xlabel('波长 (nm)')
                plt.ylabel('z 值')
                plt.title('CIE 1931 z 函数比较')
                plt.legend()
                plt.grid(True)
                
                plt.tight_layout()
                
                # 保存图表
                output_dir = "test_output"
                os.makedirs(output_dir, exist_ok=True)
                plt.savefig(os.path.join(output_dir, "cie_data_comparison.png"))
                plt.close()
                
                # 将MATLAB的数据保存为Python可以加载的格式
                output_file = os.path.join(output_dir, "matlab_cie_data.npz")
                np.savez(output_file, 
                         wavelengths=matlab_cie_wl, 
                         x=matlab_cie_x, 
                         y=matlab_cie_y, 
                         z=matlab_cie_z)
                print(f"\nMATLAB的CIE数据已保存到 {output_file}")
            else:
                print(f"警告: xyzBar的列数不是3，而是{xyzBar.shape[1]}")
        else:
            print("警告: MATLAB文件中没有'xyzBar'键")
    
    except Exception as e:
        print(f"加载MATLAB文件时出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 