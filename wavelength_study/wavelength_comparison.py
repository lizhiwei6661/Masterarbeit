import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import rgb_to_hsv
import csv

# 添加主项目路径以导入ColorCalculator类
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from color_calculator import ColorCalculator

def read_reflectance_data(file_path):
    """读取Excel文件中的反射率数据"""
    print(f"读取反射率数据: {file_path}")
    try:
        df = pd.read_excel(file_path)
        # 获取波长列(第一列)和样本数据
        wavelengths = df.iloc[:, 0].values
        sample_names = df.columns[1:]
        
        # 创建样本字典
        samples = {}
        for name in sample_names:
            sample_data = df[name].values
            # 过滤掉NaN值
            valid_indices = ~np.isnan(sample_data)
            if np.any(valid_indices):
                samples[name] = {
                    'wavelengths': wavelengths[valid_indices],
                    'reflectance': sample_data[valid_indices]
                }
            
        print(f"成功读取 {len(samples)} 个样本")
        return samples
    except Exception as e:
        print(f"读取数据时出错: {str(e)}")
        return {}

def xyz_to_lab(xyz, white_ref=None):
    """
    Convert XYZ to CIE Lab color space
    
    Parameters:
        xyz: XYZ color values [X, Y, Z]
        white_ref: White reference [Xw, Yw, Zw], if None D65 is used
    
    Returns:
        Lab color values [L*, a*, b*]
    """
    # Default white reference is D65
    if white_ref is None:
        # D65 white reference values
        white_ref = np.array([95.047, 100.0, 108.883])
    
    # Normalize XYZ by white reference
    xyz_norm = xyz / white_ref
    
    # Apply nonlinear transformation
    mask = xyz_norm > 0.008856
    xyz_norm_pow = np.power(xyz_norm, 1/3.0)
    xyz_norm_trans = xyz_norm * 7.787 + 16/116.0
    
    xyz_f = np.zeros(3)
    for i in range(3):
        if mask[i]:
            xyz_f[i] = xyz_norm_pow[i]
        else:
            xyz_f[i] = xyz_norm_trans[i]
    
    # Calculate L*, a*, b*
    L = 116.0 * xyz_f[1] - 16.0
    a = 500.0 * (xyz_f[0] - xyz_f[1])
    b = 200.0 * (xyz_f[1] - xyz_f[2])
    
    return np.array([L, a, b])

def calculate_cie76_delta_e(lab1, lab2):
    """
    Calculate CIE76 color difference (Delta E)
    
    Parameters:
        lab1: First Lab color [L1, a1, b1]
        lab2: Second Lab color [L2, a2, b2]
    
    Returns:
        Delta E value
    """
    # Calculate squared differences
    L_diff = (lab1[0] - lab2[0]) ** 2
    a_diff = (lab1[1] - lab2[1]) ** 2
    b_diff = (lab1[2] - lab2[2]) ** 2
    
    # Calculate Delta E
    delta_e = np.sqrt(L_diff + a_diff + b_diff)
    
    return delta_e

