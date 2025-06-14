# ZIP Installer Creation Script for Aleksameter Windows
# Simple version that creates a ZIP package with installation instructions

# Stop script on any error
$ErrorActionPreference = "Stop"

# Configuration
$APP_NAME = "Aleksameter"
$BUILD_DIR = ".\dist\"
$ZIP_NAME = "${APP_NAME}_windows.zip"
$TEMP_DIR = "installer_temp"
$README_FILE = "README_Installation.txt"

Write-Host "📦 Creating ZIP installer for $APP_NAME..." -ForegroundColor Green

# Check if the built app exists
$appPath = Join-Path $BUILD_DIR $APP_NAME
if (-not (Test-Path $appPath)) {
    Write-Host "❌ Error: $APP_NAME folder not found in $BUILD_DIR" -ForegroundColor Red
    Write-Host "   Please build the application first using PyInstaller" -ForegroundColor Red
    exit 1
}

# Clean up any existing files
Write-Host "🧹 Cleaning up existing files..." -ForegroundColor Yellow
if (Test-Path $ZIP_NAME) { Remove-Item $ZIP_NAME -Force }
if (Test-Path $TEMP_DIR) { Remove-Item $TEMP_DIR -Recurse -Force }

# Create temporary directory for installer contents
Write-Host "📁 Creating temporary directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $TEMP_DIR | Out-Null

# Copy the application to temp directory
Write-Host "📋 Copying application..." -ForegroundColor Yellow
Copy-Item -Path $appPath -Destination $TEMP_DIR -Recurse -Force

# Create installation README
Write-Host "📝 Creating installation instructions..." -ForegroundColor Yellow
$readmeContent = @"
=== Aleksameter Windows Installation Guide ===

Thank you for downloading Aleksameter!

🔧 Installation Steps:
1. Extract this ZIP file to your desired directory (e.g., C:\Program Files\Aleksameter or C:\Users\[Your Username]\Desktop\Aleksameter)
2. Navigate to the extracted Aleksameter folder
3. Double-click Aleksameter.exe to run the program

📋 System Requirements:
- Windows 10 or higher
- No additional Python or dependency installation required

🚀 Quick Setup:
- Create desktop shortcut: Right-click Aleksameter.exe → Send to → Desktop (create shortcut)
- Add to Start Menu: Drag Aleksameter.exe to Start Menu

⚠️ Important Notes:
- On first run, Windows may show a security warning, please select "Run anyway"
- If you encounter issues, ensure all files are in the same directory
- Do not move Aleksameter.exe file alone; keep the entire folder structure intact

📧 Support:
If you encounter any issues, please contact the developer or check the user manual.

Version: Windows Edition
Build Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@

$readmeContent | Out-File -FilePath (Join-Path $TEMP_DIR $README_FILE) -Encoding UTF8

# Create ZIP archive
Write-Host "🗄️ Creating ZIP archive..." -ForegroundColor Yellow
try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($TEMP_DIR, $ZIP_NAME)
}
catch {
    # Fallback to PowerShell 5.0+ Compress-Archive if available
    try {
        Compress-Archive -Path "$TEMP_DIR\*" -DestinationPath $ZIP_NAME -Force
    }
    catch {
        Write-Host "❌ Failed to create ZIP archive: $_" -ForegroundColor Red
        exit 1
    }
}

# Clean up temporary files
Write-Host "🧹 Cleaning up temporary files..." -ForegroundColor Yellow
Remove-Item $TEMP_DIR -Recurse -Force

# Show results
if (Test-Path $ZIP_NAME) {
    $zipSize = "{0:N2} MB" -f ((Get-Item $ZIP_NAME).Length / 1MB)
    Write-Host "✅ ZIP installer created successfully!" -ForegroundColor Green
    Write-Host "📁 Location: $(Get-Location)\$ZIP_NAME" -ForegroundColor Cyan
    Write-Host "📊 Size: $zipSize" -ForegroundColor Cyan
    
    # Show contents
    Write-Host "📦 ZIP Contents:" -ForegroundColor Cyan
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $zip = [System.IO.Compression.ZipFile]::OpenRead((Resolve-Path $ZIP_NAME))
        $zip.Entries | ForEach-Object { Write-Host "   - $($_.FullName)" -ForegroundColor Gray }
        $zip.Dispose()
    }
    catch {
        Write-Host "   (Unable to list contents)" -ForegroundColor Gray
    }
} else {
    Write-Host "❌ ZIP creation failed!" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 Windows installer packaging completed!" -ForegroundColor Green 