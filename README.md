# Godream SOP - 项目开发历程存档

> **警告**: 本仓库包含敏感开发对话记录，仅供内部参考，请勿公开。

## 项目概述

本仓库存档了鸽梦 (GoDream) 项目从 v0.0.3 到 v1.9.0 的完整开发历程，包括：

- **开发周期**: 2025年8月18日 ~ 2026年1月11日 (约5个月)
- **Git提交数**: 400+
- **版本迭代**: 45+ 个标记版本
- **对话记录**: ~320MB（原始 jsonl/txt）
- **营销物料**: 官网备份版 + 公众号文章 + 销售资料（用于"火山销售转发即用"）

## 目录结构

```
Godream_SOP/
├── README.md                    # 本文档
├── timeline.md                  # 版本演化时间线
├── conversations/               # 对话记录存档
│   ├── claude/                  # Claude Code 对话 (144MB)
│   ├── codex/                   # Codex 会话 (118MB)
│   └── serena/                  # Serena 日志 (22MB)
├── readable/                    # 可读格式摘要
│   ├── key-decisions.md         # 关键技术决策
│   ├── lessons-learned.md       # 经验教训
│   └── milestones.md            # 里程碑记录
├── marketing/                   # 对外物料（私有）
│   ├── 00_对外口径真源.md        # 对外口径真源（单一真源）
│   ├── website/                 # 官网备份版（文案/结构/动效/原型）
│   ├── wechat/                  # 公众号文章体系（发布稿/功能稿/场景稿/FAQ）
│   └── sales/                   # 销售资料包（one-pager/pitch/话术/培训）
├── sop/                         # 标准操作流程
│   ├── development-workflow.md  # 开发工作流
│   ├── packaging-guide.md       # 打包指南
│   └── debugging-guide.md       # 调试指南
└── analysis/                    # 未来数据分析
    ├── claude_jsonl_to_md.py     # Claude jsonl → Markdown 可读导出
    └── build_conversation_index.py # 生成对话索引（机器可读 + Markdown）
```

## 对话记录来源

| 来源 | 时间范围 | 文件数 | 主要内容 |
|------|----------|--------|----------|
| Claude Code | 2025-09 ~ 2026-01 | 480+ | 架构设计、重构、调试 |
| Codex | 2025-09 ~ 2026-01 | 217+ | 代码生成、批量修改 |
| Serena | 2025-09 ~ 2026-01 | 50+ | 代码分析、MCP交互 |

## 版本演化概览

| 阶段 | 版本 | 时间 | 主题 |
|------|------|------|------|
| 1 | v0.0.x~v0.1.x | 08-18~08-19 | API集成与基础功能验证 |
| 2 | v0.2.0~v0.3.91 | 08-20~08-24 | UI框架建立 (PyQt5) |
| 3 | v0.4.0~v0.5.0 | 08-24~08-25 | 配置管理与用户自定义 |
| 4 | v0.6.0~v0.8.1 | 08-28~09-19 | 存储系统完善 (CSV V2) |
| 5 | v1.0.0~v1.5.0 | 10-27~12-22 | 架构现代化 (SQLite + PySide6) |
| 6 | v1.6.0~v1.9.0 | 12-24~01-11 | 视频增强 (Seedance 1.5 Pro) + 功能稳定化 |

## 关键技术转折点

| 版本 | 转折点 | 影响 |
|------|--------|------|
| v0.6.0 | 路径同步 + 无限滚动 | 用户体验量级提升 |
| v0.8.0 | Seedream 4.0 + 多参考图 | 多源API协奏 |
| v1.2.0 | CSV → SQLite | 数据层性能跨越 |
| v1.5.0 | PyQt5 → PySide6 + Token主题 | 框架现代化完成 |
| v1.6.0 | Seedance 1.5 Pro + 视频增强 | 视频生态深化 |
| v1.8.x | 参考图路径优化 + 缓存修复 | 稳定性提升 |
| v1.9.0 | 视频参考图30MB限制提升 | 用户体验优化 |

## 使用说明

### 查看对话记录

Claude Code / Codex 对话主要以 `.jsonl` 存储（每个会话一个文件）。

### 搜索特定内容

```bash
# 在全仓库中搜索关键词（推荐）
rg "SQLite|PySide6|相对路径|NAS" .
```

### 生成对话索引（推荐先做）

```bash
python analysis/build_conversation_index.py
# 输出：
# sop/conversations/index.md
# sop/conversations/index.json
```

### 将 Claude jsonl 导出为可读 Markdown

```bash
python analysis/claude_jsonl_to_md.py conversations/claude/<session>.jsonl readable/claude/<session>.md
```

---

*创建时间: 2025-12-25*
*最后更新: 2026-01-11*
*主项目: [gemeng2](https://github.com/chituhouse/gemeng2)*
