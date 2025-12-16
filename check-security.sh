#!/bin/bash
# 自动化安全检查脚本

echo "============================================="
echo "Claude API Load Test - 安全检查"
echo "============================================="
echo ""

FAILED=0

echo "📋 检查 1: 扫描工作目录中的敏感信息..."
# 排除文档和脚本本身
if grep -r "sk-[a-zA-Z0-9]\{40,\}" . --exclude-dir=.git --exclude-dir=venv --exclude="*.md" --exclude="*.sh" 2>/dev/null; then
    echo "❌ 在工作目录中发现疑似完整 API keys"
    FAILED=$((FAILED + 1))
else
    echo "✅ 工作目录中未发现完整 API keys"
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
COMMIT_COUNT=$(git log --all --oneline | wc -l | tr -d ' ')
if [ "$COMMIT_COUNT" -le 10 ]; then
    echo "✅ Commit 历史正常（$COMMIT_COUNT 个提交）"
else
    echo "⚠️  发现 $COMMIT_COUNT 个 commits，建议手动检查历史"
fi
echo ""

echo "📋 检查 4: 验证环境变量功能..."
if grep -q "CLAUDE_API_KEY" test.sh && ! grep -E "API_KEY=\"sk-[a-zA-Z0-9]{40,}\"" test.sh; then
    echo "✅ test.sh 正确使用环境变量且无硬编码"
else
    echo "❌ test.sh 可能包含硬编码的 API keys"
    FAILED=$((FAILED + 1))
fi
echo ""

echo "📋 检查 5: 验证文档完整性..."
if [ -f "README.md" ] && [ -f "SECURITY_CHECKLIST.md" ]; then
    echo "✅ 安全文档完整"
else
    echo "❌ 缺少安全文档"
    FAILED=$((FAILED + 1))
fi
echo ""

echo "📋 检查 6: 扫描 Python 脚本..."
if grep -E "sk-[a-zA-Z0-9]{40,}" claude_load_test.py 2>/dev/null; then
    echo "❌ Python 脚本中发现疑似 API keys"
    FAILED=$((FAILED + 1))
else
    echo "✅ Python 脚本干净"
fi
echo ""

echo "============================================="
if [ $FAILED -eq 0 ]; then
    echo "✅ 所有检查通过！"
    echo "============================================="
    echo ""
    echo "🔒 安全建议:"
    echo "  1. 定期轮换 API keys（建议每90天）"
    echo "  2. 使用不同的 keys 用于开发/测试/生产环境"
    echo "  3. 启用 GitHub Secret Scanning"
    echo "  4. 定期审计 API 使用记录"
    echo ""
    exit 0
else
    echo "❌ $FAILED 项检查失败"
    echo "============================================="
    echo ""
    echo "建议操作:"
    echo "1. 查看 SECURITY_CHECKLIST.md 了解详细的安全措施"
    echo "2. 确保已撤销泄露的 API keys"
    echo "3. 使用环境变量管理新的 API keys"
    echo "4. 运行 git log -p 手动检查历史"
    exit 1
fi
