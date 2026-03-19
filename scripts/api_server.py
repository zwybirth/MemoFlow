#!/usr/bin/env python3
"""
MemoFlow 2.0 - 可视化API服务器
为D3.js图谱提供数据
"""

import sys
sys.path.insert(0, '~/.openclaw/workspace/skills/memflow-v2')

import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from memflow2 import MemoFlow2

class GraphAPIHandler(SimpleHTTPRequestHandler):
    mf = MemoFlow2()  # 类变量，所有实例共享
    
    def do_GET(self):
        # CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        if self.path == '/api/graph':
            self.send_graph_data()
        elif self.path == '/api/stats':
            self.send_stats()
        elif self.path == '/api/memories':
            self.send_memories()
        else:
            super().do_GET()
    
    def send_graph_data(self):
        """发送图谱数据"""
        cursor = self.mf.conn.cursor()
        
        # 获取所有记忆节点
        cursor.execute('SELECT id, summary as title, room, emotion FROM memories')
        nodes = []
        for row in cursor.fetchall():
            nodes.append({
                'id': row['id'],
                'title': row['title'][:30] + '...' if len(row['title']) > 30 else row['title'],
                'room': row['room'] or 'living',
                'emotion': row['emotion'],
                'radius': 15 + (len(row['title']) % 10)  # 根据内容长度调整大小
            })
        
        # 获取所有关系边
        cursor.execute('SELECT from_id, to_id, relation_type FROM memory_relations')
        links = []
        for row in cursor.fetchall():
            links.append({
                'source': row['from_id'],
                'target': row['to_id'],
                'type': row['relation_type']
            })
        
        data = {'nodes': nodes, 'links': links}
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def send_stats(self):
        """发送统计信息"""
        stats = self.mf.stats()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(stats, ensure_ascii=False).encode())
    
    def send_memories(self):
        """发送所有记忆"""
        cursor = self.mf.conn.cursor()
        cursor.execute('SELECT id, summary, room, created_at FROM memories ORDER BY created_at DESC LIMIT 100')
        memories = [dict(row) for row in cursor.fetchall()]
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(memories, ensure_ascii=False).encode())
    
    def log_message(self, format, *args):
        pass  # 静默日志

if __name__ == '__main__':
    import socket
    from pathlib import Path
    
    # 找到可用端口
    def find_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            return s.getsockname()[1]
    
    PORT = find_free_port()
    server = HTTPServer(('127.0.0.1', PORT), GraphAPIHandler)
    
    # 写入端口文件供前端读取
    port_file = Path.home() / '.openclaw/workspace/skills/memflow-v2/api_port.txt'
    port_file.write_text(str(PORT))
    
    print(f"PORT:{PORT}")  # 输出端口供脚本捕获
    print(f"🚀 MemoFlow 2.0 API服务器启动: http://127.0.0.1:{PORT}")
    print(f"📊 图谱数据: http://127.0.0.1:{PORT}/api/graph")
    print(f"📈 统计信息: http://127.0.0.1:{PORT}/api/stats")
    server.serve_forever()
