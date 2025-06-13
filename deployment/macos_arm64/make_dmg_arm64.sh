#!/bin/bash

# Set variables
APP_NAME="Aleksameter"
BUILD_DIR="../../dist/${APP_NAME}.app"
TEMP_DIR="/tmp/${APP_NAME}_dmg"
DMG_PATH="../../${APP_NAME}_mac_arm64.dmg"

# Ensure temp directory exists and is empty
rm -rf "${TEMP_DIR}"
mkdir -p "${TEMP_DIR}"

# Copy application to temp directory
cp -R "${BUILD_DIR}" "${TEMP_DIR}/"

# Create a symbolic link to /Applications in temp directory
ln -s /Applications "${TEMP_DIR}/Applications"

# Create DMG file
hdiutil create -volname "${APP_NAME}" -srcfolder "${TEMP_DIR}" -ov -format UDZO "${DMG_PATH}"

# Clean up temp directory
rm -rf "${TEMP_DIR}"

echo "DMG file created: ${DMG_PATH}" 