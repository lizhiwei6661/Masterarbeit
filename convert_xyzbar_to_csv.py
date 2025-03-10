import numpy as np
import scipy.io as sio
import os

def main():
    """
    将MATLAB的xyzBar.mat文件转换为CSV格式
    """
    print("开始转换xyzBar.mat到CSV...")
    
    # MATLAB文件路径
    xyzbar_path = "Matlab_Input/libraries/xyzBar.mat"
    output_path = "xyzBar.csv"
    
    if not os.path.exists(xyzbar_path):
        print(f"错误: MATLAB xyzBar.mat文件不存在: {xyzbar_path}")
        return
    
    try:
        # 加载MATLAB文件
        matlab_data = sio.loadmat(xyzbar_path)
        
        if 'xyzBar' not in matlab_data:
            print("错误: MATLAB文件中没有'xyzBar'键")
            return
        
        # 提取xyzBar数据
        xyzBar = matlab_data['xyzBar']
        
        if xyzBar.shape[1] != 3:
            print(f"错误: xyzBar的列数不是3，而是{xyzBar.shape[1]}")
            return
        
        # 创建波长数组 - xyzBar是401个点(380-780nm)，1nm步长
        wavelengths = np.arange(380, 781, 1)
        
        if len(wavelengths) != len(xyzBar):
            print(f"警告: 生成的波长数组长度({len(wavelengths)})与xyzBar数据长度({len(xyzBar)})不一致")
            wavelengths = np.linspace(380, 780, len(xyzBar))
        
        # 将数据合并为一个数组
        data_to_save = np.column_stack((wavelengths.reshape(-1, 1), xyzBar))
        
        # 保存为CSV
        header = "wavelength,x,y,z"
        np.savetxt(output_path, data_to_save, delimiter=',', header=header, comments='', fmt='%.8f')
        
        print(f"成功将xyzBar数据转换并保存到: {output_path}")
        print(f"数据包含{len(data_to_save)}行，波长范围: {wavelengths[0]}-{wavelengths[-1]}nm")
        print(f"x值范围: {np.min(xyzBar[:, 0]):.6f}-{np.max(xyzBar[:, 0]):.6f}")
        print(f"y值范围: {np.min(xyzBar[:, 1]):.6f}-{np.max(xyzBar[:, 1]):.6f}")
        print(f"z值范围: {np.min(xyzBar[:, 2]):.6f}-{np.max(xyzBar[:, 2]):.6f}")
        
    except Exception as e:
        print(f"转换过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 