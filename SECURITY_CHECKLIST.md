# 安全检查清单

## 🚨 紧急处理：API Keys 泄露事件

### 泄露的 API Keys

以下 API keys 曾被硬编码在代码中并推送到 GitHub：

```
sk-OiLukCez...lM2CwcpG  (本地端点 - 已部分遮蔽)
sk-sJftjTu...Wf9ai     (xapi端点 - 已部分遮蔽)
```

**完整keys已记录在密码管理器中**

**泄露时间：** 2025-12-16 13:57 (首次推送)
**修复时间：** 2025-12-16 14:05 (force push 覆盖)
**风险等级：** 🔴 高风险

---

## ✅ 立即行动清单

### 1. 撤销泄露的 API Keys

- [ ] **登录本地端点控制台** (http://172.96.160.168:3000)
  - [ ] 查找并撤销以 `sk-OiLukCez` 开头的泄露 API key
  - [ ] 撤销/删除该 key
  - [ ] 生成新的 API key
  - [ ] 记录新 key（使用密码管理器）

- [ ] **登录 xapi.aicoding.sh 控制台**
  - [ ] 查找并撤销以 `sk-sJftjTu` 开头的泄露 API key
  - [ ] 撤销/删除该 key
  - [ ] 生成新的 API key
  - [ ] 记录新 key（使用密码管理器）

### 2. 检查 API 使用记录

- [ ] **审计本地端点使用记录**
  - [ ] 检查从 2025-12-16 13:57 至今的所有 API 调用
  - [ ] 识别可疑的 IP 地址或请求模式
  - [ ] 查看是否有异常的使用量或成本增加

- [ ] **审计 xapi.aicoding.sh 使用记录**
  - [ ] 检查从 2025-12-16 13:57 至今的所有 API 调用
  - [ ] 识别可疑的 IP 地址或请求模式
  - [ ] 查看是否有异常的使用量或成本增加

### 3. 验证 GitHub 仓库安全性

- [ ] **检查 GitHub commit 历史**
  ```bash
  # 验证当前远程仓库不包含敏感信息
  git clone https://github.com/AKMCC-hub/claude-api-load-test.git /tmp/security-check
  cd /tmp/security-check
  git log --all --pretty=format: --name-only | sort -u
  grep -r "sk-" . --exclude-dir=.git
  ```

- [ ] **验证 GitHub 上的 commit 历史**
  - [ ] 访问 https://github.com/AKMCC-hub/claude-api-load-test/commits/master
  - [ ] 确认只有 1 个 commit (435d1eb)
  - [ ] 确认没有包含敏感信息的 commit

- [ ] **检查 GitHub 缓存**
  - [ ] 尝试访问旧的 commit (e422302) 是否还能通过浏览器访问
  - [ ] URL: https://github.com/AKMCC-hub/claude-api-load-test/commit/e422302
  - [ ] 如果仍可访问，联系 GitHub Support 请求清除缓存

### 4. 搜索引擎缓存检查

- [ ] **Google 搜索检查**
  ```
  site:github.com/AKMCC-hub/claude-api-load-test "sk-OiLukCez"
  site:github.com/AKMCC-hub/claude-api-load-test "sk-sJftjTu"
  ```
  - [ ] 如果找到结果，请求 Google 删除缓存

- [ ] **其他搜索引擎**
  - [ ] Bing
  - [ ] DuckDuckGo
  - [ ] Baidu（如果项目面向中国用户）

### 5. 监控可能的克隆者

- [ ] **检查 GitHub Insights**
  - [ ] 访问仓库的 Insights -> Traffic
  - [ ] 查看在泄露期间（13:57-14:05）是否有克隆或访问
  - [ ] 记录所有克隆者信息

---

## 🔒 代码安全验证

### 已完成的修复

- [x] 从 `test.sh` 中移除硬编码的 API keys
- [x] 改用环境变量 `CLAUDE_API_KEY`
- [x] 更新 README.md 添加安全说明
- [x] 添加 .gitignore 排除 .env 文件
- [x] Force push 覆盖 GitHub 历史
- [x] 清理本地 git reflog

### 本地验证

```bash
# 1. 检查工作目录
cd /Users/admin/linux.do/claude-load-test
grep -r "sk-O\|sk-s" . --exclude-dir=.git --exclude-dir=venv
# 预期输出: 无结果或仅示例文本

# 2. 检查 Git 历史
git log --all --source --full-history -- . | grep -i "sk-"
# 预期输出: 无结果

# 3. 验证 .gitignore
cat .gitignore | grep -E "(\.env|config\.local)"
# 预期输出: 包含这些条目

# 4. 测试环境变量功能
export CLAUDE_API_KEY="test-key-12345"
./test.sh --preset local --help
# 预期: 不应报错缺少 API key
```

### GitHub 远程验证

```bash
# 1. 克隆新副本验证
git clone https://github.com/AKMCC-hub/claude-api-load-test.git /tmp/verify-clean
cd /tmp/verify-clean

# 2. 扫描所有文件
find . -type f -not -path "./.git/*" -exec grep -l "sk-O\|sk-s" {} \;
# 预期输出: 无结果

# 3. 检查所有 commit
git log --all --oneline
# 预期输出: 只有一个 commit (435d1eb)

# 4. 搜索历史中的敏感字符串
git log -p --all -S "sk-OiLukCezTb6F8a8FO2DricWlnWt3P1Qt4DjPdTY4lM2CwcpG"
# 预期输出: 无结果
```

---

## 📋 后续防范措施

### 1. 设置 Git Hooks

创建 pre-commit hook 检测敏感信息：

```bash
# 在项目根目录执行
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook to prevent committing API keys

# 检测模式
PATTERNS=(
    "sk-[a-zA-Z0-9]{48}"           # Claude API keys
    "AKIA[0-9A-Z]{16}"             # AWS Access Keys
    "ghp_[a-zA-Z0-9]{36}"          # GitHub Personal Access Tokens
    "gho_[a-zA-Z0-9]{36}"          # GitHub OAuth Tokens
    "password\s*=\s*['\"][^'\"]+['\"]"  # Hardcoded passwords
)

echo "🔍 扫描敏感信息..."

for pattern in "${PATTERNS[@]}"; do
    if git diff --cached --diff-filter=d | grep -E "$pattern"; then
        echo "❌ 检测到可能的敏感信息！"
        echo "模式: $pattern"
        echo ""
        echo "请移除敏感信息后再提交。"
        exit 1
    fi
done

echo "✅ 未检测到敏感信息"
exit 0
EOF

chmod +x .git/hooks/pre-commit
```

### 2. 使用 Git Secrets 工具

- [ ] 安装 git-secrets
  ```bash
  # macOS
  brew install git-secrets

  # 配置仓库
  cd /Users/admin/linux.do/claude-load-test
  git secrets --install
  git secrets --register-aws
  git secrets --add 'sk-[a-zA-Z0-9]{48}'
  git secrets --add 'CLAUDE_API_KEY.*=.*["\'][^"\']+["\']'
  ```

### 3. 环境变量管理最佳实践

- [ ] **创建 .env.example 模板**
  ```bash
  # 创建示例文件
  cat > .env.example << 'EOF'
  # Claude API Key
  # 获取地址: https://console.anthropic.com/settings/keys
  CLAUDE_API_KEY=your-api-key-here

  # 可选: 自定义端点
  # CLAUDE_ENDPOINT=https://api.example.com/v1/messages
  EOF

  git add .env.example
  git commit -m "Add .env.example template"
  git push
  ```

- [ ] **更新 setup.sh 提示用户配置环境变量**

### 4. 定期安全扫描

- [ ] **设置 GitHub Secret Scanning**
  - 访问 https://github.com/AKMCC-hub/claude-api-load-test/settings/security_analysis
  - 启用 "Secret scanning"
  - 启用 "Push protection"

- [ ] **定期扫描**
  ```bash
  # 每周执行一次
  cd /Users/admin/linux.do/claude-load-test
  git log --all --source --full-history -S "sk-" --pretty=format:"%h %an %ad %s"
  ```

### 5. 文档更新

- [ ] 在 README.md 中添加安全章节链接
- [ ] 创建 SECURITY.md 安全政策文件
- [ ] 添加 CONTRIBUTING.md 提醒贡献者注意安全

---

## 🎯 长期安全措施

### 代码审查流程

- [ ] 所有 PR 必须经过安全审查
- [ ] 使用 GitHub Actions 自动扫描敏感信息
- [ ] 定期轮换 API keys（建议每 90 天）

### 访问控制

- [ ] 限制对生产环境 API keys 的访问
- [ ] 使用不同的 API keys 用于开发/测试/生产
- [ ] 记录所有 API key 的使用者和用途

### 监控和告警

- [ ] 设置 API 使用量告警
- [ ] 监控异常的地理位置访问
- [ ] 配置成本告警避免滥用

---

## 📞 紧急联系方式

### API 服务提供商

**aicoding.sh**
- 网站: https://aicoding.sh
- 支持: [填写支持联系方式]
- 紧急情况: [填写紧急联系方式]

### GitHub Support

- 提交请求: https://support.github.com
- 选择类别: Security & Abuse

---

## 📝 事件记录

### 事件时间线

| 时间 | 事件 | 操作者 |
|------|------|--------|
| 2025-12-16 13:53 | 创建项目目录 | Claude |
| 2025-12-16 13:55 | 创建 test.sh（包含硬编码keys） | Claude |
| 2025-12-16 13:57 | 首次推送到 GitHub | Claude |
| 2025-12-16 14:00 | 用户要求检查敏感信息 | User |
| 2025-12-16 14:02 | 发现 API keys 泄露 | Claude |
| 2025-12-16 14:03 | 修复代码移除硬编码 keys | Claude |
| 2025-12-16 14:05 | Force push 覆盖历史 | Claude |
| 2025-12-16 14:06 | 清理本地 reflog | Claude |

### 受影响范围

- **泄露时长**: 约 8 分钟（13:57 - 14:05）
- **GitHub commit**: e422302（已通过 force push 覆盖）
- **公开状态**: Public repository
- **已知访问**: 未知（需检查 GitHub Insights）

### 已采取的措施

1. ✅ 修改代码使用环境变量
2. ✅ Force push 覆盖 GitHub 历史
3. ✅ 清理本地 git reflog
4. ✅ 更新文档添加安全说明
5. ✅ 验证代码中无硬编码凭据
6. ⏳ 等待 API keys 撤销
7. ⏳ 监控 API 使用记录

---

## ✅ 验证完成确认

### Git 历史清理

- [ ] 本地仓库验证通过
- [ ] 远程仓库验证通过
- [ ] GitHub UI 确认历史干净
- [ ] 搜索引擎无缓存结果

### API Keys 管理

- [ ] 旧 keys 已撤销
- [ ] 新 keys 已生成
- [ ] 新 keys 存储在密码管理器
- [ ] 使用环境变量配置测试通过

### 监控设置

- [ ] GitHub Secret Scanning 已启用
- [ ] API 使用监控已配置
- [ ] 告警规则已设置
- [ ] Pre-commit hooks 已安装

---

## 📚 参考资源

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Git Secrets](https://github.com/awslabs/git-secrets)
- [TruffleHog: Find secrets in git](https://github.com/trufflesecurity/trufflehog)

---

**最后更新**: 2025-12-16
**责任人**: AKMCC-hub
**状态**: 🔴 待完成 - 需要撤销 API keys
