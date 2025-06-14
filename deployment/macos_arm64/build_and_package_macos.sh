#!/bin/bash

# macOS ARM64 Build and Package Script for Aleksameter
# This script builds the application and creates a DMG installer

set -e  # Exit on any error

echo "🍎 Starting macOS ARM64 build and package process..."

# Check if we're in the right directory
if [ ! -f "../../app.py" ]; then
    echo "❌ Error: Please run this script from the deployment/macos_arm64 directory"
    echo "   Current directory should contain ../../app.py"
    exit 1
fi

# Set variables
APP_NAME="Aleksameter"
PROJECT_ROOT="../../"
SPEC_FILE="Aleksameter_mac_arm64.spec"
DMG_SCRIPT="make_dmg_arm64.sh"

echo "📁 Project root: ${PROJECT_ROOT}"
echo "📋 Spec file: ${SPEC_FILE}"

# Step 1: Build the application with custom dist and work paths
echo "🔨 Building ${APP_NAME} application..."
cd "${PROJECT_ROOT}"
pyinstaller "deployment/macos_arm64/${SPEC_FILE}" --distpath "deployment/macos_arm64/dist" --workpath "deployment/macos_arm64/build"

if [ $? -eq 0 ]; then
    echo "✅ Application build successful!"
else
    echo "❌ Application build failed!"
    exit 1
fi

# Step 2: Create DMG package
echo "📦 Creating DMG package..."
cd "deployment/macos_arm64"
./"${DMG_SCRIPT}"

if [ $? -eq 0 ]; then
    echo "🎉 DMG package created successfully!"
    
    # Show results
    if [ -f "${APP_NAME}_mac_arm64.dmg" ]; then
        DMG_SIZE=$(du -sh "${APP_NAME}_mac_arm64.dmg" | cut -f1)
        echo "📁 DMG Location: $(pwd)/${APP_NAME}_mac_arm64.dmg"
        echo "📊 DMG Size: ${DMG_SIZE}"
    fi
else
    echo "❌ DMG creation failed!"
    exit 1
fi

echo "🎯 macOS deployment completed successfully!" 