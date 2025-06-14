# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

# Only collect necessary data files
datas = [
    ('../../xyzBar.csv', '.'), 
    ('../../stdIllum.csv', '.'),
    ('../../font_settings.json', '.'),
    ('../../app_settings.json', '.'),
    ('../../default_settings.json', '.'),
    ('../../Aleksameter_User_Guide.html', '.'),
    ('../../app_icon.png', '.')
]

# Only add colour library data files
datas += collect_data_files('colour')

a = Analysis(
    ['../../app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # Only include necessary backends
        'matplotlib.backends.backend_pdf',
        'matplotlib.backends.backend_svg', 
        'matplotlib.backends.backend_ps',
        'matplotlib.backends.backend_agg',
        'matplotlib.backends.backend_tkagg',
        # PySide6 core modules
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtPrintSupport',
        'shiboken6',
        # Scientific computing library core modules
        'pandas',
        'numpy',
        'scipy',
        'scipy.interpolate',
        'scipy.special',
        'scipy.special._ufuncs_cxx',
        # Other required modules
        'openpyxl',
        'colour',
        'PIL',
        'json',
        'warnings',
        'unittest',
        'numpy.testing'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary GUI libraries
        'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets',
        'PyQt5',
        'tkinter',
        # Exclude test modules (but keep unittest as it's needed by scipy/numpy)
        'pandas.tests',
        'numpy.tests',
        'scipy.tests',
        'matplotlib.tests',
        'pytest',
        # Exclude other unnecessary modules
        'IPython',
        'jupyter',
        'notebook'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Aleksameter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX to avoid Windows Defender issues
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../../app_icon.png' if os.path.exists('../../app_icon.png') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # Disable UPX to avoid Windows Defender issues
    upx_exclude=[],
    name='Aleksameter',
) 