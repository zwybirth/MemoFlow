#!/usr/bin/env python3
"""
情绪记忆增强版 - Emotion-Enhanced Memory
扩展 LOCAL-MEM 系统，支持情绪标记和检索
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# 情绪类型定义
EMOTIONS = {
    "excited": {"emoji": "😄", "name": "兴奋", "color": "\033[93m"},
    "happy": {"emoji": "😊", "name": "愉快", "color": "\033[92m"},
    "thinking": {"emoji": "🤔", "name": "思考", "color": "\033[94m"},
    "anxious": {"emoji": "😰", "name": "焦虑", "color": "\033[91m"},
    "frustrated": {"emoji": "😤", "name": "沮丧", "color": "\033[90m"},
    "insight": {"emoji": "💡", "name": "顿悟", "color": "\033[95m"},
    "creative": {"emoji": "🎨", "name": "创意", "color": "\033[96m"},
    "calm": {"emoji": "😌", "name": "平静", "color": "\033[97m"},
}

def save_with_emotion(content, title=None, emotion=None, intensity=5, tags=None, category="daily"):
    """
    保存带情绪标记的记忆
    
    Args:
        content: 记忆内容
        title: 标题
        emotion: 情绪类型 (excited/happy/thinking/anxious/frustrated/insight/creative/calm)
        intensity: 强度 1-10
        tags: 标签列表
        category: 分类
    """
    # 构建记忆条目
    memory = {
        "title": title or "未命名记忆",
        "content": content,
        "emotion": emotion,
        "intensity": intensity,
        "tags": tags or [],
        "category": category,
        "created_at": datetime.now().isoformat(),
    }
    
    # 添加情绪emoji
    if emotion and emotion in EMOTIONS:
        memory["emotion_emoji"] = EMOTIONS[emotion]["emoji"]
        memory["emotion_name"] = EMOTIONS[emotion]["name"]
    
    # 保存到情绪记忆文件
    memory_dir = Path.home() / "Documents/claw_memory/emotional"
    memory_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    emotion_file = memory_dir / f"{date_str}.jsonl"
    
    with open(emotion_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(memory, ensure_ascii=False) + "\n")
    
    # 同时保存到标准LOCAL-MEM（带情绪标签）
    emotion_tag = f"#{emotion}" if emotion else ""
    all_tags = " ".join([emotion_tag] + [f"#{t}" for t in (tags or [])])
    
    # 调用原始claw命令
    import subprocess
    cmd = [
        "python3",
        "~/.openclaw/workspace/pythontools/unified_memory.py",
        "save",
        "--content", f"{EMOTIONS.get(emotion, {}).get('emoji', '')} [{EMOTIONS.get(emotion, {}).get('name', '无情绪')}@{intensity}/10]\n\n{content}",
        "--title", title or "未命名记忆",
    ]
    if tags:
        cmd.extend(["--tags", ",".join(tags)])
    if category:
        cmd.extend(["--category", category])
    
    result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
    
    # 显示结果
    if emotion and emotion in EMOTIONS:
        e_info = EMOTIONS[emotion]
        print(f"{e_info['color']}{e_info['emoji']} 已保存情绪记忆: {e_info['name']} ({intensity}/10)\033[0m")
        print(f"   标题: {title or '未命名记忆'}")
        print(f"   标签: {all_tags}")
    else:
        print(f"✅ 已保存记忆（无情绪标记）")
    
    return memory

def search_by_emotion(emotion=None, intensity_range=None, start_date=None, end_date=None):
    """
    按情绪检索记忆
    """
    memory_dir = Path.home() / "Documents/claw_memory/emotional"
    
    if not memory_dir.exists():
        print("还没有情绪记忆记录")
        return []
    
    results = []
    
    for jsonl_file in sorted(memory_dir.glob("*.jsonl")):
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    memory = json.loads(line)
                    
                    # 情绪过滤
                    if emotion and memory.get("emotion") != emotion:
                        continue
                    
                    # 强度过滤
                    if intensity_range:
                        min_i, max_i = intensity_range
                        if not (min_i <= memory.get("intensity", 5) <= max_i):
                            continue
                    
                    results.append(memory)
                except json.JSONDecodeError:
                    continue
    
    return results

def show_emotion_stats():
    """
    显示情绪统计热力图
    """
    results = search_by_emotion()
    
    if not results:
        print("还没有情绪记忆记录")
        return
    
    # 统计情绪分布
    emotion_counts = {}
    for r in results:
        e = r.get("emotion", "unknown")
        emotion_counts[e] = emotion_counts.get(e, 0) + 1
    
    total = len(results)
    
    print("\n📊 情绪记忆分布")
    print("=" * 40)
    
    # 按数量排序
    sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
    
    for emotion, count in sorted_emotions:
        if emotion in EMOTIONS:
            e_info = EMOTIONS[emotion]
            bar = "█" * int(count / max(emotion_counts.values()) * 20)
            pct = count / total * 100
            print(f"{e_info['emoji']} {e_info['name']:6} {bar} {count}条 ({pct:.1f}%)")
    
    print("=" * 40)
    print(f"总计: {total} 条情绪记忆\n")

def main():
    parser = argparse.ArgumentParser(description="情绪记忆系统")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # save 命令
    save_parser = subparsers.add_parser("save", help="保存带情绪的记忆")
    save_parser.add_argument("--content", "-c", required=True, help="记忆内容")
    save_parser.add_argument("--title", "-t", help="标题")
    save_parser.add_argument("--emotion", "-e", 
                            choices=list(EMOTIONS.keys()),
                            help="情绪类型")
    save_parser.add_argument("--intensity", "-i", type=int, default=5,
                            help="强度 1-10")
    save_parser.add_argument("--tags", help="标签，逗号分隔")
    save_parser.add_argument("--category", default="daily", help="分类")
    
    # search 命令
    search_parser = subparsers.add_parser("search", help="按情绪检索")
    search_parser.add_argument("--emotion", "-e", choices=list(EMOTIONS.keys()))
    search_parser.add_argument("--min-intensity", type=int, default=1)
    search_parser.add_argument("--max-intensity", type=int, default=10)
    
    # stats 命令
    subparsers.add_parser("stats", help="情绪统计")
    
    # list-emotions 命令
    subparsers.add_parser("emotions", help="列出所有情绪类型")
    
    args = parser.parse_args()
    
    if args.command == "save":
        tags = args.tags.split(",") if args.tags else []
        save_with_emotion(
            content=args.content,
            title=args.title,
            emotion=args.emotion,
            intensity=args.intensity,
            tags=tags,
            category=args.category
        )
    
    elif args.command == "search":
        results = search_by_emotion(
            emotion=args.emotion,
            intensity_range=(args.min_intensity, args.max_intensity)
        )
        
        print(f"\n🔍 找到 {len(results)} 条记忆\n")
        for r in results:
            emoji = r.get("emotion_emoji", "")
            name = r.get("emotion_name", "无情绪")
            print(f"{emoji} [{name}@{r.get('intensity', 5)}/10] {r.get('title', '未命名')}")
            print(f"   {r.get('content', '')[:100]}...")
            print()
    
    elif args.command == "stats":
        show_emotion_stats()
    
    elif args.command == "emotions":
        print("\n🎭 支持的情绪类型:\n")
        for key, info in EMOTIONS.items():
            print(f"  {info['emoji']} {key:12} - {info['name']}")
        print()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
