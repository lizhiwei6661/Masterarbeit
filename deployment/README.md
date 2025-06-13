# Aleksameter Deployment

This directory contains platform-specific deployment scripts and configuration files for building and packaging Aleksameter across different operating systems.

## Directory Structure

```
deployment/
├── macos/                          # macOS deployment files
│   ├── Aleksameter_mac_arm64.spec  # PyInstaller spec for macOS ARM64
│   ├── make_dmg_arm64.sh          # DMG creation script
│   └── build_and_package_macos.sh # Complete build & package script
├── windows/                        # Windows deployment files (future)
│   └── (Windows-specific files)
└── linux/                          # Linux deployment files (future)
    └── (Linux-specific files)
```

## Usage

### macOS (Current)

#### Option 1: Complete Build & Package (Recommended)
```bash
cd deployment/macos
./build_and_package_macos.sh
```

#### Option 2: Step by Step
```bash
# From project root
pyinstaller deployment/macos/Aleksameter_mac_arm64.spec

# Create DMG
cd deployment/macos
./make_dmg_arm64.sh
```

### Future Platforms

#### Windows
- Plan to add `.spec` file for Windows
- Plan to add NSIS installer script or similar
- Plan to add complete build script

#### Linux
- Plan to add `.spec` file for Linux
- Plan to add AppImage/DEB/RPM packaging scripts
- Plan to add complete build script

## Output Files

- **macOS**: `Aleksameter_mac_arm64.dmg` (created in project root)
- **Windows**: `Aleksameter_windows_x64.exe` (planned)
- **Linux**: `Aleksameter_linux_x64.AppImage` (planned)

## Benefits of This Structure

1. **Clean Organization**: Each platform has its own directory
2. **Scalability**: Easy to add new platforms
3. **Maintainability**: Platform-specific issues are isolated
4. **Professional**: Industry standard deployment organization
5. **CI/CD Ready**: Easy to integrate with automated build systems

## Notes

- All deployment scripts should be run from their respective directories
- Generated applications and installers are placed in the project root
- Each platform directory is self-contained with all necessary files 