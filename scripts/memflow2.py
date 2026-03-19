#!/usr/bin/env python3
"""
MemoFlow 2.0 - 深度融合实现 (SQLite版)
API兼容Dolt，后续可无缝迁移
"""

import sqlite3
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

DB_PATH = Path.home() / "Documents/claw_memory/memflow2/memflow2.db"
DAILY_DIR = Path.home() / "Documents/claw_memory/daily"

class MemoFlow2:
    """MemoFlow 2.0 - 图数据库版记忆系统"""
    
    RELATIONS = {
        'depends_on': '依赖',
        'relates_to': '相关', 
        'supersedes': '替代',
        'duplicates': '重复',
        'replies_to': '回复',
        'parent_of': '父主题',
        'child_of': '子主题'
    }
    
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(DB_PATH))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
    
    def _init_schema(self):
        """初始化数据库表结构"""
        cursor = self.conn.cursor()
        
        # 记忆节点表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            room TEXT,
            emotion TEXT,
            category TEXT DEFAULT 'knowledge',
            parent_id TEXT,
            depth INTEGER DEFAULT 0,
            source TEXT,
            confidence REAL,
            embedding BLOB,
            filename TEXT
        )
        ''')
        
        # 记忆关系表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_id TEXT NOT NULL,
            to_id TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            strength REAL DEFAULT 1.0,
            ai_generated INTEGER DEFAULT 0,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(from_id, to_id, relation_type)
        )
        ''')
        
        # 标签表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_tags (
            memory_id TEXT,
            tag TEXT,
            confidence REAL,
            PRIMARY KEY (memory_id, tag)
        )
        ''')
        
        # 访问日志
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_id TEXT,
            access_type TEXT,
            context TEXT,
            accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_room ON memories(room)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_emotion ON memories(emotion)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relations_from ON memory_relations(from_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relations_to ON memory_relations(to_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relations_type ON memory_relations(relation_type)')
        
        self.conn.commit()
        print("✅ 数据库初始化完成")
    
    def _generate_id(self, content: str) -> str:
        """生成短哈希ID (beads风格)"""
        hash_obj = hashlib.md5(content.encode())
        return f"mf-{hash_obj.hexdigest()[:6]}"
    
    def migrate_from_markdown(self):
        """从 Markdown 文件迁移数据"""
        if not DAILY_DIR.exists():
            print("❌ 未找到记忆目录")
            return
        
        cursor = self.conn.cursor()
        count = 0
        
        for md_file in DAILY_DIR.glob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                memory_id = self._generate_id(content)
                
                # 提取标题
                title = md_file.stem
                if '_' in title:
                    parts = title.split('_', 2)
                    if len(parts) >= 3:
                        title = parts[2]
                
                # 检查是否已存在
                cursor.execute('SELECT id FROM memories WHERE id = ?', (memory_id,))
                if cursor.fetchone():
                    continue
                
                # 提取元数据
                import re
                room_match = re.search(r'\*分类:\s*(\w+)\*', content)
                room = room_match.group(1) if room_match else 'living'
                
                # 插入记忆
                cursor.execute('''
                INSERT INTO memories (id, content, summary, room, filename, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    memory_id,
                    content,
                    title[:200],
                    room,
                    md_file.name,
                    datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                ))
                
                count += 1
                
            except Exception as e:
                print(f"⚠️ 跳过 {md_file}: {e}")
        
        self.conn.commit()
        print(f"✅ 迁移完成: {count} 条记忆")
    
    def add_memory(self, content: str, room: str = 'living', emotion: str = None,
                   category: str = 'knowledge', parent_id: str = None) -> str:
        """添加新记忆"""
        memory_id = self._generate_id(content)
        
        # 计算层级深度
        depth = 0
        if parent_id:
            cursor = self.conn.cursor()
            cursor.execute('SELECT depth FROM memories WHERE id = ?', (parent_id,))
            row = cursor.fetchone()
            if row:
                depth = row[0] + 1
        
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO memories 
        (id, content, summary, room, emotion, category, parent_id, depth, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory_id,
            content,
            content[:200],
            room,
            emotion,
            category,
            parent_id,
            depth,
            datetime.now().isoformat()
        ))
        
        self.conn.commit()
        return memory_id
    
    def link_memories(self, from_id: str, to_id: str, relation: str, 
                      strength: float = 1.0, note: str = "") -> bool:
        """建立记忆关系"""
        if relation not in self.RELATIONS:
            print(f"❌ 未知关系类型: {relation}")
            return False
        
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO memory_relations 
            (from_id, to_id, relation_type, strength, note)
            VALUES (?, ?, ?, ?, ?)
            ''', (from_id, to_id, relation, strength, note))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ 建立关系失败: {e}")
            return False
    
    def find_related(self, memory_id: str, relation_type: str = None) -> List[Dict]:
        """查找相关记忆"""
        cursor = self.conn.cursor()
        
        query = '''
        SELECT m.*, r.relation_type, r.strength, r.note, 'outgoing' as direction
        FROM memories m
        JOIN memory_relations r ON m.id = r.to_id
        WHERE r.from_id = ?
        '''
        params = [memory_id]
        
        if relation_type:
            query += ' AND r.relation_type = ?'
            params.append(relation_type)
        
        query += '''
        UNION ALL
        SELECT m.*, r.relation_type, r.strength, r.note, 'incoming' as direction
        FROM memories m
        JOIN memory_relations r ON m.id = r.from_id
        WHERE r.to_id = ?
        '''
        params.append(memory_id)
        
        if relation_type:
            query += ' AND r.relation_type = ?'
            params.append(relation_type)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def search(self, keyword: str, limit: int = 10) -> List[Dict]:
        """搜索记忆"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT *, 
               (CASE WHEN summary LIKE ? THEN 2 ELSE 1 END +
                CASE WHEN content LIKE ? THEN 1 ELSE 0 END) as relevance
        FROM memories
        WHERE summary LIKE ? OR content LIKE ?
        ORDER BY relevance DESC, created_at DESC
        LIMIT ?
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_memory_graph(self, memory_id: str, depth: int = 2) -> Dict:
        """获取记忆图谱（BFS遍历）"""
        visited = {memory_id}
        result = {'nodes': [], 'edges': []}
        queue = [(memory_id, 0)]
        
        cursor = self.conn.cursor()
        
        while queue:
            current_id, current_depth = queue.pop(0)
            
            if current_depth > depth:
                continue
            
            # 获取节点信息
            cursor.execute('SELECT * FROM memories WHERE id = ?', (current_id,))
            node = cursor.fetchone()
            if node:
                result['nodes'].append(dict(node))
            
            # 获取关联边
            cursor.execute('''
            SELECT * FROM memory_relations 
            WHERE from_id = ? OR to_id = ?
            ''', (current_id, current_id))
            
            for row in cursor.fetchall():
                edge = dict(row)
                result['edges'].append(edge)
                
                # 加入队列继续遍历
                next_id = edge['to_id'] if edge['from_id'] == current_id else edge['from_id']
                if next_id not in visited:
                    visited.add(next_id)
                    queue.append((next_id, current_depth + 1))
        
        return result
    
    def stats(self) -> Dict:
        """统计信息"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM memories')
        memory_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM memory_relations')
        relation_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT room, COUNT(*) FROM memories GROUP BY room')
        room_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        return {
            'memories': memory_count,
            'relations': relation_count,
            'rooms': room_stats
        }
    
    def close(self):
        """关闭连接"""
        self.conn.close()


def main():
    """CLI入口"""
    import sys
    
    mf = MemoFlow2()
    
    if len(sys.argv) < 2:
        print("MemoFlow 2.0 - 深度融合记忆系统")
        print("\nCommands:")
        print("  migrate          从 Markdown 迁移数据")
        print("  search <keyword> 搜索记忆")
        print("  stats            显示统计")
        print("  graph <id>       显示记忆图谱")
        print("\nExample:")
        print("  python memflow2.py migrate")
        print("  python memflow2.py search BANK-AI")
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'migrate':
        mf.migrate_from_markdown()
    elif cmd == 'search':
        if len(sys.argv) < 3:
            print("Usage: search <keyword>")
            return
        results = mf.search(sys.argv[2])
        print(f"\n🔍 找到 {len(results)} 条记忆:\n")
        for r in results:
            print(f"📄 {r['summary'][:60]}...")
            print(f"   ID: {r['id']} | 房间: {r['room']}")
            print()
    elif cmd == 'stats':
        stats = mf.stats()
        print(f"\n📊 MemoFlow 2.0 统计")
        print(f"=" * 40)
        print(f"记忆节点: {stats['memories']}")
        print(f"关系边: {stats['relations']}")
        print(f"\n房间分布:")
        for room, count in stats['rooms'].items():
            print(f"  {room}: {count}")
    elif cmd == 'graph':
        if len(sys.argv) < 3:
            print("Usage: graph <memory_id>")
            return
        graph = mf.get_memory_graph(sys.argv[2])
        print(f"\n🕸️ 记忆图谱")
        print(f"节点: {len(graph['nodes'])}")
        print(f"边: {len(graph['edges'])}")
    else:
        print(f"Unknown command: {cmd}")
    
    mf.close()


if __name__ == '__main__':
    main()
