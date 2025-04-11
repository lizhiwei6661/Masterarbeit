from setuptools import setup
import os

# 列出实际存在的文件
def filter_existing_files(file_list):
    return [f for f in file_list if os.path.exists(f)]

# 必要的文件
base_files = [
    'xyzBar.csv',
    'stdIllum.csv',
    'ui_Settings.py',
    'ui_Import.py',
    'ui_plot_dialog.py',
    'ui_export_dialog.py',
    'app_settings.json',
]

# 过滤出实际存在的文件
existing_files = filter_existing_files(base_files)
print(f"Found existing files: {existing_files}")

# 如果data目录存在，添加为数据目录
data_files = []
if os.path.exists('data'):
    data_files.append(('data', [os.path.join('data', f) for f in os.listdir('data') if os.path.isfile(os.path.join('data', f))]))

APP = ['app.py']
DATA_FILES = existing_files

OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'CFBundleName': 'Aleksameter',
        'CFBundleDisplayName': 'Aleksameter',
        'CFBundleGetInfoString': 'Aleksameter reflectance tool',
        'CFBundleIdentifier': 'org.aleksa.aleksameter',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2024 All rights reserved.',
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': True,
    },
    'packages': [
        'PySide6',
        'numpy',
        'scipy', 
        'matplotlib',
        'pandas',
    ],
    'includes': [
        'color_calculator',
        'mainwindow',
        'settings_dialog',
        'import_dialog',
        'plot_dialog',
        'export_dialog',
    ],
    'excludes': [
        'PyInstaller',
        'black',
        'tkinter',
        'unittest',
        'email',
        'pydoc',
        'doctest',
        'test',
        'tests',
        '_testing',
        'Cython',
        'pytz.zoneinfo',
        'numpy.random.tests',
        'numpy.testing',
        'numpy.tests',
        'scipy.testing',
        'scipy.tests',
        'matplotlib.testing',
        'matplotlib.tests',
        'pandas.tests',
        'Matlab_Input',
    ],
    # 优化选项
    'optimize': 2,  # 应用Python优化器
    'compressed': True,  # 压缩字节码
    'strip': True,  # 删除符号表
    # 指定仅包含必要的图像格式
    'matplotlib.backends': ['PySide6Agg', 'PySide6Cairo', 'Agg', 'Cairo'],
    'includes_plugins': ['matplotlib.backends.backend_qt5agg'],
    'semi_standalone': False,  # 全独立应用程序
    'site_packages': True,  # 使用site-packages
    'arch': 'universal2',  # 编译为通用二进制(同时支持Intel和Apple Silicon)
}

setup(
    name='Aleksameter',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 