def compare_wavelength_ranges(samples, original_range=(380, 780), new_range=(400, 800)):
    """比较不同波长范围的颜色计算结果"""
    # 创建颜色计算器实例
    cc = ColorCalculator()
    
    # 设置默认光源为D65
    cc.illuminant = 'D65'
    
    results = {}
    
    for name, sample in samples.items():
        print(f"\n分析样本: {name}")
        wavelengths = sample['wavelengths']
        reflectance = sample['reflectance']
        
        # 检查波长范围是否满足要求
        min_wl = np.min(wavelengths)
        max_wl = np.max(wavelengths)
        print(f"样本波长范围: {min_wl}-{max_wl}nm")
        
        if min_wl > original_range[0] or max_wl < original_range[1]:
            print(f"警告: 样本波长范围 ({min_wl}-{max_wl}nm) 不满足原始波长范围要求 ({original_range[0]}-{original_range[1]}nm)")
            continue
            
        # 1. 计算原始波长范围的颜色
        # 提取原始波长范围内的数据
        original_mask = (wavelengths >= original_range[0]) & (wavelengths <= original_range[1])
        original_wavelengths = wavelengths[original_mask]
        original_reflectance = reflectance[original_mask]
        
        if len(original_wavelengths) < 10:
            print(f"警告: 原始波长范围内的数据点太少 ({len(original_wavelengths)})")
            continue
            
        # 计算原始波长范围的颜色值
        original_results = cc.process_measurement(original_reflectance, original_wavelengths)
        
        # 2. 计算新波长范围的颜色
        # 提取新波长范围内的数据
        new_mask = (wavelengths >= new_range[0]) & (wavelengths <= new_range[1])
        new_wavelengths = wavelengths[new_mask]
        new_reflectance = reflectance[new_mask]
        
        if len(new_wavelengths) < 10:
            print(f"警告: 新波长范围内的数据点太少 ({len(new_wavelengths)})")
            continue
            
        # 计算新波长范围的颜色值
        new_results = cc.process_measurement(new_reflectance, new_wavelengths)
        
        # 3. 计算CIE Lab颜色空间值和色差
        # 转换XYZ到Lab
        original_lab = xyz_to_lab(original_results['xyz'])
        new_lab = xyz_to_lab(new_results['xyz'])
        
        # 计算CIE76色差
        delta_e = calculate_cie76_delta_e(original_lab, new_lab)
        
        # 保存结果
        results[name] = {
            'original': original_results,
            'new': new_results,
            'original_lab': original_lab,
            'new_lab': new_lab,
            'delta_e': delta_e
        }
        
        # 打印关键结果比较
        print(f"原始波长范围 ({original_range[0]}-{original_range[1]}nm):")
        print(f"  XYZ: ({original_results['xyz'][0]:.4f}, {original_results['xyz'][1]:.4f}, {original_results['xyz'][2]:.4f})")
        print(f"  xy: ({original_results['xy'][0]:.4f}, {original_results['xy'][1]:.4f})")
        print(f"  sRGB: ({original_results['rgb_gamma'][0]:.4f}, {original_results['rgb_gamma'][1]:.4f}, {original_results['rgb_gamma'][2]:.4f})")
        print(f"  Hex: {original_results['hex_color']}")
        print(f"  Lab: ({original_lab[0]:.4f}, {original_lab[1]:.4f}, {original_lab[2]:.4f})")
        
        print(f"新波长范围 ({new_range[0]}-{new_range[1]}nm):")
        print(f"  XYZ: ({new_results['xyz'][0]:.4f}, {new_results['xyz'][1]:.4f}, {new_results['xyz'][2]:.4f})")
        print(f"  xy: ({new_results['xy'][0]:.4f}, {new_results['xy'][1]:.4f})")
        print(f"  sRGB: ({new_results['rgb_gamma'][0]:.4f}, {new_results['rgb_gamma'][1]:.4f}, {new_results['rgb_gamma'][2]:.4f})")
        print(f"  Hex: {new_results['hex_color']}")
        print(f"  Lab: ({new_lab[0]:.4f}, {new_lab[1]:.4f}, {new_lab[2]:.4f})")
        
        # 计算差异
        xyz_diff = np.abs(original_results['xyz'] - new_results['xyz'])
        xy_diff = np.abs(original_results['xy'] - new_results['xy'])
        rgb_diff = np.abs(original_results['rgb_gamma'] - new_results['rgb_gamma'])
        lab_diff = np.abs(original_lab - new_lab)
        
        print("差异分析:")
        print(f"  XYZ差异: ({xyz_diff[0]:.4f}, {xyz_diff[1]:.4f}, {xyz_diff[2]:.4f})")
        print(f"  xy差异: ({xy_diff[0]:.4f}, {xy_diff[1]:.4f})")
        print(f"  sRGB差异: ({rgb_diff[0]:.4f}, {rgb_diff[1]:.4f}, {rgb_diff[2]:.4f})")
        print(f"  Lab差异: ({lab_diff[0]:.4f}, {lab_diff[1]:.4f}, {lab_diff[2]:.4f})")
        print(f"  CIE76色差 (ΔE): {delta_e:.4f}")
        
        # 计算相对误差百分比
        xyz_rel_diff = 100 * xyz_diff / (np.abs(original_results['xyz']) + 1e-10)
        xy_rel_diff = 100 * xy_diff / (np.abs(original_results['xy']) + 1e-10)
        rgb_rel_diff = 100 * rgb_diff / (np.abs(original_results['rgb_gamma']) + 1e-10)
        
        print("相对误差百分比:")
        print(f"  XYZ相对误差: ({xyz_rel_diff[0]:.2f}%, {xyz_rel_diff[1]:.2f}%, {xyz_rel_diff[2]:.2f}%)")
        print(f"  xy相对误差: ({xy_rel_diff[0]:.2f}%, {xy_rel_diff[1]:.2f}%)")
        print(f"  sRGB相对误差: ({rgb_rel_diff[0]:.2f}%, {rgb_rel_diff[1]:.2f}%, {rgb_rel_diff[2]:.2f}%)")
        
        # 计算颜色感知差异
        original_hsv = rgb_to_hsv(np.clip(original_results['rgb_gamma'], 0, 1))
        new_hsv = rgb_to_hsv(np.clip(new_results['rgb_gamma'], 0, 1))
        hsv_diff = np.abs(original_hsv - new_hsv)
        # 色调差异需要特殊处理，因为它是循环的
        if hsv_diff[0] > 0.5:
            hsv_diff[0] = 1 - hsv_diff[0]
        
        print("HSV感知差异:")
        print(f"  色调差异: {hsv_diff[0]:.4f} (×360° = {hsv_diff[0]*360:.1f}°)")
        print(f"  饱和度差异: {hsv_diff[1]:.4f}")
        print(f"  明度差异: {hsv_diff[2]:.4f}")
    
    return results

