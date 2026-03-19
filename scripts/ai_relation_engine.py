#!/usr/bin/env python3
"""
MemoFlow 2.0 - AI关系推理引擎
自动发现记忆间的潜在关系
"""

import sys
sys.path.insert(0, '~/.openclaw/workspace/skills/memflow-v2')

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
from memflow2 import MemoFlow2

@dataclass
class RelationSuggestion:
    from_id: str
    to_id: str
    relation_type: str
    confidence: float
    reason: str

class AIRelationEngine:
    """AI驱动的关系发现引擎"""
    
    # 关系关键词模式
    RELATION_PATTERNS = {
        'depends_on': [
            r'基于|根据|依赖|前提|先决条件|需要先有|在...之后|在...基础上',
            r'基于|depends? on|based on|prerequisite|requires',
        ],
        'supersedes': [
            r'取代|替代|废弃|不再使用|新版|v\d+\.\d+|升级到|迁移到',
            r'supersedes?|replaces?|deprecated|migrat(e|ed|ing) to|upgraded? to',
        ],
        'relates_to': [
            r'相关|关联|关于|涉及|提到|谈到|参考|借鉴',
            r'related|relates? to|regarding|about|reference|similar to',
        ],
        'replies_to': [
            r'回复|回答|解决|针对|回应|解答|修复',
            r'replies? to|answers?|solves?|fixes?|in response to|addresses?',
        ],
    }
    
    def __init__(self):
        self.mf = MemoFlow2()
    
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取（可以后续接入更复杂的NLP）
        words = re.findall(r'\b[A-Za-z\u4e00-\u9fa5]{2,}\b', text.lower())
        
        # 过滤停用词
        stopwords = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
                     '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
                     '你', '会', '着', '没有', '看', '好', '自己', '这'}
        
        keywords = [w for w in words if w not in stopwords and len(w) > 1]
        return list(set(keywords))  # 去重
    
    def keyword_similarity(self, text1: str, text2: str) -> float:
        """基于关键词的相似度"""
        kw1 = set(self.extract_keywords(text1))
        kw2 = set(self.extract_keywords(text2))
        
        if not kw1 or not kw2:
            return 0.0
        
        intersection = kw1 & kw2
        union = kw1 | kw2
        
        return len(intersection) / len(union) if union else 0.0
    
    def detect_relation_by_pattern(self, content: str) -> List[Tuple[str, float]]:
        """通过模式匹配检测关系类型"""
        results = []
        
        for relation, patterns in self.RELATION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # 根据匹配数量计算置信度
                    matches = len(re.findall(pattern, content, re.IGNORECASE))
                    confidence = min(0.9, 0.5 + matches * 0.1)
                    results.append((relation, confidence))
                    break  # 该关系类型已匹配，跳过其他模式
        
        return results
    
    def find_semantic_relations(self, memory_id: str, threshold: float = 0.3) -> List[RelationSuggestion]:
        """查找语义相关的记忆"""
        # 获取当前记忆
        cursor = self.mf.conn.cursor()
        cursor.execute('SELECT * FROM memories WHERE id = ?', (memory_id,))
        source = cursor.fetchone()
        
        if not source:
            return []
        
        suggestions = []
        source_content = source['content']
        
        # 获取所有其他记忆
        cursor.execute('SELECT * FROM memories WHERE id != ?', (memory_id,))
        targets = cursor.fetchall()
        
        for target in targets:
            target_content = target['content']
            
            # 1. 关键词相似度
            sim_score = self.keyword_similarity(source_content, target_content)
            
            if sim_score >= threshold:
                # 2. 检测具体关系类型
                combined_text = source_content + " " + target_content
                relations = self.detect_relation_by_pattern(combined_text)
                
                if relations:
                    # 使用检测到的关系类型
                    for rel_type, rel_conf in relations:
                        combined_confidence = (sim_score + rel_conf) / 2
                        suggestions.append(RelationSuggestion(
                            from_id=memory_id,
                            to_id=target['id'],
                            relation_type=rel_type,
                            confidence=combined_confidence,
                            reason=f"关键词相似度: {sim_score:.2f}, 模式匹配: {rel_conf:.2f}"
                        ))
                else:
                    # 默认相关关系
                    suggestions.append(RelationSuggestion(
                        from_id=memory_id,
                        to_id=target['id'],
                        relation_type='relates_to',
                        confidence=sim_score,
                        reason=f"关键词相似度: {sim_score:.2f}"
                    ))
        
        # 按置信度排序
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions[:10]  # 返回前10个
    
    def auto_link_memories(self, dry_run: bool = True) -> List[RelationSuggestion]:
        """自动为所有记忆建立关系"""
        print("🤖 AI自动关系发现启动...")
        
        cursor = self.mf.conn.cursor()
        cursor.execute('SELECT id FROM memories')
        all_memories = cursor.fetchall()
        
        all_suggestions = []
        
        for i, (memory_id,) in enumerate(all_memories):
            print(f"  分析记忆 {i+1}/{len(all_memories)}: {memory_id[:10]}...", end='\r')
            
            suggestions = self.find_semantic_relations(memory_id, threshold=0.25)
            
            # 过滤已存在的关系
            for sug in suggestions:
                cursor.execute('''
                SELECT 1 FROM memory_relations 
                WHERE from_id = ? AND to_id = ? AND relation_type = ?
                ''', (sug.from_id, sug.to_id, sug.relation_type))
                
                if not cursor.fetchone():
                    all_suggestions.append(sug)
                    
                    if not dry_run and sug.confidence >= 0.5:
                        self.mf.link_memories(
                            sug.from_id,
                            sug.to_id,
                            sug.relation_type,
                            strength=sug.confidence,
                            note=f"AI自动生成: {sug.reason}"
                        )
        
        print(f"\n✅ 发现 {len(all_suggestions)} 个潜在关系")
        
        # 按置信度分组展示
        high_conf = [s for s in all_suggestions if s.confidence >= 0.6]
        med_conf = [s for s in all_suggestions if 0.4 <= s.confidence < 0.6]
        low_conf = [s for s in all_suggestions if s.confidence < 0.4]
        
        print(f"   高置信度(≥0.6): {len(high_conf)}")
        print(f"   中置信度(0.4-0.6): {len(med_conf)}")
        print(f"   低置信度(<0.4): {len(low_conf)}")
        
        return all_suggestions
    
    def suggest_for_new_memory(self, content: str) -> List[RelationSuggestion]:
        """为新记忆建议关系"""
        # 创建临时ID用于匹配
        temp_id = "temp_new_memory"
        
        suggestions = []
        
        cursor = self.mf.conn.cursor()
        cursor.execute('SELECT * FROM memories')
        
        for target in cursor.fetchall():
            sim_score = self.keyword_similarity(content, target['content'])
            
            if sim_score >= 0.25:
                suggestions.append(RelationSuggestion(
                    from_id=temp_id,
                    to_id=target['id'],
                    relation_type='relates_to',
                    confidence=sim_score,
                    reason=f"关键词相似度: {sim_score:.2f}"
                ))
        
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions[:5]
    
    def close(self):
        self.mf.close()


