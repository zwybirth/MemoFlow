#!/bin/bash
#
# MemoFlow 快速检查脚本
# 验证持久化配置是否正确
#

echo "🌊 MemoFlow 持久化配置检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查1: 文件存在
echo -e "\n📁 文件检查:"
files=(
    "$HOME/.openclaw/workspace/pythontools/memoflow_daemon.sh"
    "$HOME/.openclaw/workspace/pythontools/memoflow_auto_env.sh"
    "$HOME/.zshrc"
    "$HOME/Library/LaunchAgents/com.openclaw.memoflow.plist"
)

for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  ✅ $(basename $file)"
    else
        echo "  ❌ $(basename $file) - 缺失"
    fi
done

# 检查2: 环境变量
echo -e "\n🌍 环境变量检查:"
if [[ -n "$MEMOFLOW_HOME" ]]; then
    echo "  ✅ MEMOFLOW_HOME: $MEMOFLOW_HOME"
else
    echo "  ⚠️  MEMOFLOW_HOME: 未设置 (需要新会话或source ~/.zshrc)"
fi

if [[ "$MEMOFLOW_AUTO" == "1" ]]; then
    echo "  ✅ MEMOFLOW_AUTO: $MEMOFLOW_AUTO"
else
    echo "  ⚠️  MEMOFLOW_AUTO: 未启用"
fi

# 检查3: 运行状态
echo -e "\n🚀 运行状态检查:"
PID_FILE="$HOME/.openclaw/memoflow.pid"
if [[ -f "$PID_FILE" ]]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "  ✅ MemoFlow 运行中 (PID: $PID)"
    else
        echo "  ❌ PID文件存在但进程未运行"
    fi
else
    echo "  ❌ MemoFlow 未运行 (无PID文件)"
fi

# 检查4: 数据状态
echo -e "\n📊 数据状态:"
if command -v claw &> /dev/null; then
    MEM_COUNT=$(claw stats 2>/dev/null | grep "总记忆数" | awk '{print $2}' || echo "0")
    echo "  📦 基础层记忆: $MEM_COUNT 条"
fi

PALACE_COUNT=$(find "$HOME/Documents/claw_memory/palace/rooms" -name "*.json" 2>/dev/null | wc -l)
echo "  🏛️ 宫殿层记忆: $PALACE_COUNT 条"

# 使用建议
echo -e "\n💡 快速修复:"
echo "  启动: ~/.openclaw/workspace/pythontools/memoflow_daemon.sh start"
echo "  停止: ~/.openclaw/workspace/pythontools/memoflow_daemon.sh stop"
echo "  状态: ~/.openclaw/workspace/pythontools/memoflow_daemon.sh status"
echo "  新会话: 开启新终端自动加载"

echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
