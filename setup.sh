#!/bin/bash
# Claude API 负载测试环境初始化脚本

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "==============================================="
echo "Claude API 负载测试工具 - 环境初始化"
echo "==============================================="
echo ""

# 检查Python版本
echo "检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3，请先安装 Python 3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python 版本: $PYTHON_VERSION"

# 创建虚拟环境
echo ""
echo "创建虚拟环境..."
if [ -d "venv" ]; then
    echo "⚠ venv 已存在，是否重新创建? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "✓ 虚拟环境已重新创建"
    else
        echo "跳过创建虚拟环境"
    fi
else
    python3 -m venv venv
    echo "✓ 虚拟环境创建成功"
fi

# 激活虚拟环境并安装依赖
echo ""
echo "安装依赖包..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

if [ $? -eq 0 ]; then
    echo "✓ 依赖包安装成功"
else
    echo "✗ 依赖包安装失败"
    exit 1
fi

# 检查安装的包
echo ""
echo "已安装的包:"
pip list | grep -E "(aiohttp|Package)"

deactivate

# 设置脚本执行权限
chmod +x test.sh
chmod +x setup.sh

echo ""
echo "==============================================="
echo "环境初始化完成！"
echo "==============================================="
echo ""
echo "使用方法:"
echo "  查看帮助: ./test.sh --help"
echo "  运行测试: ./test.sh -e <endpoint> -k <api-key>"
echo ""
echo "快速开始:"
echo "  # 测试本地端点"
echo "  ./test.sh --preset local"
echo ""
echo "  # 测试xapi端点"
echo "  ./test.sh --preset xapi"
echo ""
echo "  # 自定义测试"
echo "  ./test.sh -e \"https://api.example.com/v1/messages\" -k \"sk-xxxxx\" -c 50 -n 100"
echo ""
