#!/bin/bash
#
# MemoFlow 基础使用示例
#

echo "🌊 MemoFlow 使用示例"
echo "===================="

# 示例1: 自动保存
echo -e "\n1. 自动保存记忆"
mem save --content "今天完成了MemoFlow的自动保存功能" --auto

# 示例2: 指定房间
echo -e "\n2. 保存到指定房间"
mem save --content "学习了新的设计模式" --room 书房

# 示例3: 指定情绪
echo -e "\n3. 保存并指定情绪"
mem save --content "突然想到一个产品创意！" --emotion insight --intensity 9

# 示例4: 搜索记忆
echo -e "\n4. 搜索记忆"
mem search "设计模式"

# 示例5: 查看统计
echo -e "\n5. 查看系统统计"
mem stats

echo -e "\n✅ 示例完成！"
