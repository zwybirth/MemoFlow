#!/usr/bin/env python3
"""
mem - 记忆系统统一入口 v1.0
打通基础层、情绪层、宫殿层的任督二脉

Usage:
    mem save --content "..." [--title "..."] [--auto]
    mem search "keyword"
    mem stats
    mem palace --open
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# 配置
MEMORY_PALACE_DIR = Path.home() / "Documents/claw_memory/palace"
ROOMS = {
    "厨房": {"id": "kitchen", "emoji": "🍳", "keywords": ["想法", "方案", "设计", "创意", "灵感", "脑洞", "突然", "新思路"]},
    "书房": {"id": "study", "emoji": "📚", "keywords": ["技术", "代码", "学习", "知识", "架构", "算法", "实现", "开发"]},
    "会议室": {"id": "meeting", "emoji": "💼", "keywords": ["决策", "项目", "讨论", "重要", "确定", "计划", "拍板", "决定"]},
    "车库": {"id": "garage", "emoji": "🔧", "keywords": ["工具", "脚本", "配置", "自动化", "优化", "修复", "解决"]},
    "卧室": {"id": "bedroom", "emoji": "🛏️", "keywords": ["日常", "情绪", "感受", "想法", "思考", "担心", "焦虑"]},
    "画室": {"id": "studio", "emoji": "🎨", "keywords": ["设计", "UI", "界面", "视觉", "艺术", "美观", "配色"]},
    "客厅": {"id": "living", "emoji": "🛋️", "keywords": []},  # 默认
}

EMOTIONS = {
    "excited": {"emoji": "😄", "keywords": ["太棒了", "搞定", "完成", "成功", "完美", "赞", "厉害", "爽", "开心", "兴奋", "激动"]},
    "happy": {"emoji": "😊", "keywords": ["不错", "挺好", "满意", "愉快", "喜欢", "幸福", "满足"]},
    "thinking": {"emoji": "🤔", "keywords": ["思考", "考虑", "觉得", "想", "或许", "可能", "应该", "怎么", "为什么", "如何"]},
    "anxious": {"emoji": "😰", "keywords": ["担心", "焦虑", "怕", "紧张", "怎么办", "危险", "风险", "困难"]},
    "frustrated": {"emoji": "😤", "keywords": ["沮丧", "郁闷", "烦", "生气", "卡住了", "不行", "失败"]},
    "insight": {"emoji": "💡", "keywords": ["顿悟", "突然想到", "明白了", "发现", "原来", "本质上", "关键", "突破"]},
    "creative": {"emoji": "🎨", "keywords": ["创意", "想法", "设计", "方案", "脑洞", "新颖", "独特"]},
    "calm": {"emoji": "😌", "keywords": ["平静", "淡定", "冷静", "稳定", "了解", "明白"]},
}

class MemoryRouter:
    """记忆路由器 - 智能分发记忆到各子系统"""
    
    def analyze_emotion(self, content):
        """分析情绪"""
        content_lower = content.lower()
        scores = {}
        
        for emotion, data in EMOTIONS.items():
            score = sum(1 for kw in data["keywords"] if kw in content or kw in content_lower)
            if score > 0:
                scores[emotion] = score
        
        if not scores:
            return "calm", 5
        
        best_emotion = max(scores.items(), key=lambda x: x[1])
        intensity = min(10, 5 + best_emotion[1])
        
        return best_emotion[0], intensity
    
    def assign_room(self, content, emotion=None):
        """智能分配房间"""
        # 根据情绪推断房间
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
        
        if emotion and emotion in emotion_room_map:
            return emotion_room_map[emotion]
        
        # 根据关键词分配
        for room_name, info in ROOMS.items():
            if any(kw in content for kw in info["keywords"]):
                return room_name
        
        return "客厅"
    
    def route(self, content):
        """路由决策"""
        emotion, intensity = self.analyze_emotion(content)
        room = self.assign_room(content, emotion)
        
        return {
            "emotion": emotion,
            "intensity": intensity,
            "room": room,
        }

class MemorySystem:
    """记忆系统统一接口"""
    
    def __init__(self):
        self.router = MemoryRouter()
    
    def save(self, content, title=None, auto=False):
        """
        保存记忆到所有子系统
        
        Args:
            content: 记忆内容
            title: 标题
            auto: 是否自动分析情绪和分配房间
        """
        print(f"\n📝 正在保存记忆...")
        print(f"   内容: {content[:50]}...")
        
        # 1. 基础层存储（必须）
        print("\n📦 同步到基础层...", end=" ")
        self._save_to_local_mem(content, title)
        print("✅")
        
        if auto:
            # 智能分析
            route_info = self.router.route(content)
            emotion = route_info["emotion"]
            intensity = route_info["intensity"]
            room = route_info["room"]
            
            print(f"\n🎭 智能分析结果:")
            print(f"   情绪: {EMOTIONS[emotion]['emoji']} {emotion} ({intensity}/10)")
            print(f"   房间: {ROOMS[room]['emoji']} {room}")
            
            # 2. 宫殿层存储
            print(f"\n🏛️ 同步到宫殿层...", end=" ")
            self._save_to_palace(content, title, room, emotion, intensity)
            print("✅")
            
            # 3. 情绪层存储
            print(f"\n💝 同步到情绪层...", end=" ")
            self._save_to_emotional(content, title, emotion, intensity)
            print("✅")
            
            print(f"\n🎉 记忆同步完成！")
            print(f"   已同步到: 基础层 + 宫殿层({room}) + 情绪层({emotion})")
        else:
            print(f"\n✅ 基础层保存完成（使用 --auto 启用智能分析）")
    
    def _save_to_local_mem(self, content, title):
        """保存到基础层"""
        cmd = ["claw", "save", "--content", content]
        if title:
            cmd.extend(["--title", title])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def _save_to_palace(self, content, title, room, emotion, intensity):
        """保存到宫殿层"""
        palace_script = Path.home() / ".openclaw/workspace/skills/memory-palace/palace.py"
        
        cmd = [
            "python3", str(palace_script),
            "save",
            "--content", content,
            "--room", room,
            "--emotion", emotion,
            "--intensity", str(intensity),
        ]
        if title:
            cmd.extend(["--title", title])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def _save_to_emotional(self, content, title, emotion, intensity):
        """保存到情绪层"""
        emotion_script = Path.home() / ".openclaw/workspace/skills/emotional-memory/emotion-memory.py"
        
        cmd = [
            "python3", str(emotion_script),
            "save",
            "--content", content,
            "--emotion", emotion,
            "--intensity", str(intensity),
        ]
        if title:
            cmd.extend(["--title", title])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def search(self, keyword):
        """跨系统检索"""
        print(f"\n🔍 跨系统检索: '{keyword}'")
        print("=" * 60)
        
        results = []
        
        # 并行检索
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                '基础层': executor.submit(self._search_local_mem, keyword),
                '宫殿层': executor.submit(self._search_palace, keyword),
                '情绪层': executor.submit(self._search_emotional, keyword),
            }
            
            for system, future in futures.items():
                try:
                    count = future.result()
                    results.append((system, count))
                except Exception as e:
                    results.append((system, f"错误: {e}"))
        
        print("\n" + "=" * 60)
        print("📊 检索汇总:")
        for system, count in results:
            print(f"   {system}: {count} 条结果")
    
    def _search_local_mem(self, keyword):
        """检索基础层"""
        print("\n📁 基础层:")
        result = subprocess.run(
            ["claw", "search", keyword],
            capture_output=True, text=True
        )
        
        # 解析结果数量
        lines = result.stdout.strip().split('\n')
        count = len([l for l in lines if l.startswith('  ') and '...' in l])
        if count == 0 and "找到" in result.stdout:
            # 尝试其他格式
            import re
            match = re.search(r'(\d+)', result.stdout)
            if match:
                count = int(match.group(1))
        
        print(f"   找到 {count} 条记忆")
        return count
    
    def _search_palace(self, keyword):
        """检索宫殿层"""
        print("\n🏛️ 宫殿层:")
        
        # 直接扫描宫殿文件
        palace_dir = MEMORY_PALACE_DIR / "rooms"
        count = 0
        
        if palace_dir.exists():
            for room_dir in palace_dir.iterdir():
                if room_dir.is_dir():
                    for mem_file in room_dir.glob("*.json"):
                        try:
                            with open(mem_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                if keyword in data.get('content', '') or keyword in data.get('title', ''):
                                    count += 1
                        except:
                            continue
        
        print(f"   找到 {count} 条记忆")
        return count
    
    def _search_emotional(self, keyword):
        """检索情绪层"""
        print("\n🎭 情绪层:")
        
        emotion_dir = Path.home() / "Documents/claw_memory/emotional"
        count = 0
        
        if emotion_dir.exists():
            for jsonl_file in emotion_dir.glob("*.jsonl"):
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                data = json.loads(line)
                                if keyword in data.get('content', '') or keyword in data.get('title', ''):
                                    count += 1
                            except:
                                continue
        
        print(f"   找到 {count} 条记忆")
        return count
    
    def stats(self):
        """显示系统统计"""
        print("\n📊 记忆系统统计")
        print("=" * 60)
        
        # 基础层
        result = subprocess.run(["claw", "stats"], capture_output=True, text=True)
        print("\n📦 基础层:")
        print(result.stdout)
        
        # 宫殿层
        print("\n🏛️ 宫殿层:")
        palace_dir = MEMORY_PALACE_DIR / "rooms"
        if palace_dir.exists():
            for room_name, info in ROOMS.items():
                room_dir = palace_dir / info["id"]
                count = len(list(room_dir.glob("*.json"))) if room_dir.exists() else 0
                print(f"   {info['emoji']} {room_name}: {count} 条")
        
        # 情绪层
        print("\n🎭 情绪层:")
        emotion_dir = Path.home() / "Documents/claw_memory/emotional"
        if emotion_dir.exists():
            for emotion_name, info in EMOTIONS.items():
                emotion_file = emotion_dir / f"{emotion_name}.jsonl"
                count = sum(1 for _ in open(emotion_file, 'r', encoding='utf-8') if _.strip()) if emotion_file.exists() else 0
                if count > 0:
                    print(f"   {info['emoji']} {emotion_name}: {count} 条")
        
        print("\n" + "=" * 60)
    
    def open_palace(self):
        """打开宫殿可视化"""
        print("\n🏛️ 正在生成宫殿可视化...")
        
        visualize_script = Path.home() / ".openclaw/workspace/skills/memory-palace/visualize.py"
        
        result = subprocess.run(
            ["python3", str(visualize_script)],
            capture_output=True, text=True
        )
        
        print(result.stdout)
        
        html_file = MEMORY_PALACE_DIR / "palace_visualization.html"
        if html_file.exists():
            print(f"\n🌐 正在打开浏览器...")
            import webbrowser
            webbrowser.open(f"file://{html_file}")

def main():
    parser = argparse.ArgumentParser(
        description="mem - 记忆系统统一入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  mem save --content "今天的想法" --auto
  mem save --content "重要决策" --title "项目讨论" --auto
  mem search "BANK-AI"
  mem stats
  mem palace --open
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # save 命令
    save_parser = subparsers.add_parser("save", help="保存记忆")
    save_parser.add_argument("--content", "-c", required=True, help="记忆内容")
    save_parser.add_argument("--title", "-t", help="标题")
    save_parser.add_argument("--auto", "-a", action="store_true", 
                           help="自动分析情绪和分配房间")
    
    # search 命令
    search_parser = subparsers.add_parser("search", help="跨系统检索")
    search_parser.add_argument("keyword", help="关键词")
    
    # stats 命令
    subparsers.add_parser("stats", help="系统统计")
    
    # palace 命令
    palace_parser = subparsers.add_parser("palace", help="宫殿可视化")
    palace_parser.add_argument("--open", "-o", action="store_true", help="打开浏览器")
    
    args = parser.parse_args()
    
    mem = MemorySystem()
    
    if args.command == "save":
        mem.save(args.content, args.title, args.auto)
    elif args.command == "search":
        mem.search(args.keyword)
    elif args.command == "stats":
        mem.stats()
    elif args.command == "palace":
        if args.open:
            mem.open_palace()
        else:
            print("使用 --open 打开宫殿可视化")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