def main():
    """CLI入口"""
    import sys
    
    engine = AIRelationEngine()
    
    if len(sys.argv) < 2:
        print("AI关系推理引擎")
        print("\nCommands:")
        print("  analyze <id>      分析单个记忆的关系")
        print("  auto [apply]      自动发现所有关系 (加apply执行)")
        print("  suggest <text>    为新内容建议关系")
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'analyze':
        if len(sys.argv) < 3:
            print("Usage: analyze <memory_id>")
            return
        
        memory_id = sys.argv[2]
        suggestions = engine.find_semantic_relations(memory_id)
        
        print(f"\n🔍 为 {memory_id} 发现的关系建议:\n")
        for i, sug in enumerate(suggestions[:10], 1):
            rel_name = engine.mf.RELATIONS.get(sug.relation_type, sug.relation_type)
            print(f"{i}. [{rel_name}] → {sug.to_id}")
            print(f"   置信度: {sug.confidence:.2f}")
            print(f"   原因: {sug.reason}")
            print()
    
    elif cmd == 'auto':
        dry_run = len(sys.argv) < 3 or sys.argv[2] != 'apply'
        if dry_run:
            print("💡 干运行模式 (加 'apply' 参数执行写入)\n")
        
        suggestions = engine.auto_link_memories(dry_run=dry_run)
        
        if suggestions and not dry_run:
            print(f"\n✅ 已自动建立 {len([s for s in suggestions if s.confidence >= 0.5])} 条关系")
    
    elif cmd == 'suggest':
        if len(sys.argv) < 3:
            print("Usage: suggest '<text>'")
            return
        
        text = sys.argv[2]
        suggestions = engine.suggest_for_new_memory(text)
        
        print(f"\n💡 建议关联的记忆:\n")
        for sug in suggestions:
            cursor = engine.mf.conn.cursor()
            cursor.execute('SELECT summary FROM memories WHERE id = ?', (sug.to_id,))
            row = cursor.fetchone()
            title = row['summary'][:50] if row else sug.to_id
            
            print(f"  [{sug.confidence:.2f}] {title}...")
            print(f"     ID: {sug.to_id}")
            print()
    
    engine.close()


if __name__ == '__main__':
    main()
