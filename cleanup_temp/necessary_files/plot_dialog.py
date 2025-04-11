import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QLineEdit, QPushButton, QFileDialog,
    QDialogButtonBox, QFormLayout, QCheckBox, QMessageBox,
    QSpinBox, QGroupBox
)
from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
from ui_plot_dialog import Ui_Dialog_plot


class PlotDialog(QDialog):
    def __init__(self, data, settings, parent=None):
        """
        初始化绘图对话框。
        
        参数:
            data: 要绘制的数据字典，包含以下键:
                - reflectance: 反射率数据
                - wavelengths: 波长数据
            settings: 应用程序设置
            parent: 父窗口
        """
        super().__init__(parent)
        self.setWindowTitle("Plot Export")
        self.resize(400, 300)
        
        # 存储数据和设置
        self.data = data
        self.settings = settings
        self.parent = parent
        
        # 初始化UI
        self.ui = Ui_Dialog_plot()
        self.ui.setupUi(self)
        
        # 设置默认文件名和路径
        default_dir = self.settings['export']['default_directory']
        default_filename = "plot.png"
        self.ui.lineEdit_Plot_File.setText(os.path.join(default_dir, default_filename))
        
        # 设置默认分辨率 - 不再从settings中获取，使用固定值
        self.ui.comboBox_Plot_Resolution.setCurrentIndex(1)  # 默认使用300 dpi (good)
        
        # 连接浏览按钮的信号
        self.ui.pushButton_Plot_Browse.clicked.connect(self.browse_file)
        
        # 连接确认按钮的信号
        self.ui.buttonBox.accepted.connect(self.on_accepted)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        # 确保至少选择一种图表
        self.ui.checkBox_Plot_Reflectance.stateChanged.connect(self.check_selection)
        self.ui.checkBox_Plot_CIE.stateChanged.connect(self.check_selection)
    
    def check_selection(self):
        """确保至少选择一种图表类型"""
        if not self.ui.checkBox_Plot_Reflectance.isChecked() and not self.ui.checkBox_Plot_CIE.isChecked():
            # 如果两个复选框都未选中，禁用确定按钮
            self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Ok).setEnabled(False)
        else:
            # 如果至少选中一个，启用确定按钮
            self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Ok).setEnabled(True)
    
    def browse_file(self):
        """浏览并选择导出文件路径"""
        current_path = self.ui.lineEdit_Plot_File.text()
        current_dir = os.path.dirname(current_path) if current_path else self.settings['export']['default_directory']
        
        # 获取当前选择的文件格式
        format_idx = self.ui.comboBox_Plot_Format.currentIndex()
        if format_idx == 0:
            filter_text = "PNG 文件 (*.png)"
            ext = ".png"
        elif format_idx == 1:
            filter_text = "JPEG 文件 (*.jpg)"
            ext = ".jpg"
        elif format_idx == 2:
            filter_text = "TIFF 文件 (*.tif)"
            ext = ".tif"
        else:
            filter_text = "PDF 文件 (*.pdf)"
            ext = ".pdf"
        
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "导出图表",
            os.path.join(current_dir, f"plot{ext}"),
            filter_text
        )
        
        if file_path:
            self.ui.lineEdit_Plot_File.setText(file_path)
    
    def on_accepted(self):
        """用户点击确定按钮时的处理"""
        export_reflectance = self.ui.checkBox_Plot_Reflectance.isChecked()
        export_cie = self.ui.checkBox_Plot_CIE.isChecked()
        
        if not export_reflectance and not export_cie:
            QMessageBox.warning(self, "导出错误", "请至少选择一种图表类型进行导出")
            return
        
        file_path = self.ui.lineEdit_Plot_File.text()
        if not file_path:
            QMessageBox.warning(self, "导出错误", "请指定导出文件路径")
            return
        
        # 获取当前选择的文件格式
        format_idx = self.ui.comboBox_Plot_Format.currentIndex()
        
        # 确保有正确的扩展名
        if format_idx == 0 and not file_path.lower().endswith('.png'):
            file_path += '.png'
        elif format_idx == 1 and not file_path.lower().endswith('.jpg'):
            file_path += '.jpg'
        elif format_idx == 2 and not file_path.lower().endswith('.tif'):
            file_path += '.tif'
        elif format_idx == 3 and not file_path.lower().endswith('.pdf'):
            file_path += '.pdf'
        
        # 获取文件名（不含扩展名）和目录
        file_dir = os.path.dirname(file_path)
        file_name_base = os.path.splitext(os.path.basename(file_path))[0]
        file_ext = os.path.splitext(file_path)[1]
        
        # 获取DPI设置 - 从下拉框选择获取对应的DPI值
        resolution_idx = self.ui.comboBox_Plot_Resolution.currentIndex()
        if resolution_idx == 0:
            dpi = 150  # draft
        elif resolution_idx == 1:
            dpi = 300  # good
        else:
            dpi = 600  # best
        
        success = True
        exported_files = []

        try:
            # 导出反射率图表
            if export_reflectance and hasattr(self.parent, 'reflectance_figure'):
                reflectance_file_path = os.path.join(file_dir, f"{file_name_base}_reflectance{file_ext}")
                
                # 获取设置中的反射率图表尺寸
                width_px = self.settings['plot'].get('reflectance_width', 800)
                height_px = self.settings['plot'].get('reflectance_height', 600)
                
                # 计算英寸尺寸
                width_inches = width_px / dpi
                height_inches = height_px / dpi
                
                print(f"导出反射率图表: {width_px}x{height_px}px ({width_inches:.2f}x{height_inches:.2f}英寸), DPI={dpi}")
                
                # 获取原始图表
                orig_fig = self.parent.reflectance_figure
                
                # 保存当前尺寸以便稍后恢复
                orig_size = orig_fig.get_size_inches()
                orig_dpi = orig_fig.dpi
                
                try:
                    # 先更新图表，以确保应用最新的设置
                    self.parent.update_reflectance_plot()
                    
                    # 临时调整图表尺寸
                    orig_fig.set_size_inches(width_inches, height_inches)
                    orig_fig.set_dpi(dpi)
                    
                    # 调整图表布局，确保图例等元素也按比例缩放
                    orig_fig.tight_layout(pad=1.1)  # 增加一点填充以确保元素不会被裁剪
                    
                    # 强制重新绘制以更新所有元素
                    orig_fig.canvas.draw()
                    
                    # 保存图表
                    orig_fig.savefig(
                        reflectance_file_path, 
                        dpi=dpi, 
                        bbox_inches='tight',
                        pad_inches=0.1  # 确保边缘有足够空间
                    )
                    
                    exported_files.append(reflectance_file_path)
                    print(f"反射率图表已导出到: {reflectance_file_path}")
                    
                finally:
                    # 恢复原始尺寸和DPI
                    orig_fig.set_size_inches(orig_size)
                    orig_fig.set_dpi(orig_dpi)
                    # 恢复原始布局
                    orig_fig.tight_layout()
                    orig_fig.canvas.draw()
            
            # 导出CIE色度图
            if export_cie and hasattr(self.parent, 'cie_figure'):
                cie_file_path = os.path.join(file_dir, f"{file_name_base}_cie{file_ext}")
                
                # 获取设置中的CIE图表尺寸
                width_px = self.settings['plot'].get('cie_width', 600)
                height_px = self.settings['plot'].get('cie_height', 600)
                
                # 计算英寸尺寸
                width_inches = width_px / dpi
                height_inches = height_px / dpi
                
                print(f"导出CIE图表: {width_px}x{height_px}px ({width_inches:.2f}x{height_inches:.2f}英寸), DPI={dpi}")
                
                # 获取原始图表
                orig_fig = self.parent.cie_figure
                
                # 保存当前尺寸以便稍后恢复
                orig_size = orig_fig.get_size_inches()
                orig_dpi = orig_fig.dpi
                
                try:
                    # 先更新图表，以确保应用最新的设置
                    self.parent.update_cie_plot()
                    
                    # 临时调整图表尺寸
                    orig_fig.set_size_inches(width_inches, height_inches)
                    orig_fig.set_dpi(dpi)
                    
                    # 调整图表布局，确保图例等元素也按比例缩放
                    orig_fig.tight_layout(pad=1.1)  # 增加一点填充以确保元素不会被裁剪
                    
                    # 强制重新绘制以更新所有元素
                    orig_fig.canvas.draw()
                    
                    # 保存图表
                    orig_fig.savefig(
                        cie_file_path, 
                        dpi=dpi, 
                        bbox_inches='tight',
                        pad_inches=0.1  # 确保边缘有足够空间
                    )
                    
                    exported_files.append(cie_file_path)
                    print(f"CIE色度图已导出到: {cie_file_path}")
                    
                finally:
                    # 恢复原始尺寸和DPI
                    orig_fig.set_size_inches(orig_size)
                    orig_fig.set_dpi(orig_dpi)
                    # 恢复原始布局
                    orig_fig.tight_layout()
                    orig_fig.canvas.draw()
            
            # 如果导出成功
            if success and exported_files:
                # 保存导出目录到设置
                self.settings['export']['default_directory'] = file_dir
                # 不再保存DPI到settings
                if self.parent:
                    self.parent.save_settings()
                
                # 显示成功消息
                QMessageBox.information(self, "成功", f"图表已成功导出至：\n" + "\n".join(exported_files))
                
                # 关闭对话框
                super().accept()
            else:
                QMessageBox.warning(self, "导出错误", "导出过程中发生错误")
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出图表失败: {e}")
            print(f"导出图表失败: {e}")
            import traceback
            traceback.print_exc() 