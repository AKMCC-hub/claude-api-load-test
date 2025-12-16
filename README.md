# Claude API 负载测试工具

一个用于测试 Claude API 端点性能和稳定性的并发负载测试工具。

> **特别鸣谢：** 本项目测试环境由 [aicoding.sh](https://aicoding.sh) - 国内最真的 Claude 服务商倾情提供。

## 特性

- ✅ 支持高并发请求测试（可自定义并发数）
- ✅ 包含8种不同复杂度的测试消息（高Token压力测试）
- ✅ 详细的性能统计（成功率、QPS、响应时间分布、Token使用量）
- ✅ 错误类型分析
- ✅ 便捷的命令行工具和预设配置

## 快速开始

### 1. 初始化环境

```bash
./setup.sh
```

这将：
- 创建 Python 虚拟环境
- 安装所需依赖（aiohttp）
- 设置脚本执行权限

### 2. 运行测试

#### 使用预设配置

预设配置需要设置环境变量 `CLAUDE_API_KEY`：

```bash
# 方式1: 设置环境变量后使用预设
export CLAUDE_API_KEY='your-api-key-here'
./test.sh --preset local   # 测试本地端点
./test.sh --preset xapi     # 测试 xapi 端点

# 方式2: 临时环境变量
CLAUDE_API_KEY='your-api-key-here' ./test.sh --preset local
CLAUDE_API_KEY='your-api-key-here' ./test.sh --preset xapi
```

#### 自定义测试

```bash
# 基本测试 (10并发, 100请求)
./test.sh -e "https://api.example.com/v1/messages" -k "sk-xxxxx"

# 高并发测试 (50并发, 500请求)
./test.sh -e "https://api.example.com/v1/messages" -k "sk-xxxxx" -c 50 -n 500

# 完整参数
./test.sh \
  -e "https://api.example.com/v1/messages" \
  -k "sk-xxxxx" \
  -c 100 \
  -n 1000 \
  -m "claude-3-5-sonnet-20241022"
```

### 3. 查看帮助

```bash
./test.sh --help
```

## 命令行参数

### 必需参数

- `-e, --endpoint <url>` - API端点URL
- `-k, --api-key <key>` - API密钥

### 可选参数

- `-c, --concurrency <num>` - 并发数（默认：10）
- `-n, --num-requests <num>` - 总请求数（默认：100）
- `-m, --model <name>` - 模型名称（默认：claude-sonnet-4-5-20250929）
- `-h, --help` - 显示帮助信息

## 测试消息类型

脚本包含8种复杂度不同的测试消息：

1. **大型代码审查** - 审查完整的电商订单处理系统
2. **分布式系统设计** - 设计全球分布式限流系统
3. **复杂数据处理** - 处理嵌套JSON并执行多种分析
4. **算法优化** - 优化百万级日志处理系统
5. **数据库设计** - 设计社交平台数据库架构
6. **微服务架构** - 设计外卖平台完整架构
7. **安全审计** - 全面审计认证系统
8. **性能优化** - 优化慢查询和N+1问题

每个请求随机选择一个消息类型，模拟真实的复杂使用场景。

## 输出统计

测试完成后会显示：

### 总体统计
- 总请求数、成功数、失败数
- 成功率、失败率
- 总耗时、QPS（每秒请求数）

### Token 使用统计
- 输入 Tokens（总计 + 平均）
- 输出 Tokens（总计 + 平均）
- 总计 Tokens

### 响应时间统计
- 最小值、最大值、平均值
- P50、P90、P95、P99 百分位数

### 错误类型分布
- 详细的错误类型和出现次数

## 示例输出

```
============================================================
测试结果统计
============================================================

总体统计:
  总请求数: 100
  成功数: 99
  失败数: 1
  成功率: 99.00%
  失败率: 1.00%
  总耗时: 66.04s
  QPS: 1.51 req/s

Token 使用统计:
  输入 Tokens: 78,352 (平均: 784/请求)
  输出 Tokens: 204,800 (平均: 2048/请求)
  总计 Tokens: 283,152

响应时间统计:
  最小值: 21186.54ms
  最大值: 37481.76ms
  平均值: 28909.63ms
  P50: 29526.73ms
  P90: 34226.75ms
  P95: 34648.05ms
  P99: 37481.76ms

错误类型分布:
  [1次, 100.0%] Timeout (>60s)
```

## 目录结构

```
claude-load-test/
├── README.md                   # 使用文档
├── setup.sh                    # 环境初始化脚本
├── test.sh                     # 测试启动脚本
├── claude_load_test.py         # 核心测试脚本
├── requirements.txt            # Python依赖
└── venv/                       # Python虚拟环境（自动创建）
```

## 常见问题

### Q: 如何修改测试消息？

A: 编辑 `claude_load_test.py` 中的 `TEST_MESSAGES` 列表。

### Q: 如何添加新的预设配置？

A: 编辑 `test.sh`，在预设配置部分添加新的 case。

### Q: 超时时间是多少？

A: 默认每个请求超时时间为 60 秒，可以在 `claude_load_test.py` 中修改。

### Q: 可以测试简单消息吗？

A: 可以，修改 `TEST_MESSAGES` 为简单的文本即可，例如：
```python
TEST_MESSAGES = ["你好", "1+1等于几？", "介绍一下Claude"]
```

## 安全说明

**重要：** 请勿在代码中硬编码 API keys！

建议使用以下方式管理 API keys：

1. **环境变量**（推荐）
   ```bash
   export CLAUDE_API_KEY='your-api-key-here'
   ./test.sh --preset local
   ```

2. **命令行参数**
   ```bash
   ./test.sh -e "https://api.example.com/v1/messages" -k "your-api-key-here"
   ```

3. **.env 文件**（已在 .gitignore 中）
   ```bash
   # 创建 .env 文件
   echo 'export CLAUDE_API_KEY="your-api-key-here"' > .env
   source .env
   ./test.sh --preset local
   ```

## 系统要求

- Python 3.7+
- macOS / Linux / Windows (WSL)
- 网络连接

## 依赖

- aiohttp >= 3.9.0

## 许可

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
