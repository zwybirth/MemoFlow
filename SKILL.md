---
name: memflow
description: |
  MemoFlow - 三层流动的长期记忆系统。提供记忆存储、语义搜索、情绪识别、
  宫殿分类和图谱可视化功能。支持命令行统一入口 `mem` 操作所有记忆。
  
  功能包括：
  - 记忆保存与检索 (mem save/search)
  - 三层架构：基础层(daily)、宫殿层(7 rooms)、情绪层(8 emotions)
  - 智能关系推理与自动连接
  - D3.js 可视化交互页面
  - SQLite + Dolt 双存储引擎
  
  使用场景：需要长期记忆管理、知识图谱构建、项目进展追踪、
  决策记录和跨会话上下文保持时使用本技能。
license: MIT
---

# MemoFlow 记忆流系统

三层流动的长期记忆系统，跨会话持久化存储。

## 架构概览

```
┌─────────────────────────────────────┐
│         MemoFlow 记忆流             │
│      统一入口: mem                  │
├─────────────────────────────────────┤
│  💭 输入 → 🔄 流动 → 📦 存储       │
│                                     │
│  ┌─────────┐ ┌─────────┐           │
│  │ 情绪层  │ │ 宫殿层  │           │
│  │ 8种情绪 │ │ 7个房间 │           │
│  └────┬────┘ └────┬────┘           │
│       └─────┬─────┘                 │
│       ┌─────┴─────┐                 │
│       │  基础层   │                 │
│       └───────────┘                 │
└─────────────────────────────────────┘
```

## 核心命令

### 记忆操作
```bash
# 保存记忆
mem save --content "内容" --title "标题"

# 搜索记忆
mem search "关键词"

# 查看统计
mem stats

# 查看流动状态
mem flow
```

### 可视化
```bash
# 启动可视化服务器
cd ~/.openclaw/workspace/skills/memflow-v2 && python3 -m http.server 8080
# 访问 http://localhost:8080/visualization.html
```

## 三层存储架构

### 1. 基础层 (daily/)
- 位置：`~/Documents/claw_memory/daily/`
- 按日期存储的日常记忆
- 自动归档和汇总

### 2. 宫殿层 (palace/)
7个记忆房间，按主题分类：
- **kitchen** - 生活琐事、日常安排
- **study** - 学习笔记、技术文档
- **office** - 工作项目、会议纪要
- **garage** - 工具脚本、实验性内容
- **bedroom** - 个人思考、情绪记录
- **studio** - 创意内容、设计灵感
- **living** - 通用内容、默认归档

### 3. 情绪层 (emotional/)
8种情绪识别：
- joy, sadness, anger, fear
- surprise, disgust, neutral, thinking

## 技术栈

- **存储**: SQLite + Dolt (版本控制)
- **向量**: 语义嵌入 (预留接口)
- **可视化**: D3.js + 力导向图谱
- **API**: Python HTTP Server

## 数据文件位置

```
~/Documents/claw_memory/
├── memflow2/memflow2.db          # SQLite 主数据库
├── memflow2-dolt/                 # Dolt 版本控制
├── graph_data.json                # 可视化数据
└── daily/|palace/|emotional/      # 分类存储
```

## 代码位置

```
~/.openclaw/workspace/skills/memflow-v2/
├── memflow2.py           # 主入口
├── visualization.html    # D3.js 可视化
├── api_server.py         # API 服务器
├── ai_relation_engine.py # 关系推理
└── semantic_search.py    # 语义搜索
```

## 快速开始

1. **查看当前记忆统计**
   ```bash
   mem stats
   ```

2. **搜索历史记忆**
   ```bash
   mem search "BANK-AI"
   ```

3. **保存新记忆**
   ```bash
   mem save --content "项目里程碑完成" --title "BANK-AI Phase 3"
   ```

4. **打开可视化页面**
   ```bash
   # 启动服务器
   python3 -m http.server 8080 --directory ~/.openclaw/workspace/skills/memflow-v2
   
   # 浏览器访问
   open http://localhost:8080/visualization.html
   ```

## 高级功能

### 关系推理
系统自动分析记忆间的关联：
- `depends_on` - 依赖关系
- `relates_to` - 相关关系
- `supersedes` - 替代/更新
- `replies_to` - 回复关系

### 智能路由
根据内容自动分类到：
- 合适的宫殿房间
- 对应的情绪标签
- 相关的项目/主题

### 图谱可视化
- 拖拽调整布局
- 点击查看详情
- 滚轮缩放画布
- 搜索高亮节点

## 注意事项

- 记忆数据默认存储在 `~/Documents/claw_memory/`
- 可视化需要启动本地 HTTP 服务器
- 数据库文件较大时，首次加载可能需要几秒

## 相关技能

- [custom-memory](https://clawhub.com) - 备用本地记忆系统
- [mem0-integration](https://clawhub.com) - MEM0 云端记忆集成
