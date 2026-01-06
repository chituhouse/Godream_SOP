# 对话记录存档

> 更新时间: 2026-01-06

## 目录结构

```
conversations/
├── claude/                   # Claude Code 对话记录
│   ├── gemeng2/              # gemeng2 项目会话 (273个文件)
│   └── history/              # 全局历史记录
│       └── history.jsonl
├── codex/                    # Codex CLI 对话记录
│   ├── archived_sessions/    # 归档会话 (115MB)
│   ├── sessions/             # 当前会话 (164MB)
│   └── history.jsonl         # 全局历史记录
└── serena/                   # Serena 代码分析日志
```

## 数据统计

### Claude Code
- **gemeng2 项目**: 273 个会话文件
- **历史记录**: 1053 行 (history.jsonl)
- **总大小**: ~295MB

### Codex CLI
- **归档会话**: ~115MB (67 个会话)
- **当前会话**: ~164MB (按日期组织)
- **历史记录**: 1391 行 (history.jsonl)
- **总大小**: ~280MB

## 数据说明

### Claude Code 会话格式
每个会话以 `.jsonl` 格式存储，包含：
- 用户消息
- Claude 响应
- 工具调用记录
- 上下文信息

### Codex 会话格式
会话按日期组织 (YYYY/MM/DD)，每个会话包含：
- 对话历史
- 代码生成记录
- 执行结果

## 查看指南

### 查看 Claude Code 会话
```bash
# 查看特定会话
cat conversations/claude/gemeng2/<session-id>.jsonl | python -m json.tool

# 搜索关键词
grep -r "关键词" conversations/claude/gemeng2/
```

### 查看 Codex 会话
```bash
# 查看最近的会话
ls -lt conversations/codex/sessions/2026/01/ | head -10

# 查看特定会话
cat conversations/codex/sessions/2026/01/06/<session-file>.jsonl | python -m json.tool
```

## 时间范围

- **Claude Code**: 2025-09 ~ 2026-01
- **Codex**: 2025-08 ~ 2026-01

## 注意事项

1. **敏感信息**: 对话记录可能包含 API 密钥、配置信息等敏感数据，请勿公开
2. **文件格式**: 所有对话均为 JSONL 格式 (JSON Lines)
3. **完整性**: 包含完整的开发历程，从项目启动到当前版本

---

*创建时间: 2026-01-06*
*数据来源: ~/.codex 和 ~/.claude*