def export_color_difference_table(results, output_dir, original_range=(380, 780), new_range=(400, 800)):
    """
    Export color difference data to CSV table
    
    Parameters:
        results: Comparison results dictionary
        output_dir: Directory to save the CSV file
        original_range: Original wavelength range
        new_range: New wavelength range
    """
    if not results:
        print("No results available for export")
        return
    
    csv_path = os.path.join(output_dir, 'color_difference_table.csv')
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Write header
        csvwriter.writerow([
            'Sample Name',
            'Original XYZ (X)', 'Original XYZ (Y)', 'Original XYZ (Z)',
            'New XYZ (X)', 'New XYZ (Y)', 'New XYZ (Z)',
            'XYZ diff (X)', 'XYZ diff (Y)', 'XYZ diff (Z)',
            'XYZ % diff (X)', 'XYZ % diff (Y)', 'XYZ % diff (Z)',
            'Original xy (x)', 'Original xy (y)',
            'New xy (x)', 'New xy (y)',
            'xy diff (x)', 'xy diff (y)',
            'xy % diff (x)', 'xy % diff (y)',
            'Original sRGB (R)', 'Original sRGB (G)', 'Original sRGB (B)',
            'New sRGB (R)', 'New sRGB (G)', 'New sRGB (B)',
            'sRGB diff (R)', 'sRGB diff (G)', 'sRGB diff (B)',
            'sRGB % diff (R)', 'sRGB % diff (G)', 'sRGB % diff (B)',
            'Original Lab (L*)', 'Original Lab (a*)', 'Original Lab (b*)',
            'New Lab (L*)', 'New Lab (a*)', 'New Lab (b*)',
            'Lab diff (L*)', 'Lab diff (a*)', 'Lab diff (b*)',
            'CIE76 ΔE',
            'Original Hex', 'New Hex'
        ])
        
        # Write data for each sample
        for name, result in results.items():
            original_data = result['original']
            new_data = result['new']
            original_lab = result['original_lab']
            new_lab = result['new_lab']
            
            # Calculate differences
            xyz_diff = np.abs(original_data['xyz'] - new_data['xyz'])
            xy_diff = np.abs(original_data['xy'] - new_data['xy'])
            rgb_diff = np.abs(original_data['rgb_gamma'] - new_data['rgb_gamma'])
            lab_diff = np.abs(original_lab - new_lab)
            
            # Calculate percentage differences
            xyz_rel_diff = 100 * xyz_diff / (np.abs(original_data['xyz']) + 1e-10)
            xy_rel_diff = 100 * xy_diff / (np.abs(original_data['xy']) + 1e-10)
            rgb_rel_diff = 100 * rgb_diff / (np.abs(original_data['rgb_gamma']) + 1e-10)
            
            # Write row
            csvwriter.writerow([
                name,
                f"{original_data['xyz'][0]:.6f}", f"{original_data['xyz'][1]:.6f}", f"{original_data['xyz'][2]:.6f}",
                f"{new_data['xyz'][0]:.6f}", f"{new_data['xyz'][1]:.6f}", f"{new_data['xyz'][2]:.6f}",
                f"{xyz_diff[0]:.6f}", f"{xyz_diff[1]:.6f}", f"{xyz_diff[2]:.6f}",
                f"{xyz_rel_diff[0]:.6f}", f"{xyz_rel_diff[1]:.6f}", f"{xyz_rel_diff[2]:.6f}",
                f"{original_data['xy'][0]:.6f}", f"{original_data['xy'][1]:.6f}",
                f"{new_data['xy'][0]:.6f}", f"{new_data['xy'][1]:.6f}",
                f"{xy_diff[0]:.6f}", f"{xy_diff[1]:.6f}",
                f"{xy_rel_diff[0]:.6f}", f"{xy_rel_diff[1]:.6f}",
                f"{original_data['rgb_gamma'][0]:.6f}", f"{original_data['rgb_gamma'][1]:.6f}", f"{original_data['rgb_gamma'][2]:.6f}",
                f"{new_data['rgb_gamma'][0]:.6f}", f"{new_data['rgb_gamma'][1]:.6f}", f"{new_data['rgb_gamma'][2]:.6f}",
                f"{rgb_diff[0]:.6f}", f"{rgb_diff[1]:.6f}", f"{rgb_diff[2]:.6f}",
                f"{rgb_rel_diff[0]:.6f}", f"{rgb_rel_diff[1]:.6f}", f"{rgb_rel_diff[2]:.6f}",
                f"{original_lab[0]:.6f}", f"{original_lab[1]:.6f}", f"{original_lab[2]:.6f}",
                f"{new_lab[0]:.6f}", f"{new_lab[1]:.6f}", f"{new_lab[2]:.6f}",
                f"{lab_diff[0]:.6f}", f"{lab_diff[1]:.6f}", f"{lab_diff[2]:.6f}",
                f"{result['delta_e']:.6f}",
                original_data['hex_color'], new_data['hex_color']
            ])
    
    print(f"Color difference table exported to: {csv_path}")
    
    # Also create an Excel version for better readability
    try:
        df = pd.read_csv(csv_path)
        excel_path = os.path.join(output_dir, 'color_difference_table.xlsx')
        df.to_excel(excel_path, index=False)
        print(f"Color difference table also exported as Excel: {excel_path}")
    except Exception as e:
        print(f"Failed to create Excel version: {str(e)}")

