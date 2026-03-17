#!/usr/bin/env python3
"""
MemoFlow Auto 集成脚本
在对话中自动保存和检索记忆

使用方法:
    1. 在对话开始时加载: source ~/.openclaw/workspace/pythontools/memoflow_auto_env.sh
    2. 每次用户发言后，AI自动调用保存
    3. AI自动根据上下文检索相关记忆
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".openclaw/workspace/pythontools"))

from memoflow_auto import MemoFlowAuto, process_user_message

class MemoFlowAssistant:
    """
    MemoFlow 智能助手集成
    
    用法:
        assistant = MemoFlowAssistant()
        
        # 用户发言后
        result = assistant.on_user_message("用户说的话")
        
        # 如果需要，AI可以主动提及相关记忆
        if result['recall_info']:
            print(f"根据之前的记忆...")
    """
    
    def __init__(self):
        self.autoflow = MemoFlowAuto()
        self.last_recall = None
    
    def on_user_message(self, message, context=None):
        """
        处理用户消息
        
        在每次用户发言后调用
        
        Returns:
            {
                'saved': bool,           # 是否已保存
                'save_info': {...},      # 保存详情
                'should_recall': bool,   # 是否建议主动回忆
                'recall_info': {...},    # 回忆详情
            }
        """
        result = process_user_message(message, context)
        
        # 格式化输出给AI参考
        output = {
            'saved': result['save_info'] is not None,
            'save_info': result['save_info'],
            'should_recall': result['recall_info'] is not None,
            'recall_info': result['recall_info'],
        }
        
        # 如果保存了，打印简要信息
        if output['saved']:
            info = output['save_info']
            print(f"\n💾 [MemoFlow Auto] 已自动保存记忆")
            print(f"   情绪: {info['emoji']} {info['emotion']}")
            print(f"   房间: {info['room']}")
        
        # 如果有相关记忆，打印提示
        if output['should_recall'] and output['recall_info']:
            recall = output['recall_info']
            print(f"\n🔍 [MemoFlow Auto] 发现 {recall['count']} 条相关记忆:")
            print(recall['formatted'])
            print()
        
        return output
    
    def on_assistant_response(self, response):
        """
        处理AI回复
        
        在AI回复后调用，可选保存重要回复
        """
        # 只保存重要的回复（包含决策、建议等）
        should_save, score, reason = self.autoflow.should_auto_save(response, role="assistant")
        
        if should_save and score >= 4:  # 门槛更高
            saved = self.autoflow.auto_save(response, role="assistant")
            if saved:
                print(f"\n💾 [MemoFlow Auto] 已保存AI回复")
    
    def proactive_recall(self, topic):
        """
        主动回忆某个主题
        
        AI可以主动调用，获取相关记忆
        """
        memories = self.autoflow.auto_recall(topic, max_results=3)
        
        if memories:
            formatted = self.autoflow.format_memory_for_dialog(memories)
            return formatted
        
        return None
    
    def get_context_for_prompt(self, user_message):
        """
        为AI生成prompt时获取上下文
        
        返回相关记忆，供AI参考
        """
        # 检索相关记忆
        memories = self.autoflow.auto_recall(user_message, max_results=3)
        
        if not memories:
            return ""
        
        context = "\n[相关记忆参考]\n"
        for i, mem in enumerate(memories, 1):
            time_str = mem.get("created_at", "")[5:16] if mem.get("created_at") else ""
            preview = mem.get("content", "")[:100]
            context += f"{i}. [{time_str}] {preview}...\n"
        
        return context

def main():
    """演示模式"""
    print("🌊 MemoFlow Auto 智能集成演示\n")
    print("=" * 60)
    
    assistant = MemoFlowAssistant()
    
    # 模拟对话
    conversations = [
        "你好",
        "我想继续优化BANK-AI项目",
        "上次我们讨论的记忆系统方案怎么样了？",
        "突然想到可以用自动保存的方式来改进",
    ]
    
    for msg in conversations:
        print(f"\n👤 用户: {msg}")
        result = assistant.on_user_message(msg)
        
        if result['should_recall']:
            print(f"🤖 AI可以参考这些记忆来回答")

if __name__ == "__main__":
    main()
