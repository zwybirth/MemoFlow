# 🌊 MemoFlow Auto 环境配置
# 添加到 ~/.zshrc 或 ~/.bashrc

# MemoFlow 基础
export MEMOFLOW_HOME="$HOME/.openclaw/workspace/pythontools"
export MEMOFLOW_PALACE="$HOME/Documents/claw_memory/palace"

# 添加到 PATH
export PATH="$MEMOFLOW_HOME:$PATH"

# 快捷命令
alias mem='python3 $MEMOFLOW_HOME/mem.py'
alias memflow='python3 $MEMOFLOW_HOME/memoflow.py'
alias memauto='python3 $MEMOFLOW_HOME/memoflow_auto.py'
alias memassist='python3 $MEMOFLOW_HOME/memoflow_assistant.py'

# 流动式快捷
alias flow-save='mem save --auto --content'
alias flow-search='mem search'
alias flow-status='mem stats'
alias flow-visual='mem palace --open'

# 自动模式（对话中使用）
alias mem-auto-on='export MEMOFLOW_AUTO=1 && echo "🌊 MemoFlow Auto 已启用"'
alias mem-auto-off='unset MEMOFLOW_AUTO && echo "🌊 MemoFlow Auto 已关闭"'

# 智能提示函数
memoflow_hint() {
    echo "🌊 MemoFlow 记忆流系统"
    echo ""
    echo "自动模式 (对话中自动保存和检索):"
    echo "  mem-auto-on    # 启用自动模式"
    echo "  mem-auto-off   # 关闭自动模式"
    echo ""
    echo "手动命令:"
    echo "  flow-save \"...\"      # 保存记忆"
    echo "  flow-search \"...\"    # 搜索记忆"
    echo "  flow-status          # 查看统计"
    echo "  flow-visual          # 可视化"
}

echo "🌊 MemoFlow Auto 智能记忆系统已加载"
echo "   输入 memoflow_hint 查看帮助"
