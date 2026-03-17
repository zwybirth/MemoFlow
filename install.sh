#!/bin/bash
#
# MemoFlow 安装脚本
#

set -e

echo "🌊 MemoFlow 安装程序"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: Python3 未安装"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python版本: $PYTHON_VERSION"

# 创建目录
echo "📁 创建目录..."
MEMOFLOW_HOME="${HOME}/.memoflow"
mkdir -p "$MEMOFLOW_HOME"
mkdir -p "$MEMOFLOW_HOME/rooms"
mkdir -p "$MEMOFLOW_HOME/timeline"
mkdir -p "$MEMOFLOW_HOME/emotions"
mkdir -p "$HOME/Documents/memoflow"
mkdir -p "$HOME/.openclaw/logs"

# 复制文件
echo "📦 安装文件..."
cp -r src/* "$MEMOFLOW_HOME/"

# 设置权限
chmod +x "$MEMOFLOW_HOME/"*.sh
chmod +x "$MEMOFLOW_HOME/"*.py

# 添加到PATH
echo "🔧 配置环境..."
SHELL_RC=""
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [[ -n "$SHELL_RC" && -f "$SHELL_RC" ]]; then
    # 检查是否已配置
    if ! grep -q "MEMOFLOW_HOME" "$SHELL_RC"; then
        cat >> "$SHELL_RC" << EOF

# 🌊 MemoFlow 配置
export MEMOFLOW_HOME="$MEMOFLOW_HOME"
export MEMOFLOW_PALACE="$HOME/Documents/memoflow"
export MEMOFLOW_AUTO=1
export PATH="\$MEMOFLOW_HOME:\$PATH"
source "\$MEMOFLOW_HOME/memoflow_auto_env.sh" 2>/dev/null || true
echo "🌊 MemoFlow 已加载 (Auto Save: ON)"
EOF
        echo "✅ 已添加到 $SHELL_RC"
    else
        echo "⚠️  已配置，跳过"
    fi
fi

# macOS LaunchAgent
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 配置macOS LaunchAgent..."
    mkdir -p "$HOME/Library/LaunchAgents"
    
    cat > "$HOME/Library/LaunchAgents/com.openclaw.memoflow.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.memoflow</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>source ~/.zshrc && $MEMOFLOW_HOME/memoflow_daemon.sh start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF
    
    launchctl load "$HOME/Library/LaunchAgents/com.openclaw.memoflow.plist" 2>/dev/null || true
    echo "✅ LaunchAgent 已配置"
fi

# 测试
echo "🧪 运行测试..."
if "$MEMOFLOW_HOME/memoflow_daemon.sh" test > /dev/null 2>&1; then
    echo "✅ 测试通过"
else
    echo "⚠️  测试失败，请检查依赖"
fi

echo ""
echo "🎉 MemoFlow 安装完成！"
echo ""
echo "使用方法:"
echo "  1. 重启终端或运行: source $SHELL_RC"
echo "  2. 测试: memoflow_check.sh"
echo "  3. 保存: mem save --content '...' --auto"
echo "  4. 查看: mem stats"
echo ""
echo "文档: https://github.com/yourusername/MemoFlow"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
