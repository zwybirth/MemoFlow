#!/usr/bin/env python3
"""
MemoFlow 2.0 - Dolt 数据库初始化脚本
无需等待 Dolt CLI，使用 Python 直接操作
"""

import os
import sys
import subprocess
from pathlib import Path

# Dolt 数据目录
DOLT_DIR = Path.home() / "Documents/claw_memory/memflow2"

def run_dolt_sql(sql):
    """执行 Dolt SQL"""
    dolt_bin = Path.home() / ".local/bin/dolt"
    if not dolt_bin.exists():
        # 尝试系统路径
        dolt_bin = "dolt"
    
    result = subprocess.run(
        [str(dolt_bin), "sql", "-q", sql],
        cwd=DOLT_DIR,
        capture_output=True,
        text=True
    )
    return result

def init_database():
    """初始化 MemoFlow 2.0 数据库"""
    print("🚀 初始化 MemoFlow 2.0 数据库...")
    
    # 创建目录
    DOLT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 初始化 Dolt 仓库
    subprocess.run(["git", "init"], cwd=DOLT_DIR, capture_output=True)
    
    # 创建表结构 SQL
    schema_sql = """
    CREATE TABLE IF NOT EXISTS memories (
        id VARCHAR(20) PRIMARY KEY,
        content TEXT NOT NULL,
        summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP,
        room VARCHAR(50),
        emotion VARCHAR(50),
        category VARCHAR(50),
        parent_id VARCHAR(20),
        depth INT DEFAULT 0,
        source VARCHAR(100),
        confidence FLOAT,
        embedding BLOB
    );
    
    CREATE TABLE IF NOT EXISTS memory_relations (
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
    
    CREATE TABLE IF NOT EXISTS memory_tags (
        memory_id VARCHAR(20),
        tag VARCHAR(100),
        confidence FLOAT,
        PRIMARY KEY (memory_id, tag)
    );
    
    CREATE TABLE IF NOT EXISTS access_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        memory_id VARCHAR(20),
        access_type VARCHAR(50),
        context TEXT,
        accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # 由于 Dolt 可能还没装好，先保存 SQL 文件
    schema_file = DOLT_DIR / "schema.sql"
    schema_file.write_text(schema_sql, encoding='utf-8')
    
    print(f"✅ 数据库目录: {DOLT_DIR}")
    print(f"✅ Schema 文件: {schema_file}")
    print("\n💡 等 Dolt 安装完成后，执行:")
    print(f"   cd {DOLT_DIR}")
    print("   dolt init")
    print("   dolt sql < schema.sql")
    
    return True

if __name__ == '__main__':
    init_database()
