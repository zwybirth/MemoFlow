#!/usr/bin/env python3
"""
MemoFlow Auto - 自动驾驶模式
自动保存 + 自动检索 + 主动回忆

功能：
1. 自动识别重要对话并保存
2. 对话中自动检索相关记忆
3. AI主动回忆和关联
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".openclaw/workspace/pythontools"))
sys.path.insert(0, str(Path.home() / ".openclaw/workspace/skills/emotional-memory"))

from auto_emotion import analyze_emotion, EMOTION_PATTERNS

class MemoFlowAuto:
    """MemoFlow 自动驾驶系统"""
    
    def __init__(self):
        self.palace_dir = Path.home() / "Documents/claw_memory/palace"
        self.auto_config = {
            "importance_keywords": [
                "想法", "思路", "方案", "设计", "计划", "决定", "确定",
                "问题", "解决", "突破", "完成", "实现", "发现", "明白",
                "重要", "关键", "核心", "顿悟", "突然", "新", "优化",
                "改进", "创新", "成功", "失败", "经验", "教训",
                "记住", "备忘", "记录", "存储", "保存",
                "项目名称", "BANK-AI", "决策", "拍板", "结论"
            ],
            "exclude_patterns": [
                r'^好的', r'^是的', r'^明白', r'^了解', r'^ok', r'^嗯',
                r'^谢谢', r'^再见', r'^拜拜', r'^哈哈', r'^呵呵',
            ],
            "min_length": 10,  # 最少10个字符才保存
            "max_length": 2000,  # 最多2000个字符
        }
    
    def should_auto_save(self, text, role="user"):
        """
        判断是否自动保存
        
        Args:
            text: 对话内容
            role: "user" 或 "assistant"
        
        Returns:
            (should_save, importance_score, reason)
        """
        # 长度检查
        if len(text) < self.auto_config["min_length"]:
            return False, 0, "太短"
        
        if len(text) > self.auto_config["max_length"]:
            return False, 0, "太长"
        
        # 排除闲聊
        for pattern in self.auto_config["exclude_patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                return False, 0, "闲聊模式"
        
        # 计算重要性分数
        importance_score = 0
        matched_keywords = []
        
        for keyword in self.auto_config["importance_keywords"]:
            if keyword in text:
                importance_score += 1
                matched_keywords.append(keyword)
        
        # 特殊标记
        if "memo:" in text.lower() or "记住" in text:
            importance_score += 5
        
        if "重要" in text or "关键" in text:
            importance_score += 3
        
        # 问题标记
        if "?" in text or "？" in text:
            importance_score += 1
        
        # 情绪强度
        emotion_result = analyze_emotion(text)
        emotion = emotion_result[0] if isinstance(emotion_result, tuple) else emotion_result
        if emotion in ["excited", "insight", "anxious"]:
            importance_score += 2
        
        # 决策阈值
        if importance_score >= 2:
            return True, importance_score, f"关键词: {', '.join(matched_keywords[:3])}"
        
        return False, importance_score, "重要性不足"
    
    def auto_save(self, text, role="user", context=None):
        """
        自动保存记忆
        
        Returns:
            保存结果或 None
        """
        should_save, score, reason = self.should_auto_save(text, role)
        
        if not should_save:
            return None
        
        # 智能分析
        emotion_result = analyze_emotion(text)
        emotion = emotion_result[0] if isinstance(emotion_result, tuple) else emotion_result
        intensity = emotion_result[1] if isinstance(emotion_result, tuple) and len(emotion_result) > 1 else 5
        
        # 生成标题
        title = self._generate_title(text, role)
        
        # 提取标签
        tags = self._extract_tags(text)
        
        # 构建记忆
        memory = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "content": text,
            "title": title,
            "role": role,
            "emotion": emotion,
            "intensity": intensity,
            "importance_score": score,
            "tags": tags,
            "context": context,
            "created_at": datetime.now().isoformat(),
        }
        
        # 保存到 MemoFlow
        self._save_to_memoflow(memory)
        
        return memory
    
    def _generate_title(self, text, role):
        """生成标题"""
        # 提取前20字作为标题
        title = text[:30].replace("\n", " ")
        if len(text) > 30:
            title += "..."
        
        # 根据角色添加前缀
        if role == "user":
            return f"[你] {title}"
        else:
            return f"[文源] {title}"
    
    def _infer_room(self, emotion):
        """根据情绪推断房间"""
        emotion_room_map = {
            "excited": "会议室",
            "thinking": "书房",
            "anxious": "卧室",
            "frustrated": "车库",
            "insight": "厨房",
            "creative": "画室",
            "calm": "卧室",
            "happy": "客厅",
        }
        return emotion_room_map.get(emotion, "客厅")
    
    def _extract_tags(self, text):
        """提取标签"""
        tags = []
        
        # 项目名
        projects = ["BANK-AI", "MemoFlow", "记忆系统"]
        for p in projects:
            if p in text:
                tags.append(p)
        
        # 主题
        themes = {
            "技术": ["代码", "开发", "实现", "架构"],
            "设计": ["设计", "UI", "界面", "视觉"],
            "决策": ["决定", "确定", "拍板", "方案"],
        }
        for theme, keywords in themes.items():
            if any(kw in text for kw in keywords):
                tags.append(theme)
        
        return tags[:5]
    
    def _save_to_memoflow(self, memory):
        """保存到 MemoFlow 系统"""
        import subprocess
        
        # 调用 mem 命令
        cmd = [
            "python3",
            str(Path.home() / ".openclaw/workspace/pythontools/mem.py"),
            "save",
            "--content", memory["content"],
            "--title", memory["title"],
            "--auto"
        ]
        
        subprocess.run(cmd, capture_output=True)
    
    def auto_recall(self, query, max_results=5):
        """
        自动回忆相关记忆
        
        Args:
            query: 查询内容（对话上下文）
            max_results: 最大返回条数
        
        Returns:
            相关记忆列表
        """
        # 提取关键词
        keywords = self._extract_query_keywords(query)
        
        if not keywords:
            return []
        
        # 搜索每个关键词
        all_results = []
        for kw in keywords[:3]:  # 最多3个关键词
            results = self._search_keyword(kw)
            all_results.extend(results)
        
        # 去重和排序
        seen_ids = set()
        unique_results = []
        for r in all_results:
            if r["id"] not in seen_ids:
                seen_ids.add(r["id"])
                unique_results.append(r)
        
        # 按相关性和时间排序
        unique_results.sort(key=lambda x: (x.get("importance_score", 0), x.get("created_at", "")), reverse=True)
        
        return unique_results[:max_results]
    
    def _extract_query_keywords(self, query):
        """从查询中提取关键词"""
        # 简单实现：提取长度>2的名词性词汇
        words = re.findall(r'[\u4e00-\u9fa5]{2,}|[a-zA-Z]{3,}', query)
        
        # 过滤停用词
        stop_words = ["什么", "怎么", "为什么", "如何", "这个", "那个", "我们", "咱们"]
        keywords = [w for w in words if w not in stop_words]
        
        return keywords[:5]
    
    def _search_keyword(self, keyword):
        """搜索关键词"""
        results = []
        
        # 搜索基础层
        try:
            import subprocess
            result = subprocess.run(
                ["claw", "search", keyword],
                capture_output=True, text=True
            )
            # 解析结果并添加到 results
            # 简化版：这里只返回空列表，实际应该解析输出
        except:
            pass
        
        return results
    
    def should_proactive_recall(self, text):
        """
        判断是否主动回忆
        
        触发条件：
        1. 提到项目名
        2. 提到"上次"、"之前"
        3. 问题模式
        """
        triggers = [
            "BANK-AI", "记忆系统", "项目",
            "上次", "之前", "以前", "曾经",
            "？", "?",
            "记得", "回忆", "想起",
        ]
        
        for trigger in triggers:
            if trigger in text:
                return True
        
        return False
    
    def format_memory_for_dialog(self, memories):
        """格式化记忆为对话形式"""
        if not memories:
            return None
        
        formatted = []
        for mem in memories[:3]:  # 最多3条
            time_str = mem.get("created_at", "")[5:16] if mem.get("created_at") else ""
            preview = mem.get("content", "")[:80] + "..." if len(mem.get("content", "")) > 80 else mem.get("content", "")
            formatted.append(f"[{time_str}] {preview}")
        
        return "\n".join(formatted)

def process_user_message(message, context=None):
    """
    处理用户消息的主入口
    
    在每次用户发言后调用
    """
    autoflow = MemoFlowAuto()
    
    # 1. 自动保存
    saved_memory = autoflow.auto_save(message, role="user", context=context)
    
    save_info = None
    if saved_memory:
        emotion_emoji = EMOTION_PATTERNS.get(saved_memory["emotion"], {}).get("emoji", "")
        save_info = {
            "saved": True,
            "emotion": saved_memory["emotion"],
            "emoji": emotion_emoji,
            "room": autoflow._infer_room(saved_memory["emotion"]),
            "title": saved_memory["title"],
        }
    
    # 2. 判断是否主动回忆
    should_recall = autoflow.should_proactive_recall(message)
    
    recall_info = None
    if should_recall:
        memories = autoflow.auto_recall(message)
        if memories:
            recall_info = {
                "recalled": True,
                "count": len(memories),
                "memories": memories,
                "formatted": autoflow.format_memory_for_dialog(memories),
            }
    
    return {
        "save_info": save_info,
        "recall_info": recall_info,
    }

def main():
    """测试模式"""
    autoflow = MemoFlowAuto()
    
    # 测试自动保存
    test_messages = [
        "好的",  # 不应该保存
        "突然想到一个关于BANK-AI的新方案",  # 应该保存
        "记住这个：记忆系统的自动保存功能",  # 应该保存
        "哈哈",  # 不应该保存
    ]
    
    print("🌊 MemoFlow Auto 测试\n")
    print("=" * 60)
    
    for msg in test_messages:
        result = autoflow.auto_save(msg)
        should_save, score, reason = autoflow.should_auto_save(msg)
        
        status = "✅ 已保存" if result else f"❌ 未保存 ({reason})"
        print(f"\n📝 {msg[:30]}...")
        print(f"   决策: {status}")
        if result:
            print(f"   情绪: {result['emotion']} ({result['intensity']}/10)")
            print(f"   标题: {result['title']}")

if __name__ == "__main__":
    main()
