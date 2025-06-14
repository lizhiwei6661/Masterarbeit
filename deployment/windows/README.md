# Aleksameter Windows Build

Windows deployment tools for building and packaging the Aleksameter application.

## Quick Build

Run one of these commands:

```batch
# Simple batch build
build_windows.bat
```

```powershell
# Complete build with dependency checks
powershell -ExecutionPolicy Bypass -File "build_complete.ps1"
```

## Core Files

- `Aleksameter_windows.spec` - Build configuration (optimized, 605MB output)
- `build_complete.ps1` - Main build script with dependency verification
- `setup_dependencies.ps1` - Install Python and required packages
- `make_installer_windows.ps1` - Create ZIP installer
- `fix_windows_defender.ps1` - Fix antivirus false positives
- `build_windows.bat` - Simple batch launcher
- `dist/Aleksameter/` - Built application
- `Aleksameter_windows.zip` - Final installer (251MB)

## First Time Setup

```powershell
# Install dependencies
powershell -ExecutionPolicy Bypass -File "setup_dependencies.ps1"
```

## Windows Defender Issue

If Windows flags the executable as a virus (common with PyInstaller):

```powershell
# Run the fix script
powershell -ExecutionPolicy Bypass -File "fix_windows_defender.ps1"
```

**Or manually:**
1. Open Windows Security → Virus & threat protection
2. Add exclusion for the `dist/Aleksameter/` folder
3. The executable is safe - this is a false positive

## Requirements

- Windows 10/11 (64-bit)
- Python 3.11+
- Required packages: PySide6, pandas, numpy, scipy, matplotlib, openpyxl, colour-science, Pillow

## Build Results

- **Application**: ~605 MB (optimized from 800MB)
- **Executable**: ~20 MB
- **ZIP Installer**: ~251 MB
- **Build Time**: 3-5 minutes

## Troubleshooting

**Build fails:**
- Run `setup_dependencies.ps1` first
- Check Python version: `python --version`

**Missing modules:**
```powershell
python -c "import pandas, numpy, PySide6; print('Dependencies OK')"
```

**Antivirus interference:**
- Temporarily disable antivirus during build
- Use `fix_windows_defender.ps1` after build

## Installation for End Users

1. Extract `Aleksameter_windows.zip`
2. Run `Aleksameter.exe`
3. No additional installation needed 