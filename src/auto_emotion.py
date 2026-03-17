#!/usr/bin/env python3
"""
自动情绪分析记忆系统
AI自动判断情绪并保存记忆
"""

import re
import sys
import json
from datetime import datetime
from pathlib import Path

# 情绪关键词映射
EMOTION_PATTERNS = {
    "excited": {
        "keywords": ["太棒了", "搞定", "完成", "成功", " breakthrough", "excited", "awesome", "great", "amazing", "完美", "赞", "厉害", "牛逼", "爽", "开心", "高兴", "兴奋", "激动", "耶", "woohoo", "yay"],
        "emoji": "😄",
        "name": "兴奋",
        "intensity_boost": 2
    },
    "happy": {
        "keywords": ["不错", "挺好", "满意", "愉快", "happy", "good", "nice", "pleasant", "enjoy", "喜欢", "爱", "幸福", "满足", "舒适", "顺心"],
        "emoji": "😊",
        "name": "愉快",
        "intensity_boost": 0
    },
    "thinking": {
        "keywords": ["思考", "考虑", "觉得", "想", "thinking", "wonder", "ponder", "analyze", "或许", "可能", "应该", "怎么", "为什么", "如何", "问题", "疑问"],
        "emoji": "🤔",
        "name": "思考",
        "intensity_boost": 0
    },
    "anxious": {
        "keywords": ["担心", "焦虑", "怕", "紧张", "anxious", "worried", "concern", "nervous", "stress", "怎么办", "危险", "风险", "困难", "麻烦", "糟糕", "不好", "失败"],
        "emoji": "😰",
        "name": "焦虑",
        "intensity_boost": 1
    },
    "frustrated": {
        "keywords": ["沮丧", "郁闷", "烦", "生气", "frustrated", "annoyed", "angry", "upset", "disappointed", "stuck", "卡住了", "bug", "错误", "不行", "失败", "放弃"],
        "emoji": "😤",
        "name": "沮丧",
        "intensity_boost": 1
    },
    "insight": {
        "keywords": ["顿悟", "突然想到", "明白了", "发现", "insight", "realize", "aha", "eureka", "原来", "其实", "本质上", "关键", "核心", "突破", "新思路", "灵感"],
        "emoji": "💡",
        "name": "顿悟",
        "intensity_boost": 2
    },
    "creative": {
        "keywords": ["创意", "想法", "设计", "方案", "creative", "idea", "design", "imagine", "脑洞", "新颖", "独特", "有趣", "好玩", "艺术", "美", "创新"],
        "emoji": "🎨",
        "name": "创意",
        "intensity_boost": 1
    },
    "calm": {
        "keywords": ["平静", "淡定", "冷静", "calm", "peaceful", "relaxed", "steady", "稳定", "OK", "好的", "嗯", "了解", "明白", "知道了"],
        "emoji": "😌",
        "name": "平静",
        "intensity_boost": -1
    }
}

def analyze_emotion(text):
    """
    分析文本情绪
    返回: (emotion_type, intensity, confidence)
    """
    text_lower = text.lower()
    scores = {}
    
    for emotion, data in EMOTION_PATTERNS.items():
        score = 0
        matched_keywords = []
        
        for keyword in data["keywords"]:
            if keyword in text or keyword in text_lower:
                score += 1
                matched_keywords.append(keyword)
        
        if score > 0:
            scores[emotion] = {
                "score": score,
                "keywords": matched_keywords,
                "data": data
            }
    
    if not scores:
        # 默认平静
        return "calm", 5, 0.3
    
    # 选择得分最高的情绪
    best_emotion = max(scores.items(), key=lambda x: x[1]["score"])
    emotion_type = best_emotion[0]
    emotion_data = best_emotion[1]
    
    # 计算强度
    base_intensity = 5
    keyword_count = emotion_data["score"]
    boost = emotion_data["data"]["intensity_boost"]
    
    # 根据关键词数量和标点符号调整强度
    intensity = base_intensity + keyword_count + boost
    
    # 感叹号增加强度
    exclamation_count = text.count('!') + text.count('！')
    intensity += exclamation_count
    
    # 问号可能表示思考或焦虑
    question_count = text.count('?') + text.count('？')
    if emotion_type in ["thinking", "anxious"]:
        intensity += question_count
    
    # 限制在1-10范围
    intensity = max(1, min(10, intensity))
    
    # 计算置信度
    confidence = min(1.0, emotion_data["score"] * 0.3 + 0.2)
    
    return emotion_type, intensity, confidence, emotion_data["keywords"]

def extract_tags(text):
    """
    从文本中提取关键词作为标签
    """
    tags = []
    
    # 项目名
    project_patterns = [r'BANK-AI', r'Phase \d', r'Week \d+', r'知识图谱', r'GNN', r'KGQA']
    for pattern in project_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        tags.extend(matches)
    
    # 技术关键词
    tech_keywords = [r'AI', r'API', r'代码', r'算法', r'架构', r'数据库', r'前端', r'后端', r'测试', r'优化', r'设计', r'功能', r'系统', r'技能', r'记忆', r'情绪']
    for keyword in tech_keywords:
        if re.search(keyword, text, re.IGNORECASE):
            tags.append(keyword)
    
    # 去重
    tags = list(set(tags))
    
    return tags[:5]  # 最多5个标签

