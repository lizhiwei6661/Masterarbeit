# Windows Defender False Positive Fix Script
# This script helps resolve false positive detections for PyInstaller executables

$ErrorActionPreference = "Stop"

Write-Host "🛡️ Windows Defender False Positive Fix" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  This script requires administrator privileges for some operations." -ForegroundColor Yellow
    Write-Host "   Some operations may not work without admin rights." -ForegroundColor Yellow
    Write-Host ""
}

# Get current directory and dist path
$currentDir = Get-Location
$distPath = Join-Path $currentDir "dist"
$exePath = Join-Path $distPath "Aleksameter\Aleksameter.exe"

Write-Host "📁 Current build directory: $currentDir" -ForegroundColor Cyan
Write-Host "📁 Executable path: $exePath" -ForegroundColor Cyan
Write-Host ""

# Method 1: Add exclusion for the entire build directory
Write-Host "🔧 Method 1: Add Windows Defender Exclusions" -ForegroundColor Yellow
Write-Host ""

if ($isAdmin) {
    try {
        Write-Host "   Adding exclusion for build directory..." -ForegroundColor Cyan
        Add-MpPreference -ExclusionPath $currentDir
        Write-Host "   ✅ Added exclusion for: $currentDir" -ForegroundColor Green
        
        Write-Host "   Adding exclusion for dist directory..." -ForegroundColor Cyan
        Add-MpPreference -ExclusionPath $distPath
        Write-Host "   ✅ Added exclusion for: $distPath" -ForegroundColor Green
        
        if (Test-Path $exePath) {
            Write-Host "   Adding exclusion for executable..." -ForegroundColor Cyan
            Add-MpPreference -ExclusionPath $exePath
            Write-Host "   ✅ Added exclusion for: $exePath" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "   ❌ Failed to add exclusions: $_" -ForegroundColor Red
        Write-Host "   Try running as administrator." -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠️  Administrator rights required for automatic exclusions." -ForegroundColor Yellow
    Write-Host "   Manual steps:" -ForegroundColor Cyan
    Write-Host "   1. Open Windows Security" -ForegroundColor Gray
    Write-Host "   2. Go to Virus & threat protection" -ForegroundColor Gray
    Write-Host "   3. Manage settings under Virus & threat protection settings" -ForegroundColor Gray
    Write-Host "   4. Add exclusions" -ForegroundColor Gray
    Write-Host "   5. Add folder exclusion for: $currentDir" -ForegroundColor Gray
}

Write-Host ""

# Method 2: Submit file to Microsoft for analysis
Write-Host "🔧 Method 2: Submit to Microsoft for Analysis" -ForegroundColor Yellow
Write-Host ""
Write-Host "   If the file continues to be flagged, you can submit it to Microsoft:" -ForegroundColor Cyan
Write-Host "   1. Go to: https://www.microsoft.com/wdsi/filesubmission" -ForegroundColor Gray
Write-Host "   2. Upload the file: $exePath" -ForegroundColor Gray
Write-Host "   3. Select 'I believe this file is safe'" -ForegroundColor Gray
Write-Host "   4. Provide details about the application" -ForegroundColor Gray
Write-Host ""

# Method 3: Temporarily disable real-time protection
Write-Host "🔧 Method 3: Temporarily Disable Real-time Protection" -ForegroundColor Yellow
Write-Host ""

if ($isAdmin) {
    $choice = Read-Host "   Do you want to temporarily disable Windows Defender real-time protection? (y/n)"
    if ($choice -eq "y" -or $choice -eq "Y") {
        try {
            Write-Host "   Disabling real-time protection..." -ForegroundColor Cyan
            Set-MpPreference -DisableRealtimeMonitoring $true
            Write-Host "   ✅ Real-time protection disabled" -ForegroundColor Green
            Write-Host "   ⚠️  Remember to re-enable it later!" -ForegroundColor Yellow
            
            Write-Host ""
            Write-Host "   To re-enable protection, run:" -ForegroundColor Cyan
            Write-Host "   Set-MpPreference -DisableRealtimeMonitoring `$false" -ForegroundColor Gray
        }
        catch {
            Write-Host "   ❌ Failed to disable real-time protection: $_" -ForegroundColor Red
        }
    }
} else {
    Write-Host "   ⚠️  Administrator rights required to disable real-time protection." -ForegroundColor Yellow
}

Write-Host ""

# Method 4: Alternative build options
Write-Host "🔧 Method 4: Alternative Build Options" -ForegroundColor Yellow
Write-Host ""
Write-Host "   For future builds, consider these options to reduce false positives:" -ForegroundColor Cyan
Write-Host "   1. Use --onedir instead of --onefile (already doing this)" -ForegroundColor Gray
Write-Host "   2. Exclude unnecessary libraries in .spec file" -ForegroundColor Gray
Write-Host "   3. Use UPX compression: --upx-dir=<path>" -ForegroundColor Gray
Write-Host "   4. Code signing certificate (for commercial distribution)" -ForegroundColor Gray
Write-Host ""

# Check current Windows Defender status
Write-Host "📊 Current Windows Defender Status:" -ForegroundColor Cyan
try {
    $defenderStatus = Get-MpComputerStatus
    Write-Host "   Real-time Protection: $($defenderStatus.RealTimeProtectionEnabled)" -ForegroundColor Gray
    Write-Host "   Antimalware Service: $($defenderStatus.AMServiceEnabled)" -ForegroundColor Gray
} catch {
    Write-Host "   Unable to retrieve Windows Defender status" -ForegroundColor Yellow
}

Write-Host ""

# Final instructions
Write-Host "🎯 Next Steps:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Try running your application again" -ForegroundColor Cyan
Write-Host "2. If still blocked, manually add exclusions in Windows Security" -ForegroundColor Cyan
Write-Host "3. For distribution, consider code signing or alternative packaging" -ForegroundColor Cyan
Write-Host ""

# Test if executable exists and can be run
if (Test-Path $exePath) {
    Write-Host "🧪 Testing executable..." -ForegroundColor Yellow
    $testChoice = Read-Host "   Do you want to test run the executable now? (y/n)"
    if ($testChoice -eq "y" -or $testChoice -eq "Y") {
        try {
            Write-Host "   Attempting to run: $exePath" -ForegroundColor Cyan
            Start-Process -FilePath $exePath -NoNewWindow
            Write-Host "   ✅ Executable started successfully!" -ForegroundColor Green
        }
        catch {
            Write-Host "   ❌ Failed to run executable: $_" -ForegroundColor Red
        }
    }
} else {
    Write-Host "⚠️  Executable not found at: $exePath" -ForegroundColor Yellow
    Write-Host "   Make sure the build completed successfully." -ForegroundColor Gray
}

Write-Host ""
Write-Host "💡 Tip: This is a common issue with PyInstaller. The false positive doesn't mean" -ForegroundColor Gray
Write-Host "     your application is malicious - it's just how antivirus software works." -ForegroundColor Gray 