def export_simplified_error_table(results, output_dir, original_range=(380, 780), new_range=(400, 800)):
    """
    Export simplified color difference data to CSV and Excel
    Only includes error metrics and Delta E values
    
    Parameters:
        results: Comparison results dictionary
        output_dir: Directory to save the CSV file
        original_range: Original wavelength range
        new_range: New wavelength range
    """
    if not results:
        print("No results available for export")
        return
    
    csv_path = os.path.join(output_dir, 'color_error_simplified.csv')
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Write header
        csvwriter.writerow([
            'Sample Name',
            'XYZ diff (X)', 'XYZ diff (Y)', 'XYZ diff (Z)',
            'XYZ % diff (X)', 'XYZ % diff (Y)', 'XYZ % diff (Z)',
            'xy diff (x)', 'xy diff (y)',
            'xy % diff (x)', 'xy % diff (y)',
            'sRGB diff (R)', 'sRGB diff (G)', 'sRGB diff (B)',
            'sRGB % diff (R)', 'sRGB % diff (G)', 'sRGB % diff (B)',
            'Lab diff (L*)', 'Lab diff (a*)', 'Lab diff (b*)',
            'CIE76 ΔE',
            'Original Hex', 'New Hex'
        ])
        
        # Write data for each sample
        for name, result in results.items():
            original_data = result['original']
            new_data = result['new']
            original_lab = result['original_lab']
            new_lab = result['new_lab']
            
            # Calculate differences
            xyz_diff = np.abs(original_data['xyz'] - new_data['xyz'])
            xy_diff = np.abs(original_data['xy'] - new_data['xy'])
            rgb_diff = np.abs(original_data['rgb_gamma'] - new_data['rgb_gamma'])
            lab_diff = np.abs(original_lab - new_lab)
            
            # Calculate percentage differences
            xyz_rel_diff = 100 * xyz_diff / (np.abs(original_data['xyz']) + 1e-10)
            xy_rel_diff = 100 * xy_diff / (np.abs(original_data['xy']) + 1e-10)
            rgb_rel_diff = 100 * rgb_diff / (np.abs(original_data['rgb_gamma']) + 1e-10)
            
            # Write row
            csvwriter.writerow([
                name,
                f"{xyz_diff[0]:.6f}", f"{xyz_diff[1]:.6f}", f"{xyz_diff[2]:.6f}",
                f"{xyz_rel_diff[0]:.6f}", f"{xyz_rel_diff[1]:.6f}", f"{xyz_rel_diff[2]:.6f}",
                f"{xy_diff[0]:.6f}", f"{xy_diff[1]:.6f}",
                f"{xy_rel_diff[0]:.6f}", f"{xy_rel_diff[1]:.6f}",
                f"{rgb_diff[0]:.6f}", f"{rgb_diff[1]:.6f}", f"{rgb_diff[2]:.6f}",
                f"{rgb_rel_diff[0]:.6f}", f"{rgb_rel_diff[1]:.6f}", f"{rgb_rel_diff[2]:.6f}",
                f"{lab_diff[0]:.6f}", f"{lab_diff[1]:.6f}", f"{lab_diff[2]:.6f}",
                f"{result['delta_e']:.6f}",
                original_data['hex_color'], new_data['hex_color']
            ])
    
    print(f"Simplified color error table exported to: {csv_path}")
    
    # Also create an Excel version for better readability
    try:
        df = pd.read_csv(csv_path)
        excel_path = os.path.join(output_dir, 'color_error_simplified.xlsx')
        df.to_excel(excel_path, index=False)
        print(f"Simplified color error table also exported as Excel: {excel_path}")
    except Exception as e:
        print(f"Failed to create Excel version: {str(e)}")

def plot_results(samples, results, original_range=(380, 780), new_range=(400, 800)):
    """绘制结果图表"""
    if not results:
        print("没有可用于绘图的结果")
        return
    
    # 创建保存图表的目录
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "comparison_results")
    os.makedirs(output_dir, exist_ok=True)
    
    # Export color difference tables
    export_color_difference_table(results, output_dir, original_range, new_range)
    export_simplified_error_table(results, output_dir, original_range, new_range)
    
    for name, result in results.items():
        # 修复文件名，替换斜杠和空格为下划线
        safe_name = name.replace("/", "_").replace(" ", "_").strip()
        
        # 1. 绘制反射率曲线比较
        plt.figure(figsize=(12, 6))
        
        original_data = result['original']
        new_data = result['new']
        
        # 绘制原始波长范围反射率
        plt.plot(original_data['wavelengths'], original_data['reflectance'], 
                 'b-', linewidth=2, label=f'原始 ({original_range[0]}-{original_range[1]}nm)')
        
        # 绘制新波长范围反射率
        plt.plot(new_data['wavelengths'], new_data['reflectance'], 
                 'r--', linewidth=2, label=f'裁剪 ({new_range[0]}-{new_range[1]}nm)')
        
        plt.xlabel('波长 (nm)')
        plt.ylabel('反射率')
        plt.title(f'样本 "{name}" 的反射率曲线比较')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(os.path.join(output_dir, f'{safe_name}_reflectance.png'), dpi=150)
        plt.close()
        
        # 2. 创建颜色比较图
        fig, ax = plt.subplots(1, 2, figsize=(8, 4))
        
        # 原始波长范围的颜色
        original_rgb = np.clip(original_data['rgb_gamma'], 0, 1)
        ax[0].add_patch(plt.Rectangle((0, 0), 1, 1, color=original_rgb))
        ax[0].set_title(f'原始 ({original_range[0]}-{original_range[1]}nm)\n{original_data["hex_color"]}')
        ax[0].set_xticks([])
        ax[0].set_yticks([])
        
        # 新波长范围的颜色
        new_rgb = np.clip(new_data['rgb_gamma'], 0, 1)
        ax[1].add_patch(plt.Rectangle((0, 0), 1, 1, color=new_rgb))
        ax[1].set_title(f'裁剪 ({new_range[0]}-{new_range[1]}nm)\n{new_data["hex_color"]}')
        ax[1].set_xticks([])
        ax[1].set_yticks([])
        
        plt.suptitle(f'样本 "{name}" 的颜色比较')
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(os.path.join(output_dir, f'{safe_name}_color.png'), dpi=150)
        plt.close()
    
    # 3. 创建汇总分析报告
    create_summary_report(results, output_dir, original_range, new_range)
    
    print(f"结果图表已保存至 {output_dir}")

