#!/bin/bash
# Claude API 负载测试启动脚本
# 用法: ./test.sh [选项]

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "错误: venv 不存在，请先运行 ./setup.sh"
    exit 1
fi

# 默认参数
ENDPOINT=""
API_KEY=""
CONCURRENCY=10
NUM_REQUESTS=100
MODEL="claude-sonnet-4-5-20250929"

# 显示帮助信息
show_help() {
    cat << EOF
Claude API 负载测试工具

用法:
  ./test.sh -e <endpoint> -k <api-key> [选项]

必需参数:
  -e, --endpoint <url>        API端点URL (例如: https://api.example.com/v1/messages)
  -k, --api-key <key>         API密钥

可选参数:
  -c, --concurrency <num>     并发数 (默认: 10)
  -n, --num-requests <num>    总请求数 (默认: 100)
  -m, --model <name>          模型名称 (默认: claude-sonnet-4-5-20250929)
  -h, --help                  显示此帮助信息

示例:
  # 基本测试 (10并发, 100请求)
  ./test.sh -e "https://api.example.com/v1/messages" -k "sk-xxxxx"

  # 高并发测试 (50并发, 500请求)
  ./test.sh -e "https://api.example.com/v1/messages" -k "sk-xxxxx" -c 50 -n 500

  # 指定模型
  ./test.sh -e "https://api.example.com/v1/messages" -k "sk-xxxxx" -m "claude-3-5-sonnet-20241022"

预设配置:
  # 测试本地端点
  ./test.sh --preset local

  # 测试xapi端点
  ./test.sh --preset xapi

EOF
}

# 预设配置
if [ "$1" = "--preset" ]; then
    case "$2" in
        local)
            ENDPOINT="http://172.96.160.168:3000/v1/messages"
            # API_KEY需要通过环境变量 CLAUDE_API_KEY 设置或使用 -k 参数
            if [ -z "$CLAUDE_API_KEY" ]; then
                echo "错误: 使用预设配置需要设置环境变量 CLAUDE_API_KEY"
                echo "示例: export CLAUDE_API_KEY='sk-xxxxx'"
                echo "或者: CLAUDE_API_KEY='sk-xxxxx' ./test.sh --preset local"
                exit 1
            fi
            API_KEY="$CLAUDE_API_KEY"
            shift 2
            ;;
        xapi)
            ENDPOINT="https://xapi.aicoding.sh/v1/messages"
            # API_KEY需要通过环境变量 CLAUDE_API_KEY 设置或使用 -k 参数
            if [ -z "$CLAUDE_API_KEY" ]; then
                echo "错误: 使用预设配置需要设置环境变量 CLAUDE_API_KEY"
                echo "示例: export CLAUDE_API_KEY='sk-xxxxx'"
                echo "或者: CLAUDE_API_KEY='sk-xxxxx' ./test.sh --preset xapi"
                exit 1
            fi
            API_KEY="$CLAUDE_API_KEY"
            shift 2
            ;;
        *)
            echo "未知的预设: $2"
            echo "可用预设: local, xapi"
            exit 1
            ;;
    esac
fi

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--endpoint)
            ENDPOINT="$2"
            shift 2
            ;;
        -k|--api-key)
            API_KEY="$2"
            shift 2
            ;;
        -c|--concurrency)
            CONCURRENCY="$2"
            shift 2
            ;;
        -n|--num-requests)
            NUM_REQUESTS="$2"
            shift 2
            ;;
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 验证必需参数
if [ -z "$ENDPOINT" ]; then
    echo "错误: 缺少必需参数 --endpoint"
    echo ""
    show_help
    exit 1
fi

if [ -z "$API_KEY" ]; then
    echo "错误: 缺少必需参数 --api-key"
    echo ""
    show_help
    exit 1
fi

# 运行测试
echo "正在启动 Claude API 负载测试..."
echo "==============================================="
echo "端点: $ENDPOINT"
echo "并发数: $CONCURRENCY"
echo "总请求数: $NUM_REQUESTS"
echo "模型: $MODEL"
echo "==============================================="
echo ""

python3 claude_load_test.py \
    -e "$ENDPOINT" \
    -k "$API_KEY" \
    -c "$CONCURRENCY" \
    -n "$NUM_REQUESTS" \
    -m "$MODEL"

# 退出虚拟环境
deactivate
