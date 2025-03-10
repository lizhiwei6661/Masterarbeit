import numpy as np
import scipy.io as sio
import os

def main():
    """
    将MATLAB的stdIllum.mat文件转换为CSV格式
    """
    print("开始转换stdIllum.mat到CSV...")
    
    # MATLAB文件路径
    stdillum_path = "Matlab_Input/libraries/stdIllum.mat"
    output_path = "stdIllum.csv"
    
    if not os.path.exists(stdillum_path):
        print(f"错误: MATLAB stdIllum.mat文件不存在: {stdillum_path}")
        return
    
    try:
        # 加载MATLAB文件
        matlab_data = sio.loadmat(stdillum_path)
        
        # 打印所有键，了解文件结构
        print("MATLAB文件中的键:")
        for key in matlab_data.keys():
            if not key.startswith('__'):  # 排除内部变量
                print(f"  - {key}: 形状 {matlab_data[key].shape}")
        
        if 'stdIllum' not in matlab_data:
            print("错误: MATLAB文件中没有'stdIllum'键")
            return
        
        # 提取标准光源数据
        stdIllum = matlab_data['stdIllum']
        print(f"stdIllum数据形状: {stdIllum.shape}")
        
        # 创建波长数组 - 假设是401个点(380-780nm)，1nm步长
        wavelengths = np.arange(380, 781, 1)
        
        if len(wavelengths) != stdIllum.shape[0]:
            print(f"警告: 生成的波长数组长度({len(wavelengths)})与stdIllum数据行数({stdIllum.shape[0]})不一致")
            wavelengths = np.linspace(380, 780, stdIllum.shape[0])
        
        # 确定列数，确定是哪些光源
        num_sources = stdIllum.shape[1]
        source_names = ['A', 'D65', 'D50']
        if num_sources != len(source_names):
            print(f"警告: 源数量({num_sources})与预期名称数量({len(source_names)})不一致")
            if num_sources < len(source_names):
                source_names = source_names[:num_sources]
            else:
                # 添加额外的光源名称
                for i in range(len(source_names), num_sources):
                    source_names.append(f"Source_{i+1}")
        
        # 准备CSV表头
        header = "wavelength," + ",".join(source_names)
        
        # 将数据合并为一个数组
        data_to_save = np.column_stack((wavelengths.reshape(-1, 1), stdIllum))
        
        # 保存为CSV
        np.savetxt(output_path, data_to_save, delimiter=',', header=header, comments='', fmt='%.8f')
        
        print(f"成功将stdIllum数据转换并保存到: {output_path}")
        print(f"数据包含{len(data_to_save)}行，波长范围: {wavelengths[0]}-{wavelengths[-1]}nm")
        print(f"包含{num_sources}个光源: {', '.join(source_names)}")
        
        for i, name in enumerate(source_names):
            source_data = stdIllum[:, i]
            print(f"{name}光源范围: {np.min(source_data):.6f}-{np.max(source_data):.6f}")
        
    except Exception as e:
        print(f"转换过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 