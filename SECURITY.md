# Security Policy

## 🔒 安全政策

我们非常重视 claude-api-load-test 项目的安全性。本文档描述了我们的安全政策、如何报告安全漏洞以及我们的安全最佳实践。

## 🚨 报告安全漏洞

如果您发现了安全漏洞，**请勿**通过公开的 GitHub Issues 报告。

### 报告渠道

请通过以下方式之一私密报告安全问题：

1. **GitHub Security Advisories**（推荐）
   - 访问 https://github.com/AKMCC-hub/claude-api-load-test/security/advisories
   - 点击 "New draft security advisory"
   - 填写详细信息

2. **私密邮件**
   - 发送至：[您的安全邮箱]
   - 邮件主题：[SECURITY] Claude API Load Test - [简短描述]

### 报告内容应包括

- 漏洞的详细描述
- 重现步骤
- 潜在影响
- 建议的修复方案（如果有）
- 您的联系方式

## 🛡️ 支持的版本

| 版本 | 支持状态 |
| --- | --- |
| Latest (master) | ✅ 支持 |
| Older versions | ❌ 不支持 |

我们仅对最新的 master 分支提供安全更新。

## 🔐 安全最佳实践

### 1. API Keys 管理

#### ❌ 永远不要这样做

```bash
# 硬编码 API key
API_KEY="sk-abc123def456..."

# 在命令行历史中暴露
./test.sh -k "sk-abc123def456..."
```

#### ✅ 正确的做法

```bash
# 使用环境变量
export CLAUDE_API_KEY="sk-abc123def456..."
./test.sh --preset local

# 或使用 .env 文件
echo 'export CLAUDE_API_KEY="sk-xxx"' > .env
source .env
```

### 2. .env 文件安全

```bash
# 确保 .env 在 .gitignore 中
echo ".env" >> .gitignore

# 设置正确的文件权限（仅所有者可读写）
chmod 600 .env

# 复制示例配置
cp .env.example .env
```

### 3. Git 安全

#### 安装 Pre-commit Hook

项目已包含 pre-commit hook，会自动检测敏感信息：

```bash
# Hook 已自动安装在 .git/hooks/pre-commit
# 测试 hook
git add .
git commit -m "test"  # 会自动运行安全检查
```

#### 检查历史记录

```bash
# 运行安全检查脚本
./check-security.sh

# 手动扫描历史
git log -p | grep -i "api.key\|password\|secret"
```

### 4. 定期安全审计

我们建议每 90 天进行以下操作：

- [ ] 轮换所有 API keys
- [ ] 审计 API 使用记录
- [ ] 检查 GitHub Security Advisories
- [ ] 更新依赖到最新版本
- [ ] 运行 `./check-security.sh`

### 5. 生产环境建议

#### 环境隔离

```bash
# 开发环境
export CLAUDE_API_KEY_DEV="sk-dev-xxx"

# 测试环境
export CLAUDE_API_KEY_TEST="sk-test-xxx"

# 生产环境
export CLAUDE_API_KEY_PROD="sk-prod-xxx"
```

#### 权限最小化

- 使用只读 API keys（如果可用）
- 限制 IP 白名单
- 设置使用量限制
- 启用审计日志

## 🔍 自动化安全检查

### GitHub Actions

项目配置了自动化安全扫描，在每次 push 时运行：

- 扫描硬编码的凭据
- 验证 .gitignore 配置
- 使用 Gitleaks 检测泄露的 secrets
- 生成安全报告

查看结果：https://github.com/AKMCC-hub/claude-api-load-test/actions

### 本地检查

```bash
# 运行完整安全检查
./check-security.sh

# 手动测试 pre-commit hook
.git/hooks/pre-commit
```

## 🚑 安全事件响应

如果发生 API key 泄露：

1. **立即撤销泄露的 keys**
2. **生成新的 keys**
3. **审计使用记录**（检查异常活动）
4. **评估影响范围**
5. **更新所有使用该 key 的系统**
6. **完成 SECURITY_CHECKLIST.md 中的所有项目**

详细的响应流程请参考 [SECURITY_CHECKLIST.md](./SECURITY_CHECKLIST.md)。

## 📚 相关资源

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [Git Secrets](https://github.com/awslabs/git-secrets)
- [Anthropic API Best Practices](https://docs.anthropic.com/claude/reference/api-best-practices)

## 📞 联系方式

- **安全问题**: 通过 GitHub Security Advisories 报告
- **一般问题**: 提交 GitHub Issue
- **项目维护者**: @AKMCC-hub

## 🆕 变更日志

| 日期 | 变更 |
|------|------|
| 2025-12-16 | 初始版本 - 添加安全政策和最佳实践 |

## 🙏 致谢

感谢所有报告安全问题和帮助改进项目安全性的贡献者。

---

**记住：安全是一个持续的过程，而不是一次性的任务。** 🛡️