def auto_save_memory(content, title=None, source="auto"):
    """
    自动分析情绪并保存记忆
    """
    # 分析情绪
    emotion, intensity, confidence, keywords = analyze_emotion(content)
    emotion_data = EMOTION_PATTERNS[emotion]
    
    # 提取标签
    auto_tags = extract_tags(content)
    
    # 构建记忆
    memory = {
        "title": title or f"自动保存_{datetime.now().strftime('%H:%M')}",
        "content": content,
        "emotion": emotion,
        "emotion_name": emotion_data["name"],
        "emotion_emoji": emotion_data["emoji"],
        "intensity": intensity,
        "confidence": confidence,
        "matched_keywords": keywords,
        "auto_tags": auto_tags,
        "source": source,
        "created_at": datetime.now().isoformat(),
    }
    
    # 保存到自动记忆文件
    memory_dir = Path.home() / "Documents/claw_memory/auto_emotional"
    memory_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    memory_file = memory_dir / f"{date_str}.jsonl"
    
    with open(memory_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(memory, ensure_ascii=False) + "\n")
    
    # 同时保存到标准系统
    try:
        import subprocess
        all_tags = [emotion] + auto_tags
        cmd = [
            "python3",
            str(Path.home() / ".openclaw/workspace/pythontools/unified_memory.py"),
            "save",
            "--content", f"{emotion_data['emoji']} [{emotion_data['name']}@{intensity}/10, 置信度{confidence:.0%}]\n\n{content}",
            "--title", memory["title"],
            "--tags", ",".join(all_tags),
            "--category", "auto_emotional"
        ]
        subprocess.run(cmd, capture_output=True, text=True)
    except Exception as e:
        pass
    
    # 显示结果
    color_map = {
        "excited": "\033[93m",  # 黄色
        "happy": "\033[92m",    # 绿色
        "thinking": "\033[94m", # 蓝色
        "anxious": "\033[91m",  # 红色
        "frustrated": "\033[90m", # 灰色
        "insight": "\033[95m",  # 紫色
        "creative": "\033[96m", # 青色
        "calm": "\033[97m",     # 白色
    }
    color = color_map.get(emotion, "\033[0m")
    reset = "\033[0m"
    
    print(f"\n{color}{emotion_data['emoji']} AI自动分析情绪: {emotion_data['name']} ({intensity}/10){reset}")
    print(f"   置信度: {confidence:.0%}")
    print(f"   触发词: {', '.join(keywords[:3])}")
    print(f"   自动标签: {', '.join(auto_tags)}")
    print(f"   标题: {memory['title']}")
    print(f"   {color}已自动保存到记忆系统{reset}\n")
    
    return memory

def analyze_conversation(user_text, assistant_text=None):
    """
    分析对话并保存重要记忆
    """
    # 判断是否是重要对话
    important_patterns = [
        r'想法', r'思路', r'方案', r'设计', r'计划', r'决定', r'确定',
        r'问题', r'解决', r'突破', r'完成', r'实现', r'发现', r'明白',
        r'重要', r'关键', r'核心', r'顿悟', r'突然',
    ]
    
    is_important = any(re.search(pattern, user_text) for pattern in important_patterns)
    
    if not is_important:
        return None
    
    # 合并对话内容
    full_content = user_text
    if assistant_text:
        full_content += f"\n\n[AI回应]: {assistant_text[:200]}..."
    
    # 生成标题
    title = generate_title(user_text)
    
    # 自动保存
    return auto_save_memory(full_content, title, source="conversation")

def generate_title(text):
    """
    从文本生成标题
    """
    # 提取前20个字符作为标题
    title = text[:30].replace("\n", " ")
    if len(text) > 30:
        title += "..."
    return title

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="自动情绪分析记忆")
    parser.add_argument("--text", "-t", help="要分析的文本")
    parser.add_argument("--demo", action="store_true", help="运行演示")
    
    args = parser.parse_args()
    
    if args.demo:
        # 演示各种情绪
        demo_texts = [
            "太棒了！刚刚完成了这个功能，效果比预期好很多！",
            "突然想到一个更好的方案，可以用情绪+时间轴结合...",
            "有点担心这个架构的复杂度，实现起来可能有风险...",
            "这个问题卡住了，试了好几种方法都不行，有点沮丧...",
            "你觉得这个设计怎么样？我在想是不是可以换个思路...",
        ]
        
        print("🎭 自动情绪分析演示\n")
        print("=" * 60)
        
        for text in demo_texts:
            print(f"\n原文: {text}")
            auto_save_memory(text, source="demo")
            print("-" * 60)
    
    elif args.text:
        auto_save_memory(args.text)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
