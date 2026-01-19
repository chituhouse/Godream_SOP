# SOP 踩坑记录与 Skill 缺口分析

> 基于核心踩坑文档分析，确定真正需要的 Skill 改进

---

## 一、8 个绕远路案例分类

| 案例 | 耗时 | 问题类型 | 现有 Skill 覆盖？ | 真正缺失的 | 解决方案 |
|-----|------|---------|----------------|----------|----------|
| 1. 缩略图显示改造 | 2-3h | **流程** | ✅ systematic-debugging | 缺"第一性原理"检查点 | 增强 systematic-debugging |
| 2. Codex 连接问题 | 20min | 工具 | ❌ | 工具故障排查清单 | **需要工具脚本**，非 skill |
| 3. 窗口缩放溢出 | 2-3h | **流程** | ✅ systematic-debugging | 缺"全局策略"检查点 | 增强 systematic-debugging |
| 4. latin-1 编码错误 | 2-3h | **流程** | ✅ systematic-debugging | 第一性原理已在 v2.0 添加 | ✅ 已覆盖 |
| 5. macOS 签名问题 | 30min | 知识 | ❌ | 不知道项目已有脚本 | **需要文档**，非 skill |
| 6. 参考图完整流程 | 2-3h | **流程** | ❌ | 系统性分析方法 | **需要新 skill** |
| 7. 按钮样式不稳定 | 2-3h | 知识 | ❌ | Qt 调试工具 | **需要文档**，非 skill |
| 8. 图片缩略图不显示 | 1h | 知识 | ✅ systematic-debugging | 应先用调试工具 | **需要文档**，非 skill |

### 分类统计

| 类型 | 数量 | 案例 | 解决方式 |
|-----|------|------|---------|
| **流程问题** | 3 | 1, 3, 6 | **增强/新建 skill** |
| 知识问题 | 3 | 5, 7, 8 | 文档/学习资源 |
| 工具问题 | 1 | 2 | 工具脚本 |
| 已覆盖 | 1 | 4 | 无需改进 |

---

## 二、真正需要的 Skill 优化（不重复）

### 1. 增强 systematic-debugging（Phase 1）

**缺失检查点**：
- **第一性原理检查**（案例 1, 4）
  - [ ] 问题描述是"症状"还是"根因"？
  - [ ] 如果改了多次仍未解决 → 停下来，用第一性原理重新分析
  - [ ] "为什么会发生"比"怎么绕过"更重要

- **全局策略检查**（案例 3）
  - [ ] 发现局部调整无效时 → 问"这个问题的本质是什么"
  - [ ] 是否需要统一策略而非逐个修复？
  - [ ] 示例：窗口缩放溢出 → 统一 `_fit_window_within_screen` 策略

**证据**：
- blind-spots.md 案例 1："缺乏第一性原理思维，AI 使用了隔靴搔痒的临时补丁"
- blind-spots.md 案例 3："没有从全局角度思考问题，而是逐个调整局部参数"
- bug-fix-workflow.md："问'为什么会发生'而非'怎么绕过去'"

**是否与现有配置重复**：
- No（systematic-debugging 目前只有"Root Cause Investigation"，缺少"第一性原理"和"全局策略"明确检查点）

---

### 2. 新建 code-understanding Skill（案例 6）

**缺失的完整流程**：
```
需要理解复杂代码流程时，必须系统性追踪：

Phase 1: 绘制数据流图
- [ ] 确定入口：UI 组件
- [ ] 追踪调用链：UI → Service → Storage → Database
- [ ] 标注关键路径和分支
- [ ] 用图表呈现（文本或工具）

Phase 2: 分层理解
- [ ] 表现层（UI）：用户交互如何触发
- [ ] 业务层（Service）：逻辑处理在哪里
- [ ] 持久层（Storage/DB）：数据如何存储

Phase 3: 验证理解
- [ ] 列出关键假设
- [ ] 找代码证据验证假设
- [ ] 发现矛盾 → 更新理解

避免：碎片化探索（分多个会话探索不同方面）
```

**证据**：
- blind-spots.md 案例 6："缺乏系统性分析方法，碎片化探索"
- "更好路径：一开始就画出数据流图，从 UI → Service → Storage → Database 完整追踪"

**是否与现有配置重复**：
- No（现有 skills 没有"代码理解"的系统性方法）

---

### 3. 增强 brainstorming（设计阶段检查）

**缺失检查点**：
```
设计方案时，必须评估：

架构设计检查：
- [ ] 数据流是否清晰？（原始数据 → 处理 → 存储 → 显示）
- [ ] 是否有不必要的开关/分叉？
- [ ] 缓存设计是否包含完整信息？
- [ ] 避免"先画方块再修正"的临时补丁

示例（案例 1）：
- ❌ 添加多个开关分叉 → 先画方块再修正 → 缓存不带尺寸信息
- ✅ 从一开始设计清晰的数据流：原始尺寸 → 缓存 → 显示
```

**证据**：
- blind-spots.md 案例 1："从一开始设计清晰的数据流：原始尺寸 → 缓存 → 显示"

**是否与现有配置重复**：
- Partially（brainstorming 有"架构、数据流"，但缺少"临时补丁检查"）

---

