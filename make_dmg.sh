#!/bin/bash

# 设置变量
APP_NAME="Aleksameter"
DMG_NAME="${APP_NAME}_Installer"
DMG_DIR="./dmg_tmp"
APP_PATH="./dist/${APP_NAME}.app"
DMG_PATH="./dist/${DMG_NAME}.dmg"

# 确保临时目录存在并为空
rm -rf "${DMG_DIR}"
mkdir -p "${DMG_DIR}"

# 复制应用程序到临时目录
cp -R "${APP_PATH}" "${DMG_DIR}/"

# 在临时目录中创建一个指向/Applications的符号链接
ln -s /Applications "${DMG_DIR}/Applications"

# 创建DMG文件
hdiutil create -volname "${DMG_NAME}" -srcfolder "${DMG_DIR}" -ov -format UDZO "${DMG_PATH}"

# 清理临时目录
rm -rf "${DMG_DIR}"

echo "DMG文件已创建: ${DMG_PATH}" 