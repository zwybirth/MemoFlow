#!/usr/bin/env python3
"""
MemoFlow 2.0 - SQLite 到 Dolt 迁移工具
API兼容，可无缝切换
"""

import sys
sys.path.insert(0, '~/.openclaw/workspace/skills/memflow-v2')

import sqlite3
import subprocess
from pathlib import Path
from memflow2 import MemoFlow2, DB_PATH

# Dolt 数据库目录
DOLT_DIR = Path.home() / "Documents/claw_memory/memflow2-dolt"

class DoltMigrator:
    """SQLite 到 Dolt 迁移器"""
    
    SQLITE_TO_DOLT_TYPES = {
        'TEXT': 'TEXT',
        'INTEGER': 'INT',
        'REAL': 'FLOAT',
        'BLOB': 'BLOB',
        'TIMESTAMP': 'TIMESTAMP'
    }
    
    def __init__(self):
        self.sqlite_conn = sqlite3.connect(str(DB_PATH))
        self.sqlite_conn.row_factory = sqlite3.Row
        DOLT_DIR.mkdir(parents=True, exist_ok=True)
    
    def generate_dolt_schema(self) -> str:
        """生成 Dolt 兼容的 SQL Schema"""
        
        schema = """
-- MemoFlow 2.0 Dolt Schema
-- 与 SQLite 版本 API 兼容

CREATE TABLE memories (
    id VARCHAR(20) PRIMARY KEY,
    content TEXT NOT NULL,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    room VARCHAR(50),
    emotion VARCHAR(50),
    category VARCHAR(50) DEFAULT 'knowledge',
    parent_id VARCHAR(20),
    depth INT DEFAULT 0,
    source VARCHAR(100),
    confidence FLOAT,
    embedding BLOB,
    filename TEXT
);

CREATE TABLE memory_relations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    from_id VARCHAR(20) NOT NULL,
    to_id VARCHAR(20) NOT NULL,
    relation_type VARCHAR(50) NOT NULL,
    strength FLOAT DEFAULT 1.0,
    ai_generated BOOLEAN DEFAULT FALSE,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_relation (from_id, to_id, relation_type)
);

CREATE TABLE memory_tags (
    memory_id VARCHAR(20),
    tag VARCHAR(100),
    confidence FLOAT,
    PRIMARY KEY (memory_id, tag)
);

CREATE TABLE access_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    memory_id VARCHAR(20),
    access_type VARCHAR(50),
    context TEXT,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_memories_room ON memories(room);
CREATE INDEX idx_memories_emotion ON memories(emotion);
CREATE INDEX idx_memories_created ON memories(created_at);
CREATE INDEX idx_relations_from ON memory_relations(from_id);
CREATE INDEX idx_relations_to ON memory_relations(to_id);
CREATE INDEX idx_relations_type ON memory_relations(relation_type);
"""
        return schema
    
    def export_to_sql(self) -> str:
        """导出 SQLite 数据为 SQL"""
        sql_statements = []
        cursor = self.sqlite_conn.cursor()
        
        def format_value(v):
            if v is None:
                return 'NULL'
            elif isinstance(v, str):
                # 转义单引号
                escaped = v.replace("'", "''")
                return f"'{escaped}'"
            else:
                return str(v)
        
        # 导出 memories
        cursor.execute('SELECT * FROM memories')
        columns = [d[0] for d in cursor.description]
        for row in cursor.fetchall():
            values = [format_value(row[i]) for i in range(len(columns))]
            sql = f"INSERT INTO memories ({', '.join(columns)}) VALUES ({', '.join(values)});"
            sql_statements.append(sql)
        
        # 导出 relations
        cursor.execute('SELECT * FROM memory_relations')
        columns = [d[0] for d in cursor.description]
        for row in cursor.fetchall():
            values = [format_value(row[i]) for i in range(len(columns))]
            sql = f"INSERT INTO memory_relations ({', '.join(columns)}) VALUES ({', '.join(values)});"
            sql_statements.append(sql)
        
        # 导出 tags
        cursor.execute('SELECT * FROM memory_tags')
        columns = [d[0] for d in cursor.description]
        for row in cursor.fetchall():
            values = [format_value(row[i]) for i in range(len(columns))]
            sql = f"INSERT INTO memory_tags ({', '.join(columns)}) VALUES ({', '.join(values)});"
            sql_statements.append(sql)
        
        return '\n'.join(sql_statements)
    
    def create_migration_package(self):
        """创建完整的迁移包"""
        
        print("📦 创建 Dolt 迁移包...")
        
        # 1. 生成 Schema
        schema = self.generate_dolt_schema()
        schema_file = DOLT_DIR / "schema.sql"
        schema_file.write_text(schema, encoding='utf-8')
        print(f"✅ Schema: {schema_file}")
        
        # 2. 导出数据
        data_sql = self.export_to_sql()
        data_file = DOLT_DIR / "data.sql"
        data_file.write_text(data_sql, encoding='utf-8')
        print(f"✅ 数据导出: {data_file}")
        
        # 3. 创建迁移脚本
        migrate_script = f"""#!/bin/bash
# MemoFlow 2.0 Dolt 迁移脚本

echo "🚀 开始 Dolt 迁移..."

# 1. 初始化 Dolt 仓库
cd {DOLT_DIR}
dolt init

# 2. 创建数据库
dolt sql < schema.sql

# 3. 导入数据
dolt sql < data.sql

# 4. 提交初始版本
dolt add .
dolt commit -m "Initial import from SQLite"

echo "✅ 迁移完成！"
echo ""
echo "使用方式:"
echo "  cd {DOLT_DIR}"
echo "  dolt sql -q 'SELECT * FROM memories LIMIT 5;'"
"""
        script_file = DOLT_DIR / "migrate.sh"
        script_file.write_text(migrate_script, encoding='utf-8')
        script_file.chmod(0o755)
        print(f"✅ 迁移脚本: {script_file}")
        
        # 4. 创建 README
        readme = f"""# MemoFlow 2.0 Dolt 迁移包

## 统计
- 记忆节点: {self.get_count('memories')}
- 关系边: {self.get_count('memory_relations')}
- 标签: {self.get_count('memory_tags')}

## 迁移步骤

### 方法1: 自动脚本
```bash
cd {DOLT_DIR}
./migrate.sh
```

### 方法2: 手动执行
```bash
cd {DOLT_DIR}

# 1. 初始化
dolt init

# 2. 导入 Schema
dolt sql < schema.sql

# 3. 导入数据
dolt sql < data.sql

# 4. 提交
dolt add .
dolt commit -m "Initial import"
```

## 验证
```bash
# 检查数据
dolt sql -q "SELECT COUNT(*) FROM memories;"
dolt sql -q "SELECT COUNT(*) FROM memory_relations;"

# 查看表结构
dolt schema show memories
```

## API 兼容性
SQLite 和 Dolt 版本使用完全相同的 Python API：
```python
from memflow2 import MemoFlow2  # 自动检测后端

mf = MemoFlow2()
# 所有操作与 SQLite 版本完全一致
```
"""
        readme_file = DOLT_DIR / "README.md"
        readme_file.write_text(readme, encoding='utf-8')
        print(f"✅ 说明文档: {readme_file}")
        
        print(f"\n📁 迁移包位置: {DOLT_DIR}")
        print("\n💡 安装 Dolt 后执行:")
        print(f"   cd {DOLT_DIR}")
        print("   ./migrate.sh")
    
    def get_count(self, table: str) -> int:
        """获取表记录数"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        return cursor.fetchone()[0]
    
    def close(self):
        self.sqlite_conn.close()


def main():
    """CLI入口"""
    print("🔄 MemoFlow 2.0 Dolt 迁移工具")
    print("=" * 50)
    
    migrator = DoltMigrator()
    
    # 显示统计
    print(f"\n当前 SQLite 数据库统计:")
    print(f"  记忆节点: {migrator.get_count('memories')}")
    print(f"  关系边: {migrator.get_count('memory_relations')}")
    print(f"  标签: {migrator.get_count('memory_tags')}")
    
    # 创建迁移包
    print("\n" + "=" * 50)
    migrator.create_migration_package()
    
    migrator.close()
    
    print("\n✅ 迁移包创建完成！")
    print("\n下一步:")
    print("1. 安装 Dolt: brew install dolt")
    print(f"2. cd {DOLT_DIR}")
    print("3. ./migrate.sh")


if __name__ == '__main__':
    main()
