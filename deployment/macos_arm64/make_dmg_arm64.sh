#!/bin/bash

# DMG Creation Script for Aleksameter macOS ARM64
# Simple version that creates a DMG with Applications folder

set -e  # Exit on any error

# Configuration
APP_NAME="Aleksameter"
BUILD_DIR="./dist/"
DMG_NAME="${APP_NAME}_mac_arm64.dmg"
TEMP_DIR="dmg_temp"

echo "📦 Creating DMG package for ${APP_NAME}..."

# Check if the built app exists
if [ ! -d "${BUILD_DIR}${APP_NAME}.app" ]; then
    echo "❌ Error: ${APP_NAME}.app not found in ${BUILD_DIR}"
    echo "   Please build the application first using PyInstaller"
    exit 1
fi

# Clean up any existing files
echo "🧹 Cleaning up existing files..."
rm -f "${DMG_NAME}"
rm -rf "${TEMP_DIR}"

# Create temporary directory for DMG contents
echo "📁 Creating temporary directory..."
mkdir -p "${TEMP_DIR}"

# Copy the app to temp directory
echo "📋 Copying application..."
cp -R "${BUILD_DIR}${APP_NAME}.app" "${TEMP_DIR}/"

# Create Applications symlink
echo "🔗 Creating Applications symlink..."
ln -s /Applications "${TEMP_DIR}/Applications"

# Create DMG
echo "🗄️ Creating DMG..."
hdiutil create -volname "${APP_NAME}" -srcfolder "${TEMP_DIR}" -ov -format UDZO "${DMG_NAME}"

# Clean up temporary files
echo "🧹 Cleaning up temporary files..."
rm -rf "${TEMP_DIR}"

# Show results
if [ -f "${DMG_NAME}" ]; then
    DMG_SIZE=$(du -sh "${DMG_NAME}" | cut -f1)
    echo "✅ DMG created successfully!"
    echo "📁 Location: $(pwd)/${DMG_NAME}"
    echo "📊 Size: ${DMG_SIZE}"
else
    echo "❌ DMG creation failed!"
    exit 1
fi

echo "🎉 DMG packaging completed!" 