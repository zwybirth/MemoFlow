#!/usr/bin/env python3
"""
MemoFlow 自动恢复模块
在OpenClaw Gateway启动时自动加载
"""

import os
import sys
from pathlib import Path

# MemoFlow 自动恢复配置
MEMOFLOW_CONFIG = {
    "enabled": True,
    "auto_save": True,
    "auto_recall": True,
    "version": "3.2",
}

def initialize_memoflow():
    """
    初始化MemoFlow系统
    在Gateway启动时调用
    """
    memoflow_home = Path.home() / ".openclaw/workspace/pythontools"
    
    # 添加到Python路径
    if str(memoflow_home) not in sys.path:
        sys.path.insert(0, str(memoflow_home))
    
    try:
        # 导入核心模块
        from memoflow_auto import MemoFlowAuto
        from memoflow_assistant import MemoFlowAssistant
        
        # 初始化全局实例
        global memoflow_auto, memoflow_assistant
        memoflow_auto = MemoFlowAuto()
        memoflow_assistant = MemoFlowAssistant()
        
        # 设置环境变量
        os.environ["MEMOFLOW_AUTO"] = "1"
        os.environ["MEMOFLOW_INITIALIZED"] = "1"
        
        print("🌊 MemoFlow Auto 已自动加载")
        print("   自动保存: ✅ 已启用")
        print("   自动检索: ✅ 已启用")
        
        return True
        
    except Exception as e:
        print(f"⚠️  MemoFlow 初始化失败: {e}")
        return False

def get_memoflow_context(user_message=""):
    """
    获取MemoFlow上下文
    在每次对话前调用，提供相关记忆
    """
    if os.environ.get("MEMOFLOW_INITIALIZED") != "1":
        return ""
    
    try:
        # 检索相关记忆
        context = memoflow_assistant.get_context_for_prompt(user_message)
        return context
    except:
        return ""

def process_user_input(user_message):
    """
    处理用户输入
    自动保存和检索
    """
    if os.environ.get("MEMOFLOW_INITIALIZED") != "1":
        return None
    
    try:
        result = memoflow_assistant.on_user_message(user_message)
        return result
    except Exception as e:
        print(f"⚠️  MemoFlow 处理失败: {e}")
        return None

# Gateway启动时自动初始化
if __name__ == "__main__":
    initialize_memoflow()
