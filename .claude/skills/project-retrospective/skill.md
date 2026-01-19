---
name: project-retrospective
description: 项目全量复盘 - 分析对话记录，发现认知边界，产出 SOP
version: 1.0.0
---

# /project-retrospective

对项目的完整对话记录进行全量分析，从 6 个视角建立索引，发现知识盲区，产出专业级 SOP。

## 使用方式

```
/project-retrospective [conversations_dir]
```

默认分析当前项目的 `conversations/` 目录。

## 执行流程

### 阶段 B：建立索引
1. 扫描 conversations/ 目录，识别所有对话文件
2. 按月份分配给 5 个 Agent 并行分析
3. 每个 Agent 从 6 个视角提取信息
4. 第 6 个 Agent 做跨月关联分析
5. 输出结构化索引到 analysis/overnight/

### 阶段 A：深度洞见
1. 基于索引筛选重点对话
2. 6 个 Agent 分主题深挖：
   - 巨石文件 & 上下文管理
   - UI 硬编码 & 主题系统
   - 性能卡顿 & 虚拟列表
   - Bug 反复改 & 回滚
   - 工具切换 & 模型演进
   - 知识盲区 & 学习路径
3. 产出 SOP 文档

## 6 个分析视角

1. **时间线与节奏** — 密集期、空白期、对话长度
2. **问题生命周期** — 跨会话问题、复发问题、解决/放弃
3. **用户思维模式** — 提问方式、表达习惯、直觉准确率
4. **情绪与决策** — 挫败点、突破点、妥协、放弃
5. **工具与技术演进** — 工具切换、技术栈变化
6. **知识盲区** — 本可以用的、绕远路的、后来学到的

## 输出物

```
analysis/overnight/
├── month_YYYY_MM.json     # 月度索引
├── cross_month.json       # 跨月关联
└── full_index.md          # 可读汇总

sop/
├── checklists/            # 检查清单
├── patterns/              # 最佳实践
├── anti-patterns/         # 反模式（踩坑）
├── evolution/             # 演进记录
└── retrospective/         # 月度复盘
```

## 配置文件

- `analysis/agent_instructions/agent_month_analysis.md` — 月度分析指令
- `analysis/agent_instructions/agent_cross_month.md` — 跨月分析指令
- `analysis/agent_instructions/output_schema.md` — 输出格式规范

## 适用场景

- 项目完成后的全面复盘
- 阶段性总结（季度/半年/年度）
- 新成员 onboarding（了解项目历史）
- 提炼可复用的经验教训
