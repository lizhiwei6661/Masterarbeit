#!/bin/bash
# 清理脚本 - 删除所有不必要的文件

# 项目根目录
PROJECT_DIR="$HOME/Masterarbeit"
cd "$PROJECT_DIR"

# 删除所有测试文件
find . -name "test_*.py" -type f -delete
find . -name "test_*.xlsx" -type f -delete
find . -name "test_*.txt" -type f -delete

# 删除调试和转换脚本
find . -name "debug_*.py" -type f -delete
find . -name "debug_*.txt" -type f -delete
find . -name "convert_*.py" -type f -delete
find . -name "manual_*.py" -type f -delete
find . -name "compare*.py" -type f -delete

# 删除备份文件和不必要的文档
find . -name "*.bak" -type f -delete
find . -name "*.md" -type f -delete
find . -name "conclusion.txt" -type f -delete

# 删除导出的样例文件
find . -name "export_*.xlsx" -type f -delete

# 删除Matlab相关文件夹
rm -rf ./Matlab_Input

# 删除所有本地的测试输出
rm -rf ./dist
rm -rf ./build
rm -rf ./__pycache__
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -type f -delete
find . -name "*.pyo" -type f -delete

# 保留一个干净的备份
#mkdir -p clean_aleksameter
#cp -r cleanup_temp/necessary_files/* clean_aleksameter/

echo "完成清理！只保留了必要的文件。" 