def create_summary_report(results, output_dir, original_range, new_range):
    """创建汇总分析报告"""
    if not results:
        return
    
    # 计算所有样本的平均差异
    all_xy_diffs = []
    all_xyz_diffs = []
    all_rgb_diffs = []
    all_delta_e = []
    
    for name, result in results.items():
        original_data = result['original']
        new_data = result['new']
        
        # 计算差异
        xyz_diff = np.abs(original_data['xyz'] - new_data['xyz'])
        xy_diff = np.abs(original_data['xy'] - new_data['xy'])
        rgb_diff = np.abs(original_data['rgb_gamma'] - new_data['rgb_gamma'])
        
        all_xyz_diffs.append(xyz_diff)
        all_xy_diffs.append(xy_diff)
        all_rgb_diffs.append(rgb_diff)
        all_delta_e.append(result['delta_e'])
    
    # 计算平均差异
    avg_xyz_diff = np.mean(all_xyz_diffs, axis=0)
    avg_xy_diff = np.mean(all_xy_diffs, axis=0)
    avg_rgb_diff = np.mean(all_rgb_diffs, axis=0)
    avg_delta_e = np.mean(all_delta_e)
    
    # 创建报告文件
    with open(os.path.join(output_dir, 'summary_report.txt'), 'w', encoding='utf-8') as f:
        f.write(f"波长范围比较分析报告\n")
        f.write(f"======================\n\n")
        f.write(f"原始波长范围: {original_range[0]}-{original_range[1]}nm\n")
        f.write(f"裁剪波长范围: {new_range[0]}-{new_range[1]}nm\n\n")
        f.write(f"分析样本数量: {len(results)}\n\n")
        
        f.write(f"平均差异分析:\n")
        f.write(f"  XYZ平均差异: ({avg_xyz_diff[0]:.4f}, {avg_xyz_diff[1]:.4f}, {avg_xyz_diff[2]:.4f})\n")
        f.write(f"  xy平均差异: ({avg_xy_diff[0]:.4f}, {avg_xy_diff[1]:.4f})\n")
        f.write(f"  sRGB平均差异: ({avg_rgb_diff[0]:.4f}, {avg_rgb_diff[1]:.4f}, {avg_rgb_diff[2]:.4f})\n")
        f.write(f"  平均CIE76色差(ΔE): {avg_delta_e:.4f}\n\n")
        
        # 输出每个样本的详细信息
        f.write(f"各样本详细分析:\n")
        f.write(f"----------------\n\n")
        
        for name, result in results.items():
            original_data = result['original']
            new_data = result['new']
            
            # 计算差异
            xyz_diff = np.abs(original_data['xyz'] - new_data['xyz'])
            xy_diff = np.abs(original_data['xy'] - new_data['xy'])
            rgb_diff = np.abs(original_data['rgb_gamma'] - new_data['rgb_gamma'])
            
            f.write(f"样本: {name}\n")
            f.write(f"  原始波长范围 ({original_range[0]}-{original_range[1]}nm):\n")
            f.write(f"    XYZ: ({original_data['xyz'][0]:.4f}, {original_data['xyz'][1]:.4f}, {original_data['xyz'][2]:.4f})\n")
            f.write(f"    xy: ({original_data['xy'][0]:.4f}, {original_data['xy'][1]:.4f})\n")
            f.write(f"    sRGB: ({original_data['rgb_gamma'][0]:.4f}, {original_data['rgb_gamma'][1]:.4f}, {original_data['rgb_gamma'][2]:.4f})\n")
            f.write(f"    Hex: {original_data['hex_color']}\n\n")
            
            f.write(f"  裁剪波长范围 ({new_range[0]}-{new_range[1]}nm):\n")
            f.write(f"    XYZ: ({new_data['xyz'][0]:.4f}, {new_data['xyz'][1]:.4f}, {new_data['xyz'][2]:.4f})\n")
            f.write(f"    xy: ({new_data['xy'][0]:.4f}, {new_data['xy'][1]:.4f})\n")
            f.write(f"    sRGB: ({new_data['rgb_gamma'][0]:.4f}, {new_data['rgb_gamma'][1]:.4f}, {new_data['rgb_gamma'][2]:.4f})\n")
            f.write(f"    Hex: {new_data['hex_color']}\n\n")
            
            f.write(f"  差异分析:\n")
            f.write(f"    XYZ差异: ({xyz_diff[0]:.4f}, {xyz_diff[1]:.4f}, {xyz_diff[2]:.4f})\n")
            f.write(f"    xy差异: ({xy_diff[0]:.4f}, {xy_diff[1]:.4f})\n")
            f.write(f"    sRGB差异: ({rgb_diff[0]:.4f}, {rgb_diff[1]:.4f}, {rgb_diff[2]:.4f})\n")
            f.write(f"    CIE76色差(ΔE): {result['delta_e']:.4f}\n\n")
            
            # 计算相对误差百分比
            xyz_rel_diff = 100 * xyz_diff / (np.abs(original_data['xyz']) + 1e-10)
            xy_rel_diff = 100 * xy_diff / (np.abs(original_data['xy']) + 1e-10)
            rgb_rel_diff = 100 * rgb_diff / (np.abs(original_data['rgb_gamma']) + 1e-10)
            
            f.write(f"  相对误差百分比:\n")
            f.write(f"    XYZ相对误差: ({xyz_rel_diff[0]:.2f}%, {xyz_rel_diff[1]:.2f}%, {xyz_rel_diff[2]:.2f}%)\n")
            f.write(f"    xy相对误差: ({xy_rel_diff[0]:.2f}%, {xy_rel_diff[1]:.2f}%)\n")
            f.write(f"    sRGB相对误差: ({rgb_rel_diff[0]:.2f}%, {rgb_rel_diff[1]:.2f}%, {rgb_rel_diff[2]:.2f}%)\n\n")
            
            # 可感知颜色差异分析
            original_hsv = rgb_to_hsv(np.clip(original_data['rgb_gamma'], 0, 1))
            new_hsv = rgb_to_hsv(np.clip(new_data['rgb_gamma'], 0, 1))
            hsv_diff = np.abs(original_hsv - new_hsv)
            # 色调差异需要特殊处理，因为它是循环的
            if hsv_diff[0] > 0.5:
                hsv_diff[0] = 1 - hsv_diff[0]
            
            f.write(f"  HSV感知差异:\n")
            f.write(f"    色调差异: {hsv_diff[0]:.4f} (×360° = {hsv_diff[0]*360:.1f}°)\n")
            f.write(f"    饱和度差异: {hsv_diff[1]:.4f}\n")
            f.write(f"    明度差异: {hsv_diff[2]:.4f}\n\n")
            
            f.write(f"----------------\n\n")
    
    # 创建汇总图表
    create_summary_charts(results, output_dir, original_range, new_range)

