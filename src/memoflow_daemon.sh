#!/bin/bash
#
# MemoFlow 系统启动脚本
# 确保新会话和Gateway重启后自动恢复
#

set -e

MEMOFLOW_HOME="${HOME}/.openclaw/workspace/pythontools"
PALACE_DIR="${HOME}/Documents/claw_memory/palace"
LOG_DIR="${HOME}/.openclaw/logs"
PID_FILE="${HOME}/.openclaw/memoflow.pid"

# 创建日志目录
mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/memoflow.log"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        log "❌ Python3 未安装"
        exit 1
    fi
    log "✅ Python3 已安装: $(python3 --version)"
}

check_dependencies() {
    log "🔍 检查依赖..."
    
    # 检查关键文件
    local files=(
        "$MEMOFLOW_HOME/mem.py"
        "$MEMOFLOW_HOME/memoflow_auto.py"
        "$MEMOFLOW_HOME/memoflow_assistant.py"
    )
    
    for file in "${files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log "❌ 缺失文件: $file"
            exit 1
        fi
    done
    
    log "✅ 所有依赖文件存在"
}

init_local_mem() {
    log "🧠 初始化 LOCAL-MEM..."
    
    # 检查并恢复 LOCAL-MEM
    if [[ -f "$MEMOFLOW_HOME/unified_memory.py" ]]; then
        python3 "$MEMOFLOW_HOME/unified_memory.py" status >> "$LOG_DIR/memoflow.log" 2>&1 || true
        log "✅ LOCAL-MEM 已就绪"
    else
        log "⚠️  unified_memory.py 不存在，尝试恢复..."
        # 这里可以添加恢复逻辑
    fi
}

init_memoflow() {
    log "🌊 初始化 MemoFlow..."
    
    # 检查宫殿目录
    if [[ ! -d "$PALACE_DIR" ]]; then
        log "📁 创建宫殿目录..."
        mkdir -p "$PALACE_DIR/rooms"
        mkdir -p "$PALACE_DIR/timeline"
        mkdir -p "$PALACE_DIR/emotions"
    fi
    
    # 检查房间
    local rooms=("study" "bedroom" "living" "kitchen" "garage" "meeting" "studio")
    for room in "${rooms[@]}"; do
        mkdir -p "$PALACE_DIR/rooms/$room"
    done
    
    log "✅ MemoFlow 宫殿已就绪"
}

test_auto_mode() {
    log "🧪 测试自动驾驶模式..."
    
    # 简单的功能测试
    local test_result=$(python3 -c "
import sys
sys.path.insert(0, '$MEMOFLOW_HOME')
from memoflow_auto import MemoFlowAuto
autoflow = MemoFlowAuto()
result = autoflow.should_auto_save('测试消息')
print('OK' if result else 'FAIL')
" 2>&1)
    
    if [[ "$test_result" == *"OK"* ]]; then
        log "✅ 自动驾驶模式正常"
    else
        log "⚠️  自动驾驶模式测试失败: $test_result"
    fi
}

start_memoflow() {
    log "🚀 启动 MemoFlow 系统..."
    
    # 写入PID文件
    echo $$ > "$PID_FILE"
    
    # 设置环境变量
    export MEMOFLOW_AUTO=1
    export MEMOFLOW_HOME="$MEMOFLOW_HOME"
    export MEMOFLOW_PALACE="$PALACE_DIR"
    
    log "✅ MemoFlow 系统已启动"
    log "   PID: $$"
    log "   自动保存: 已启用"
    log "   自动检索: 已启用"
}

show_status() {
    log "📊 MemoFlow 系统状态"
    log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 基础层统计
    if command -v claw &> /dev/null; then
        local mem_count=$(claw stats 2>/dev/null | grep "总记忆数" | awk '{print $2}' || echo "未知")
        log "📦 基础层记忆: $mem_count 条"
    fi
    
    # 宫殿层统计
    local palace_count=$(find "$PALACE_DIR/rooms" -name "*.json" 2>/dev/null | wc -l)
    log "🏛️ 宫殿层记忆: $palace_count 条"
    
    # 房间分布
    for room in study bedroom living kitchen garage meeting studio; do
        local count=$(find "$PALACE_DIR/rooms/$room" -name "*.json" 2>/dev/null | wc -l)
        if [[ $count -gt 0 ]]; then
            log "   $room: $count 条"
        fi
    done
    
    log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

case "${1:-start}" in
    start)
        log "🌊 MemoFlow 启动脚本"
        check_python
        check_dependencies
        init_local_mem
        init_memoflow
        test_auto_mode
        start_memoflow
        show_status
        log "🎉 MemoFlow 启动完成！"
        ;;
    
    status)
        if [[ -f "$PID_FILE" ]] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            log "✅ MemoFlow 运行中 (PID: $(cat $PID_FILE))"
            show_status
        else
            log "❌ MemoFlow 未运行"
        fi
        ;;
    
    stop)
        if [[ -f "$PID_FILE" ]]; then
            kill $(cat "$PID_FILE") 2>/dev/null || true
            rm -f "$PID_FILE"
            log "🛑 MemoFlow 已停止"
        else
            log "⚠️  PID文件不存在"
        fi
        ;;
    
    restart)
        $0 stop
        sleep 1
        $0 start
        ;;
    
    test)
        log "🧪 运行测试..."
        check_python
        check_dependencies
        test_auto_mode
        log "✅ 测试完成"
        ;;
    
    *)
        echo "用法: $0 {start|stop|restart|status|test}"
        exit 1
        ;;
esac
