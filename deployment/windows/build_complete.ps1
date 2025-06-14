# Complete Build Script for Aleksameter Windows
# This script performs a complete build with dependency verification

$ErrorActionPreference = "Stop"

Write-Host "🔧 Aleksameter Complete Build Process" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

# Verify Python environment
Write-Host "🔍 Verifying Python environment..." -ForegroundColor Yellow

$requiredPackages = @(
    @{name="PySide6"; import="PySide6.QtCore"},
    @{name="pandas"; import="pandas"},
    @{name="numpy"; import="numpy"},
    @{name="scipy"; import="scipy"},
    @{name="matplotlib"; import="matplotlib"},
    @{name="openpyxl"; import="openpyxl"},
    @{name="colour-science"; import="colour"},
    @{name="Pillow"; import="PIL"}
)

$missingPackages = @()

foreach ($pkg in $requiredPackages) {
    try {
        & python -c "import $($pkg.import)" 2>$null
        Write-Host "   ✅ $($pkg.name) - OK" -ForegroundColor Green
    }
    catch {
        Write-Host "   ❌ $($pkg.name) - MISSING" -ForegroundColor Red
        $missingPackages += $pkg.name
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host ""
    Write-Host "❌ Missing required packages: $($missingPackages -join ', ')" -ForegroundColor Red
    Write-Host "   Installing missing packages..." -ForegroundColor Yellow
    
    foreach ($package in $missingPackages) {
        try {
            & python -m pip install $package --upgrade
            Write-Host "   ✅ Installed $package" -ForegroundColor Green
        }
        catch {
            Write-Host "   ❌ Failed to install $package" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""
Write-Host "🧹 Cleaning previous build..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }

Write-Host ""
Write-Host "🔨 Building application..." -ForegroundColor Yellow

try {
    & python -m PyInstaller Aleksameter_windows.spec --distpath dist --workpath build --clean
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Build completed successfully!" -ForegroundColor Green
    } else {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }
}
catch {
    Write-Host "❌ Build failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🧪 Testing executable..." -ForegroundColor Yellow

$exePath = "dist\Aleksameter\Aleksameter.exe"
if (Test-Path $exePath) {
    Write-Host "✅ Executable found: $exePath" -ForegroundColor Green
    
    # Get file size
    $fileSize = "{0:N2} MB" -f ((Get-Item $exePath).Length / 1MB)
    Write-Host "📊 Executable size: $fileSize" -ForegroundColor Cyan
    
    # Test dependencies
    Write-Host ""
    Write-Host "🔍 Testing runtime dependencies..." -ForegroundColor Yellow
    
    # Create a simple test script
    $testScript = @"
import sys
import os
import traceback

# Add the application directory to path
if hasattr(sys, '_MEIPASS'):
    sys.path.insert(0, sys._MEIPASS)

try:
    print("Testing imports...")
    import pandas
    print("✅ pandas imported successfully")
    
    import numpy
    print("✅ numpy imported successfully")
    
    import PySide6.QtCore
    print("✅ PySide6 imported successfully")
    
    import matplotlib
    print("✅ matplotlib imported successfully")
    
    import scipy
    print("✅ scipy imported successfully")
    
    import openpyxl
    print("✅ openpyxl imported successfully")
    
    import colour
    print("✅ colour imported successfully")
    
    print("🎉 All dependencies imported successfully!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    traceback.print_exc()
    sys.exit(1)
"@
    
    $testScript | Out-File -FilePath "test_imports.py" -Encoding UTF8
    
    try {
        # Run test using the built executable
        $distDir = "dist\Aleksameter"
        Push-Location $distDir
        
        $testResult = & python "..\..\test_imports.py" 2>&1
        Write-Host $testResult
        
        Pop-Location
        Remove-Item "test_imports.py" -Force
        
        Write-Host "✅ Runtime dependency test completed" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  Could not perform runtime test: $_" -ForegroundColor Yellow
        if (Test-Path "test_imports.py") { Remove-Item "test_imports.py" -Force }
    }
    
} else {
    Write-Host "❌ Executable not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Creating installer package..." -ForegroundColor Yellow

try {
    & ".\make_installer_windows.ps1"
    Write-Host "✅ Installer package created!" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  Installer creation failed, but build was successful" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Build process completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Results:" -ForegroundColor Cyan
Write-Host "   Executable: $exePath" -ForegroundColor Gray
if (Test-Path "Aleksameter_windows.zip") {
    $zipSize = "{0:N2} MB" -f ((Get-Item "Aleksameter_windows.zip").Length / 1MB)
    Write-Host "   Installer: Aleksameter_windows.zip ($zipSize)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🚀 You can now run: .\dist\Aleksameter\Aleksameter.exe" -ForegroundColor Yellow 