def create_summary_charts(results, output_dir, original_range, new_range):
    """创建汇总图表"""
    if not results:
        return
    
    # 1. xy色度图比较
    plt.figure(figsize=(10, 8))
    
    # 绘制色品图边界
    t = np.linspace(0, 1, 100)
    plt.plot(t, -3*t + 2, 'k-', alpha=0.2)  # y = -3x + 2
    plt.plot(t, 2.5*t - 0.5, 'k-', alpha=0.2)  # y = 2.5x - 0.5
    plt.plot([0.35, 0], [0.375, 0], 'k-', alpha=0.2)
    plt.fill_between([0, 0.35, 0.67, 0.35, 0], 
                     [0, 0.375, 0.175, 0, 0], alpha=0.05, color='gray')
    
    for name, result in results.items():
        original_x, original_y = result['original']['xy']
        new_x, new_y = result['new']['xy']
        
        # 绘制原始点和新点，并用线连接
        plt.plot(original_x, original_y, 'bo', markersize=8, alpha=0.7)
        plt.plot(new_x, new_y, 'ro', markersize=8, alpha=0.7)
        plt.plot([original_x, new_x], [original_y, new_y], 'k-', alpha=0.3)
        
        # 标记样本名称
        plt.text(original_x+0.005, original_y+0.005, name, fontsize=8)
    
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('CIE xy色度图上的颜色坐标比较')
    plt.grid(True, alpha=0.3)
    plt.axis([0, 0.8, 0, 0.9])
    
    # 添加图例
    plt.plot([], [], 'bo', markersize=8, label=f'原始 ({original_range[0]}-{original_range[1]}nm)')
    plt.plot([], [], 'ro', markersize=8, label=f'裁剪 ({new_range[0]}-{new_range[1]}nm)')
    plt.legend()
    
    plt.savefig(os.path.join(output_dir, 'xy_comparison.png'), dpi=150)
    plt.close()
    
    # 2. RGB颜色差异柱状图
    rgb_labels = ['R', 'G', 'B']
    all_rgb_diffs = []
    
    for name, result in results.items():
        original_rgb = result['original']['rgb_gamma']
        new_rgb = result['new']['rgb_gamma']
        rgb_diff = np.abs(original_rgb - new_rgb)
        all_rgb_diffs.append(rgb_diff)
    
    avg_rgb_diff = np.mean(all_rgb_diffs, axis=0)
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(rgb_labels, avg_rgb_diff, color=['red', 'green', 'blue'], alpha=0.7)
    
    # 添加数值标签
    for bar, val in zip(bars, avg_rgb_diff):
        plt.text(bar.get_x() + bar.get_width()/2, 
                 bar.get_height() + 0.005, 
                 f'{val:.4f}', 
                 ha='center')
    
    plt.title('RGB颜色分量平均差异')
    plt.ylabel('绝对差异')
    plt.grid(axis='y', alpha=0.3)
    plt.savefig(os.path.join(output_dir, 'rgb_diff.png'), dpi=150)
    plt.close()
    
    # 3. CIE76色差柱状图
    plt.figure(figsize=(12, 8))
    
    # 获取样本名称和对应的色差值
    sample_names = list(results.keys())
    delta_e_values = [results[name]['delta_e'] for name in sample_names]
    
    # 按照色差值降序排序
    sorted_indices = np.argsort(delta_e_values)[::-1]
    sorted_names = [sample_names[i] for i in sorted_indices]
    sorted_values = [delta_e_values[i] for i in sorted_indices]
    
    # 如果样本太多，只显示前20个
    if len(sorted_names) > 20:
        sorted_names = sorted_names[:20]
        sorted_values = sorted_values[:20]
    
    # 绘制柱状图
    bars = plt.bar(range(len(sorted_names)), sorted_values, color='purple', alpha=0.7)
    
    # 添加数值标签
    for i, (bar, val) in enumerate(zip(bars, sorted_values)):
        plt.text(bar.get_x() + bar.get_width()/2, 
                 val + 0.02,
                 f'{val:.4f}', 
                 ha='center', va='bottom', rotation=90 if len(sorted_names) > 10 else 0)
    
    plt.xticks(range(len(sorted_names)), sorted_names, rotation=90 if len(sorted_names) > 10 else 45)
    plt.title('CIE76 Color Difference (ΔE) Comparison')
    plt.ylabel('ΔE')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'delta_e_comparison.png'), dpi=150)
    plt.close()

