# 🌊 MemoFlow

> 让记忆流动起来的智能记忆管理系统
> 
> Memories Flow, Knowledge Grows

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Compatible-green.svg)](https://openclaw.ai)

---

## ✨ 核心特性

### 🎯 自动驾驶模式
- **自动保存**：智能识别重要对话并自动保存
- **自动检索**：根据上下文主动回忆相关记忆
- **智能过滤**：自动过滤闲聊，保留精华

### 🏛️ 记忆宫殿
- **7个房间**：书房、卧室、客厅、厨房、车库、会议室、画室
- **情绪驱动**：根据情绪自动分配到最适合的房间
- **可视化**：HTML交互式记忆地图

### 🎭 情绪记忆
- **8种情绪**：兴奋、愉快、思考、焦虑、沮丧、顿悟、创意、平静
- **自动分析**：AI自动识别对话情绪
- **情绪导航**：按情绪状态检索记忆

### 🔄 统一入口
```bash
mem save --content "..." --auto    # 一键保存到所有子系统
mem search "..."                   # 跨系统检索
mem stats                          # 查看系统状态
```

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/MemoFlow.git
cd MemoFlow

# 安装依赖
pip install -r requirements.txt

# 初始化
./install.sh
```

### 基础使用

```bash
# 自动模式（推荐）
mem save --content "今天完成了一个功能" --auto

# 查看统计
mem stats

# 搜索记忆
mem search "项目"

# 可视化
mem palace --open
```

### 自动驾驶模式

开启后，**正常对话即可**，MemoFlow自动工作：

```bash
# 启用自动模式
export MEMOFLOW_AUTO=1

# 对话示例
你: "突然想到一个关于BANK-AI的新方案"
AI: [自动保存 + 检索相关记忆 + 融入回复]
```

---

## 🏗️ 架构

```
MemoFlow
├── 📝 基础层 (LOCAL-MEM)      - 完整存储
├── 🎭 情绪层 (Emotional)      - 8种情绪
├── 🏛️ 宫殿层 (Memory Palace)  - 7个房间
└── 🌊 统一入口 (mem)         - 一键操作
```

---

## 📊 效果展示

```bash
$ mem stats

📊 MemoFlow 系统状态
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 基础层记忆: 153 条
🏛️ 宫殿层记忆: 13 条
   📚 书房: 7 条
   🛏️ 卧室: 3 条
   🍳 厨房: 1 条
   💼 会议室: 2 条
🎭 情绪类型: 8 种
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🛠️ 配置

### 环境变量

```bash
export MEMOFLOW_HOME="$HOME/.memoflow"
export MEMOFLOW_AUTO=1              # 启用自动模式
export MEMOFLOW_PALACE="$HOME/Documents/memoflow"
```

### 自动恢复

```bash
# macOS LaunchAgent (开机自启)
cp config/com.openclaw.memoflow.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.openclaw.memoflow.plist

# Shell 集成 (新会话自动加载)
echo 'source ~/.memoflow/memoflow_auto_env.sh' >> ~/.zshrc
```

---

## 📚 文档

- [安装指南](docs/INSTALL.md)
- [使用手册](docs/USAGE.md)
- [架构设计](docs/ARCHITECTURE.md)
- [API文档](docs/API.md)
- [贡献指南](docs/CONTRIBUTING.md)

---

## 🎯 使用场景

### 个人知识管理
```bash
# 学习笔记
mem save --content "学习了PyTorch的自动微分..." --room 书房

# 灵感记录
mem save --content "突然想到一个产品创意..." --auto
```

### 项目管理
```bash
# 决策记录
mem save --content "决定采用微服务架构..." --room 会议室

# 进度跟踪
mem save --content "完成了用户认证模块..." --auto
```

### 情绪日记
```bash
# 记录心情
mem save --content "今天压力很大..." --auto

# 查看情绪分布
mem emotions
```

---

## 🌟 核心优势

| 特性 | MemoFlow | 传统笔记 | 普通数据库 |
|------|----------|----------|------------|
| 自动保存 | ✅ | ❌ | ❌ |
| 情绪标记 | ✅ | ❌ | ❌ |
| 空间组织 | ✅ 7房间 | ❌ | ❌ |
| 自动检索 | ✅ | ❌ | ❌ |
| 可视化 | ✅ | ❌ | ❌ |

---

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](docs/CONTRIBUTING.md)

### 开发

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/

# 代码检查
flake8 src/
black src/
```

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

- 灵感来源：记忆宫殿法、情绪日记
- 技术栈：Python, SQLite, OpenClaw
- 贡献者：感谢所有贡献代码和建议的朋友

---

## 🔗 相关链接

- [OpenClaw](https://openclaw.ai)
- [记忆宫殿法](https://en.wikipedia.org/wiki/Method_of_loci)
- [项目Wiki](https://github.com/yourusername/MemoFlow/wiki)

---

**🌊 让记忆流动起来**

*Memories Flow, Knowledge Grows*
