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
    'Aleksameter_User_Guide.html',
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
        'PySide6',  # 包含完整的PySide6模块，不只是特定组件
        'numpy',
        'scipy',
        'matplotlib',  # 包含整个matplotlib包，而不只是figure模块
        'pandas',   # 添加pandas包
    ],
    'includes': [
        'color_calculator',
        'mainwindow',
        'settings_dialog',
        'import_dialog',
        'plot_dialog',
        'export_dialog',
        'cmath',  # 确保包含cmath标准库
        'math',   # 确保包含math标准库
        'matplotlib.pyplot',  # 确保包含matplotlib.pyplot
    ],
    'excludes': [
        # 基本排除
        'PyInstaller',
        'black',
        'tkinter',
        # 'unittest',  # unittest被numpy.testing间接需要，移除排除
        'doctest',
        'distutils',
        'setuptools',
        'pip',
        'lib2to3',
        # 'pandas',  # 我们需要pandas库，不排除它
        
        # 测试模块
        'test', 'tests', '_testing', 'testing',
        # 'numpy.testing', # 可能被numpy自身需要，移除排除
        'numpy.tests',
        'scipy.testing', 'scipy.tests',
        'matplotlib.testing', 'matplotlib.tests',
        'pandas.tests',
        
        # 不需要的大型模块 - 暂时注释掉，确保基本功能
        # 'scipy.io.matlab',
        # 'scipy.spatial',
        # 'scipy.stats',
        # 'scipy.optimize',
        # 'scipy.signal',
        # 'scipy.fft',
        # 'scipy.cluster',
        # 'scipy.sparse',
        # 'scipy.linalg',
        'pandas.io.excel',
        'pandas.io.formats.style',
        'pandas.io.clipboard',
        'pandas.io.parquet',
        'pandas.io.sas',
        'matplotlib.backends.web',
        'matplotlib.backends.qt_editor',
        
        # GUI组件
        # 以下是非必要的GUI组件，可以被排除：
        # 'PySide6.QtWebEngine',
        # 'PySide6.QtWebEngineCore',
        # 'PySide6.QtWebEngineWidgets',
        # 'PySide6.QtNetwork',
        # 'PySide6.QtQml',
        # 'PySide6.QtQuick',
        # 'PySide6.QtSql',
        # 'PySide6.QtDesigner',
        # 'PySide6.QtHelp',
        # 'PySide6.QtMultimedia',
        # 'PySide6.QtBluetooth',
        # 'PySide6.QtPositioning',
        # 'PySide6.QtOpenGL',
        # 'PySide6.QtTest',
        # 'PySide6.QtXml',
        # 'PySide6.Qt3DCore',
        # 'PySide6.Qt3DExtras',
        # 'PySide6.Qt3DInput',
        # 'PySide6.Qt3DLogic',
        # 'PySide6.Qt3DRender',
        
        # 其他
        'pytz.zoneinfo',
        'Cython',
        'IPython',
        'Matlab_Input',
    ],
    # 优化选项
    'optimize': 2,  # 应用Python优化器
    'compressed': True,  # 压缩字节码
    'strip': True,  # 删除符号表
    'arch': 'universal2',  # 编译为通用二进制(同时支持IntelandApple Silicon)
    'site_packages': True,  # 包含site-packages
    'no_chdir': True,  # 不切换到资源目录
    'semi_standalone': False,  # 不使用系统Python
    'dylib_excludes': ['libQt*'],  # 排除不需要的动态库
}

setup(
    name='Aleksameter',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 