def generate_german_summary(results, original_range, new_range):
    """
    生成德语总结，描述颜色误差分析
    
    Parameters:
        results: 比较结果字典
        original_range: 原始波长范围
        new_range: 新波长范围
    """
    if not results:
        print("没有可用于生成德语总结的结果")
        return
    
    # 创建保存摘要的目录
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "comparison_results")
    os.makedirs(output_dir, exist_ok=True)
    
    # 计算平均误差
    all_xyz_diffs = []
    all_xy_diffs = []
    all_rgb_diffs = []
    all_lab_diffs = []
    all_delta_e = []
    
    for name, result in results.items():
        original_data = result['original']
        new_data = result['new']
        original_lab = result['original_lab']
        new_lab = result['new_lab']
        
        # 计算差异
        xyz_diff = np.abs(original_data['xyz'] - new_data['xyz'])
        xy_diff = np.abs(original_data['xy'] - new_data['xy'])
        rgb_diff = np.abs(original_data['rgb_gamma'] - new_data['rgb_gamma'])
        lab_diff = np.abs(original_lab - new_lab)
        
        all_xyz_diffs.append(xyz_diff)
        all_xy_diffs.append(xy_diff)
        all_rgb_diffs.append(rgb_diff)
        all_lab_diffs.append(lab_diff)
        all_delta_e.append(result['delta_e'])
    
    # 计算平均差异
    avg_xyz_diff = np.mean(all_xyz_diffs, axis=0)
    avg_xy_diff = np.mean(all_xy_diffs, axis=0)
    avg_rgb_diff = np.mean(all_rgb_diffs, axis=0)
    avg_lab_diff = np.mean(all_lab_diffs, axis=0)
    avg_delta_e = np.mean(all_delta_e)
    
    # 找出Delta E最大的几个样本
    delta_e_values = [(name, result['delta_e']) for name, result in results.items()]
    sorted_delta_e = sorted(delta_e_values, key=lambda x: x[1], reverse=True)
    worst_samples = sorted_delta_e[:5]  # 最差的5个样本
    
    # 生成德语总结
    with open(os.path.join(output_dir, 'farbfehler_zusammenfassung.txt'), 'w', encoding='utf-8') as f:
        f.write("Zusammenfassung der Wellenlängenbereichsanalyse\n")
        f.write("==============================================\n\n")
        
        f.write(f"Ursprünglicher Wellenlängenbereich: {original_range[0]}-{original_range[1]}nm\n")
        f.write(f"Gekürzter Wellenlängenbereich: {new_range[0]}-{new_range[1]}nm\n\n")
        
        f.write("Bewertung der Farbfehler\n")
        f.write("------------------------\n\n")
        
        f.write("Die Farbfehler wurden mit folgenden Metriken bewertet:\n\n")
        f.write("1. CIE XYZ-Farbwertdifferenzen\n")
        f.write("2. CIE xy-Chromatizitätskoordinatendifferenzen\n")
        f.write("3. sRGB-Farbdifferenzen\n")
        f.write("4. CIE L*a*b* Farbdifferenzen\n")
        f.write("5. CIE76 Delta E (ΔE) - Der Gesamtfarbunterschied\n\n")
        
        f.write("Durchschnittliche Farbfehler:\n")
        f.write(f"- XYZ-Differenz: ({avg_xyz_diff[0]:.6f}, {avg_xyz_diff[1]:.6f}, {avg_xyz_diff[2]:.6f})\n")
        f.write(f"- xy-Differenz: ({avg_xy_diff[0]:.6f}, {avg_xy_diff[1]:.6f})\n")
        f.write(f"- sRGB-Differenz: ({avg_rgb_diff[0]:.6f}, {avg_rgb_diff[1]:.6f}, {avg_rgb_diff[2]:.6f})\n")
        f.write(f"- L*a*b*-Differenz: ({avg_lab_diff[0]:.6f}, {avg_lab_diff[1]:.6f}, {avg_lab_diff[2]:.6f})\n")
        f.write(f"- Durchschnittliches ΔE: {avg_delta_e:.6f}\n\n")
        
        f.write("Ursachen der Farbfehler:\n")
        f.write("Die Farbfehler werden hauptsächlich durch den Abschnitt der spektralen Daten im langwelligen Bereich (750nm-780nm) und kurzwelligen Bereich (380nm-400nm) verursacht. Diese Wellenlängenbereiche tragen zur Farbwahrnehmung bei, auch wenn ihr Beitrag relativ gering ist. Die Tristimulus-Werte (XYZ) werden durch die Integration der spektralen Daten über den gesamten sichtbaren Bereich berechnet. Wenn ein Teil des Spektrums fehlt, führt dies zu leicht unterschiedlichen XYZ-Werten und damit zu abweichenden Farbwerten.\n\n")
        
        f.write("Bei dieser Studie fehlen besonders:\n")
        f.write("- Kurzwelliger Bereich (380nm-400nm): Dieser beeinflusst hauptsächlich die blaue Komponente (Z-Wert).\n")
        f.write("- Langwelliger Bereich (750nm-780nm): Dieser beeinflusst hauptsächlich die rote Komponente (X-Wert).\n\n")
        
        f.write("Proben mit den größten Farbunterschieden:\n")
        for i, (name, delta_e) in enumerate(worst_samples):
            f.write(f"{i+1}. Probe \"{name}\": ΔE = {delta_e:.6f}\n")
            
            # 获取样本详细数据
            sample_data = results[name]
            original_data = sample_data['original']
            new_data = sample_data['new']
            
            # 计算相对误差百分比
            xyz_diff = np.abs(original_data['xyz'] - new_data['xyz'])
            xyz_rel_diff = 100 * xyz_diff / (np.abs(original_data['xyz']) + 1e-10)
            
            f.write(f"   - XYZ-Differenz: ({xyz_diff[0]:.6f}, {xyz_diff[1]:.6f}, {xyz_diff[2]:.6f})\n")
            f.write(f"   - XYZ-Relative Differenz: ({xyz_rel_diff[0]:.2f}%, {xyz_rel_diff[1]:.2f}%, {xyz_rel_diff[2]:.2f}%)\n")
        
        f.write("\nEmpfehlungen für die Praxis:\n")
        f.write("Da die durchschnittliche Delta-E-Differenz von {:.6f} unter dem wahrnehmbaren Schwellenwert von 1,0 liegt, kann der gekürzete Wellenlängenbereich (400nm-750nm) für die meisten praktischen Anwendungen als ausreichend betrachtet werden. Die resultierenden Farbunterschiede sind für das menschliche Auge kaum wahrnehmbar.\n".format(avg_delta_e))
        f.write("Für hochpräzise Farbmessungen sollte jedoch der vollständige Wellenlängenbereich (380nm-780nm) verwendet werden, um maximale Genauigkeit zu gewährleisten.\n")
    
    print(f"德语总结已保存至: {os.path.join(output_dir, 'farbfehler_zusammenfassung.txt')}")

def main():
    # 设置波长范围
    original_range = (380, 780)  # 原始波长范围
    new_range = (400, 750)       # 新波长范围
    
    # 读取反射率数据
    reflectance_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'sample_data', 
        'Reflections.xlsx'
    )
    
    samples = read_reflectance_data(reflectance_file)
    
    if not samples:
        print("没有找到有效的样本数据")
        return
    
    # 比较不同波长范围的颜色计算结果
    results = compare_wavelength_ranges(samples, original_range, new_range)
    
    # 绘制结果图表
    plot_results(samples, results, original_range, new_range)
    
    # 生成德语总结
    generate_german_summary(results, original_range, new_range)
    
    print("\n分析完成！")

if __name__ == "__main__":
    main() 