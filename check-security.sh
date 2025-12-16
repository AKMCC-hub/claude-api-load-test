#!/bin/bash
# 自动化安全检查脚本

echo "============================================="
echo "Claude API Load Test - 安全检查"
echo "============================================="
echo ""

FAILED=0

echo "📋 检查 1: 扫描工作目录中的敏感信息..."
if grep -r "sk-O\|sk-s" . --exclude-dir=.git --exclude-dir=venv 2>/dev/null | grep -v "SECURITY_CHECKLIST" | grep -v "check-security.sh" | grep -v "your-api-key" | grep -v "sk-xxxxx"; then
    echo "❌ 在工作目录中发现疑似 API keys"
    FAILED=$((FAILED + 1))
else
    echo "✅ 工作目录干净"
fi
echo ""

echo "📋 检查 2: 验证 .gitignore 配置..."
if grep -q ".env" .gitignore && grep -q "config.local" .gitignore; then
    echo "✅ .gitignore 配置正确"
else
    echo "❌ .gitignore 缺少必要条目"
    FAILED=$((FAILED + 1))
fi
echo ""

echo "📋 检查 3: 检查 Git commit 历史..."
COMMIT_COUNT=$(git log --all --oneline | wc -l)
if [ "$COMMIT_COUNT" -le 2 ]; then
    echo "✅ Commit 历史干净（$COMMIT_COUNT 个提交）"
else
    echo "⚠️  发现 $COMMIT_COUNT 个 commits，建议手动检查"
fi
echo ""

echo "📋 检查 4: 扫描 Git 历史中的敏感字符串..."
if git log --all --source --full-history -S "sk-OiLukCezTb6F8a8FO2DricWlnWt3P1Qt4DjPdTY4lM2CwcpG" --oneline 2>/dev/null | grep -v "^$"; then
    echo "❌ 在 Git 历史中发现泄露的 API key"
    FAILED=$((FAILED + 1))
else
    echo "✅ Git 历史中未发现泄露的 local API key"
fi

if git log --all --source --full-history -S "sk-sJftjTuZKPixQcE7IQYmKd6xAqrWf9ai" --oneline 2>/dev/null | grep -v "^$"; then
    echo "❌ 在 Git 历史中发现泄露的 API key"
    FAILED=$((FAILED + 1))
else
    echo "✅ Git 历史中未发现泄露的 xapi API key"
fi
echo ""

echo "📋 检查 5: 验证环境变量功能..."
if grep -q "CLAUDE_API_KEY" test.sh; then
    echo "✅ test.sh 使用环境变量"
else
    echo "❌ test.sh 未使用环境变量"
    FAILED=$((FAILED + 1))
fi
echo ""

echo "📋 检查 6: 验证文档完整性..."
if [ -f "README.md" ] && [ -f "SECURITY_CHECKLIST.md" ]; then
    echo "✅ 安全文档完整"
else
    echo "❌ 缺少安全文档"
    FAILED=$((FAILED + 1))
fi
echo ""

echo "============================================="
if [ $FAILED -eq 0 ]; then
    echo "✅ 所有检查通过！"
    echo "============================================="
    exit 0
else
    echo "❌ $FAILED 项检查失败"
    echo "============================================="
    echo ""
    echo "建议操作:"
    echo "1. 查看 SECURITY_CHECKLIST.md 了解详细的安全措施"
    echo "2. 确保已撤销泄露的 API keys"
    echo "3. 使用环境变量管理新的 API keys"
    exit 1
fi
