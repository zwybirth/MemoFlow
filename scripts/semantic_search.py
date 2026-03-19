#!/usr/bin/env python3
"""
MemoFlow 2.0 - 语义搜索引擎
基于关键词向量的简单实现
可后续接入真实Embedding模型
"""

import sys
sys.path.insert(0, '~/.openclaw/workspace/skills/memflow-v2')

import numpy as np
from typing import List, Dict
from collections import Counter
from memflow2 import MemoFlow2

class SemanticSearch:
    """语义搜索引擎"""
    
    def __init__(self):
        self.mf = MemoFlow2()
        self.memory_vectors = {}
        self._build_vectors()
    
    def _text_to_vector(self, text: str) -> np.ndarray:
        """将文本转换为向量（简单词袋模型）"""
        # 提取关键词
        import re
        words = re.findall(r'\b[A-Za-z\u4e00-\u9fa5]{2,}\b', text.lower())
        
        # 构建词频向量
        word_counts = Counter(words)
        
        # 创建固定维度的向量（使用哈希技巧）
        vector_dim = 128
        vector = np.zeros(vector_dim)
        
        for word, count in word_counts.items():
            # 使用哈希确定位置
            hash_val = hash(word) % vector_dim
            vector[hash_val] += count
        
        # 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def _build_vectors(self):
        """为所有记忆构建向量"""
        cursor = self.mf.conn.cursor()
        cursor.execute('SELECT id, content FROM memories')
        
        for row in cursor.fetchall():
            vector = self._text_to_vector(row['content'])
            self.memory_vectors[row['id']] = vector
    
    def cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """计算余弦相似度"""
        return np.dot(v1, v2)
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """语义搜索"""
        query_vector = self._text_to_vector(query)
        
        results = []
        for memory_id, mem_vector in self.memory_vectors.items():
            similarity = self.cosine_similarity(query_vector, mem_vector)
            if similarity > 0.1:  # 阈值
                results.append({
                    'id': memory_id,
                    'similarity': similarity
                })
        
        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # 获取完整信息
        enriched_results = []
        for r in results[:top_k]:
            cursor = self.mf.conn.cursor()
            cursor.execute('SELECT * FROM memories WHERE id = ?', (r['id'],))
            row = cursor.fetchone()
            
            if row:
                enriched_results.append({
                    **dict(row),
                    'similarity': r['similarity']
                })
        
        return enriched_results
    
    def find_similar(self, memory_id: str, top_k: int = 5) -> List[Dict]:
        """找到相似的记忆"""
        if memory_id not in self.memory_vectors:
            return []
        
        source_vector = self.memory_vectors[memory_id]
        
        results = []
        for mid, mvector in self.memory_vectors.items():
            if mid != memory_id:
                sim = self.cosine_similarity(source_vector, mvector)
                if sim > 0.3:
                    results.append({
                        'id': mid,
                        'similarity': sim
                    })
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # 获取完整信息
        enriched = []
        for r in results[:top_k]:
            cursor = self.mf.conn.cursor()
            cursor.execute('SELECT * FROM memories WHERE id = ?', (r['id'],))
            row = cursor.fetchone()
            if row:
                enriched.append({**dict(row), 'similarity': r['similarity']})
        
        return enriched
    
    def close(self):
        self.mf.close()


def main():
    """CLI入口"""
    import sys
    
    search = SemanticSearch()
    
    if len(sys.argv) < 2:
        print("语义搜索引擎")
        print("\nCommands:")
        print("  search <query>    语义搜索")
        print("  similar <id>      找相似记忆")
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'search':
        if len(sys.argv) < 3:
            print("Usage: search <query>")
            return
        
        query = sys.argv[2]
        results = search.search(query, top_k=10)
        
        print(f"\n🔍 语义搜索: '{query}'")
        print(f"找到 {len(results)} 个结果:\n")
        
        for i, r in enumerate(results, 1):
            sim_pct = r['similarity'] * 100
            print(f"{i}. [{sim_pct:.1f}%] {r['summary'][:50]}...")
            print(f"   ID: {r['id']}")
            print()
    
    elif cmd == 'similar':
        if len(sys.argv) < 3:
            print("Usage: similar <memory_id>")
            return
        
        memory_id = sys.argv[2]
        results = search.find_similar(memory_id, top_k=5)
        
        print(f"\n💡 与 {memory_id} 相似的记忆:\n")
        for r in results:
            sim_pct = r['similarity'] * 100
            print(f"[{sim_pct:.1f}%] {r['summary'][:50]}...")
            print(f"   ID: {r['id']}")
            print()
    
    search.close()


if __name__ == '__main__':
    main()