## 三、需要的工具（非 skill）

### 1. 硬编码扫描脚本

**解决问题**：自动发现硬编码样式（案例 7 间接相关）

**证据**：blind-spots.md LSP 能力："硬编码问题分散在多处，逐个发现效率低"

**实现方式**：
```bash
# scripts/scan_hardcoded_styles.sh
rg --type py "#[0-9A-Fa-f]{6}" src/  # 查找十六进制颜色
rg --type py "setFixedSize|setFixedWidth|setFixedHeight" src/  # 固定尺寸
```

**触发时机**：
- 手动运行：`./scripts/scan_hardcoded_styles.sh`
- 或在 pre-commit hook 中检查

---

### 2. MCP/工具连接检查脚本

**解决问题**：快速诊断 MCP 工具连接问题（案例 2）

**证据**：blind-spots.md 案例 2："17 分钟内反复输入 nihao/hello 测试连接（9次）"

**实现方式**：
```bash
# scripts/check_mcp_status.sh
# 1. 检查进程状态
ps aux | grep mcp

# 2. 检查日志
tail -n 50 ~/.mcp/logs/latest.log

# 3. 测试连接
curl http://localhost:PORT/health || echo "MCP 未启动"
```

---

## 四、需要的文档/培训（非 skill）

### 1. 项目工具清单（解决案例 5）

**缺失知识**：不知道项目已有脚本/工具

**补充方式**：
创建 `docs/project_tooling.md`：
```markdown
# 项目工具清单

## 打包脚本
- scripts/macos/build_macos_app.sh（macOS 签名打包）
- scripts/windows/build_windows.sh（Windows 打包）

## 开发工具
- /design-system（初始化 Token 系统）
- /dev（开发模式）

## 调试工具
- scripts/scan_hardcoded_styles.sh（硬编码扫描）
```

---

### 2. Qt 调试工具文档（解决案例 7, 8）

**缺失知识**：
- QSignalSpy（信号调试）
- Qt 样式表调试器
- exiftool（图片元数据）

**补充方式**：
创建 `docs/debugging_tools.md`：
```markdown
# 调试工具速查

## Qt 信号调试
- QSignalSpy：验证信号是否正确发出和接收
- 用法：`spy = QSignalSpy(obj, SIGNAL("signalName()"))`

## Qt 样式调试
- Qt 样式表调试器：`app.setStyleSheet(debug=True)`
- 检查样式继承链

## 图片问题
- exiftool：检查图片元数据
- 用法：`exiftool image.jpg`
```

---

## 五、总结：适合用 Skill 解决的坑（Top 3）

### 真正需要 Skill 的流程问题：

| 优先级 | Skill | 缺失的检查清单 | 证据来源 | 是否重复 |
|--------|-------|--------------|---------|---------|
| **P0** | systematic-debugging 增强 | 第一性原理 + 全局策略检查 | 案例 1, 3, 4 | No |
| **P1** | code-understanding 新建 | 系统性追踪数据流 | 案例 6 | No |
| **P2** | brainstorming 增强 | 临时补丁检查 | 案例 1 | Partial |

### 不适合 Skill 的：

**工具类**（案例 2）：
- 解决方式：scripts/check_mcp_status.sh

**知识类**（案例 5, 7, 8）：
- 解决方式：docs/project_tooling.md、docs/debugging_tools.md

---

## 六、现有配置已覆盖的坑

### 系统提示词 v3.1

| 原则 | 覆盖的坑 | 案例 |
|-----|---------|------|
| 先理解需求 | 避免白干 | 案例 1（设计错误） |
| 复杂任务隔离 | 上下文管理 | tool-journey.md 上下文溢出 |
| 必须验证 | 防止错误 | verification-before-completion skill |
| 先备份 | 可回滚 | bug-fix-workflow.md |

### UI Design Guide

| 功能 | 覆盖的坑 | 案例 |
|-----|---------|------|
| Token 系统 | 硬编码问题 | 案例 7（按钮样式） |
| /design-system | 自动生成配置 | tool-journey.md 主题系统 |

---

## 七、实施建议

### 立即行动（P0）

1. **增强 systematic-debugging**
   - 添加 Phase 1.5：第一性原理检查
   - 添加 Phase 2.5：全局策略检查
   - 触发条件：多次修复无效时强制执行

### 短期补充（P1）

2. **新建 code-understanding skill**
   - 提供系统性分析方法（数据流追踪）
   - 避免碎片化探索

3. **创建工具和文档**
   - scripts/check_mcp_status.sh
   - scripts/scan_hardcoded_styles.sh
   - docs/project_tooling.md
   - docs/debugging_tools.md

### 可选优化（P2）

4. **增强 brainstorming**
   - 设计阶段添加"临时补丁检查"

---

## 附录：数据来源

- `sop/anti-patterns/blind-spots.md`（8 个绕远路案例）
- `sop/patterns/bug-fix-workflow.md`（根因分析方法）
- `sop/evolution/tool-journey.md`（工具演进历程）
- 现有 skills：systematic-debugging、brainstorming、verification-before-completion
- 用户配置：~/.claude/CLAUDE.md v3.1、~/.claude/guides/ui-design.md

*分析日期：2026-01-19*
