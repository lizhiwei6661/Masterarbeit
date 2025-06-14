# Dependency Setup Script for Aleksameter Windows Build
# This script checks and installs required dependencies

param(
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"

Write-Host "🔧 Aleksameter Windows Dependencies Setup" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host ""

# Function to check if a command exists
function Test-CommandExists {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to download and install Python
function Install-Python {
    Write-Host "📥 Installing Python..." -ForegroundColor Yellow
    
    $pythonUrl = "https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe"
    $pythonInstaller = "$env:TEMP\python-installer.exe"
    
    try {
        Write-Host "   Downloading Python installer..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller -UseBasicParsing
        
        Write-Host "   Running Python installer..." -ForegroundColor Cyan
        Write-Host "   Please follow the installation prompts and make sure to check 'Add Python to PATH'" -ForegroundColor Yellow
        
        Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_test=0" -Wait
        
        Remove-Item $pythonInstaller -Force
        
        Write-Host "✅ Python installation completed!" -ForegroundColor Green
        Write-Host "⚠️  Please restart your PowerShell session and run this script again." -ForegroundColor Yellow
        
        return $false # Need to restart
    }
    catch {
        Write-Host "❌ Failed to install Python" -ForegroundColor Red
        Write-Host "   Please manually install Python from https://www.python.org/" -ForegroundColor Yellow
        return $false
    }
}

# Check Python installation
Write-Host "🔍 Checking Python installation..." -ForegroundColor Cyan

if (Test-CommandExists "python") {
    try {
        $pythonVersion = & python --version 2>&1
        if ($pythonVersion -match "Python (\d+\.\d+\.\d+)") {
            Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
            $pythonInstalled = $true
        } else {
            Write-Host "⚠️  Python command exists but version check failed" -ForegroundColor Yellow
            $pythonInstalled = $false
        }
    }
    catch {
        Write-Host "⚠️  Python command exists but not working properly" -ForegroundColor Yellow
        $pythonInstalled = $false
    }
} else {
    Write-Host "❌ Python not found" -ForegroundColor Red
    $pythonInstalled = $false
}

# Install Python if needed
if (-not $pythonInstalled -or $Force) {
    $install = Read-Host "Would you like to install Python automatically? (y/n)"
    if ($install -eq "y" -or $install -eq "Y") {
        $needRestart = Install-Python
        if ($needRestart -eq $false) {
            Write-Host "Please restart PowerShell and run this script again." -ForegroundColor Yellow
            exit 0
        }
    } else {
        Write-Host "Please install Python manually from https://www.python.org/" -ForegroundColor Yellow
        Write-Host "Make sure to add Python to PATH during installation." -ForegroundColor Yellow
        exit 1
    }
}

# Check pip
Write-Host "🔍 Checking pip..." -ForegroundColor Cyan
try {
    $pipVersion = & python -m pip --version 2>&1
    Write-Host "✅ Pip found: $pipVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Pip not working properly" -ForegroundColor Red
    Write-Host "   Trying to install pip..." -ForegroundColor Yellow
    try {
        & python -m ensurepip --upgrade
        Write-Host "✅ Pip installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to install pip" -ForegroundColor Red
        exit 1
    }
}

# Check and install PyInstaller
Write-Host "🔍 Checking PyInstaller..." -ForegroundColor Cyan

try {
    $pyinstallerVersion = & python -m PyInstaller --version 2>&1
    if ($pyinstallerVersion -match "\d+\.\d+") {
        Write-Host "✅ PyInstaller found: $pyinstallerVersion" -ForegroundColor Green
        $pyinstallerInstalled = $true
    } else {
        $pyinstallerInstalled = $false
    }
}
catch {
    $pyinstallerInstalled = $false
}

if (-not $pyinstallerInstalled -or $Force) {
    Write-Host "📦 Installing PyInstaller..." -ForegroundColor Yellow
    try {
        & python -m pip install pyinstaller
        Write-Host "✅ PyInstaller installed successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to install PyInstaller" -ForegroundColor Red
        exit 1
    }
}

# Check other required packages
Write-Host "🔍 Checking other dependencies..." -ForegroundColor Cyan

$requiredPackages = @("matplotlib", "numpy", "tkinter")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    try {
        & python -c "import $package" 2>$null
        Write-Host "✅ $package is available" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  $package not found" -ForegroundColor Yellow
        $missingPackages += $package
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "📦 Installing missing packages..." -ForegroundColor Yellow
    foreach ($package in $missingPackages) {
        try {
            if ($package -eq "tkinter") {
                # tkinter is usually included with Python, so we'll skip it
                Write-Host "   Skipping tkinter (should be included with Python)" -ForegroundColor Cyan
                continue
            }
            Write-Host "   Installing $package..." -ForegroundColor Cyan
            & python -m pip install $package
            Write-Host "✅ $package installed" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ Failed to install $package" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "🎉 Dependency setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
try {
    $pythonVer = & python --version 2>&1
    Write-Host "   ✅ Python: $pythonVer" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python: Not available" -ForegroundColor Red
}

try {
    $pipVer = & python -m pip --version 2>&1
    Write-Host "   ✅ Pip: $pipVer" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Pip: Not available" -ForegroundColor Red
}

try {
    $pyinstallerVer = & python -m PyInstaller --version 2>&1
    Write-Host "   ✅ PyInstaller: $pyinstallerVer" -ForegroundColor Green
} catch {
    Write-Host "   ❌ PyInstaller: Not available" -ForegroundColor Red
}
Write-Host ""
Write-Host "🚀 You can now run the build script:" -ForegroundColor Yellow
Write-Host "   .\build_windows.bat" -ForegroundColor Cyan
Write-Host "   or" -ForegroundColor Gray
Write-Host "   .\build_and_package_windows.ps1" -ForegroundColor Cyan 