# 主题系统重构规划 v5.0

> 版本: v5.0 (执行中期修订版)
> 创建日期: 2025-12-18
> 基于: v4.0 执行反馈 + Review 审查 + 自我检查
> 状态: **待审批**

---

## 一、执行状态总结

### 1.1 已完成阶段

| 阶段 | 状态 | Commit | 净效果 |
|------|------|--------|--------|
| Step 0: Git 备份 | ✅ 完成 | `edd075f` | 安全检查点 |
| C1: 调色板更新 | ✅ 完成 | `b4305e7` | Linear 风格 Token 完整 |
| B1: StyleManager 迁移 | ✅ 完成 | `28bb029` | 删除 ~265 行，统一调色板 |

### 1.2 已解决的问题

| 问题 | 解决方案 | 验证 |
|------|---------|------|
| 双调色板系统并存 | 删除 StyleManager 类 | ✅ utils/ 无残留 |
| Light 主题死白背景 | bg_app #FFFFFF → #FBFBFC | ✅ JSON 已更新 |
| 调色板 Token 不完整 | 新增 overlay, accent, tertiary, *_subtle | ✅ 结构完整 |
| 死代码堆积 | 删除 StyleManager + build_global_stylesheet | ✅ -265 行 |

### 1.3 暂停的阶段

| 阶段 | 原因 | 处理 |
|------|------|------|
| A1: 删除废弃文件 | 依赖分析不完整，需重新规划 | 见 v5.0 新规划 |

---

## 二、新发现的问题

### 2.1 自我检查发现

**creation_components.py 遗留硬编码:**

| 行号 | 内容 | 类型 |
|------|------|------|
| 827 | `color: white !important;` | 硬编码颜色 |
| 853 | `color: white !important;` | 硬编码颜色 |
| 871 | `color: white !important;` | 硬编码颜色 |
| 894 | `color: white !important;` | 硬编码颜色 |
| 342 | `rgba(128, 128, 128, 0.2)` | 硬编码边框 |

**说明**: 这些不在原 B1 范围内（B1 仅处理 StyleManager），但应纳入后续任务。

### 2.2 A1 依赖重新评估

| 组件 | 原假设 | 实际情况 | 结论 |
|------|--------|---------|------|
| `safe_get_open_file_name` | 硬依赖 qt_app | **已有 fallback** (1244-1257行) | 低风险 |
| launcher 脚本 | 需复杂迁移 | **仅改一行** `from qt_app` → `from main` | 低风险 |
| tools/ 调试工具 | 阻塞项 | **使用 PyQt5，独立于主应用** | 可单独处理 |
| cards/ delegates/ | 废弃可删 | **waterfall_widget.py 使用中** | 不应删除 |

---

## 三、Review 审查意见整合

### 3.1 审查结论摘要

| 项目 | 状态 | 关键反馈 |
|------|------|---------|
| C1 调色板更新 | ✅ 通过 | Token 完整性良好，Linear 风格正确 |
| B1 StyleManager 迁移 | ✅ 通过 | 活跃代码无残留，仅 archive/ 和 qt_app.py 有 |
| A1 阻塞分析 | ✅ 同意 | 原规划确实存在风险，必须调整 |
| A1-NEW 新规划 | ✅ 批准 | 需关注 A1.1 (脚本修复) 和 A1.2 (函数提取) |

### 3.2 审查重点建议

1. **P0 优先**: 修复启动脚本指向 main.py，否则 CI/CD 或用户启动失败
2. **安全性**: 删除 qt_app.py 前确保所有依赖解除
3. **渐进式**: 只有确认所有依赖解除后才物理删除

---

## 四、v5.0 新规划

### 4.1 阶段划分

```
Phase 1 (已完成): 调色板统一
  ├── C1: 更新 JSON ✅
  └── B1: 删除 StyleManager ✅

Phase 2 (待执行): 入口迁移
  ├── A1.1: 更新 launcher 脚本
  ├── A1.2: 确认 fallback 覆盖
  └── A1.3: 删除 qt_app.py

Phase 3 (后续): 硬编码清理
  ├── H1: creation_components.py 硬编码
  ├── H2: 其他组件硬编码审查
  └── H3: cards/delegates 主题化 (可选)

Phase 4 (可选): 工具链更新
  └── T1: tools/ PyQt5 脚本处理
```

### 4.2 Phase 2 详细规划 (A1-NEW)

#### A1.1: 更新 Launcher 脚本

**目标**: 所有启动脚本指向正确的 PySide6 入口 (main.py)

| 文件 | 修改 | 风险 |
|------|------|------|
| `scripts/python/start_app.py:93` | `from qt_app import main` → `from main import main` | 低 |
| `scripts/macos/start_mac.py:107` | `from qt_app import main` → `from main import main` | 低 |
| `packaging/zero_config_launcher.py:246` | `from qt_app import main` → `from main import main` | 低 |
| `packaging/macos/app_launcher.py:147` | `from qt_app import main` → `from main import main` | 低 |

**验证**: 修改后运行各脚本确认启动正常

#### A1.2: 确认 Fallback 覆盖

**目标**: 确保 qt_app.py 删除后无功能缺失

| 依赖 | 当前状态 | 处理 |
|------|---------|------|
| `safe_get_open_file_name` | creation_components.py 已有 fallback (1244-1257) | 无需处理 |
| `MainWindow` (tools/) | tools/ 是独立 PyQt5 调试工具 | 单独处理或保留 |

**验证**:
1. 临时重命名 qt_app.py → qt_app.py.bak
2. 运行 `python main.py` 确认应用正常
3. 测试上传图片功能 (触发 safe_get_open_file_name)

#### A1.3: 删除 qt_app.py

**前置条件**:
- [ ] A1.1 完成且验证通过
- [ ] A1.2 验证通过
- [ ] 用户确认可以删除

**操作**:
```bash
git rm qt_app.py
git commit -m "chore: 删除废弃的 PyQt5 入口 qt_app.py (~900 行)"
```

**回滚**: `git revert <commit>` 或从 `edd075f` 检查点恢复

### 4.3 Phase 3 详细规划 (硬编码清理)

#### H1: creation_components.py 硬编码

| 行号 | 当前值 | 建议替换为 | 优先级 |
|------|--------|-----------|--------|
| 827, 853, 871, 894 | `color: white` | `{palette['text']}` | P2 |
| 342 | `rgba(128,128,128,0.2)` | `{palette['border']}` 或 Token | P3 |

#### H2: 其他组件审查 (待执行)

需要对以下目录进行硬编码颜色扫描：
- `components/dialogs/`
- `components/modes/`
- `components/widgets/`
- `components/layouts/`

### 4.4 Phase 4 详细规划 (可选)

#### T1: tools/ PyQt5 脚本

| 文件 | 状态 | 建议 |
|------|------|------|
| `tools/fix_video_reference_visibility.py` | 使用 PyQt5 + qt_app | 保留或标记废弃 |
| `tools/deep_visibility_analysis.py` | 使用 PyQt5 + qt_app | 保留或标记废弃 |

**说明**: 这些是调试工具，不影响主应用运行。可以：
1. 保留但标记为 "仅限旧版调试"
2. 迁移到 PySide6 + main.py
3. 移动到 archive/

---

## 五、执行策略建议

### 5.1 推荐执行顺序

```
1. [测试验证] 运行 python main.py 确认当前改动稳定
      ↓
2. [Phase 2] A1.1 → A1.2 → A1.3 (入口迁移)
      ↓
3. [测试验证] 完整功能测试
      ↓
4. [Phase 3] H1 → H2 (硬编码清理) [可选]
      ↓
5. [Phase 4] T1 (工具链) [可选]
```

### 5.2 风险控制

| 阶段 | 风险级别 | 控制措施 |
|------|---------|---------|
| Phase 2 A1.1 | 低 | 逐个文件修改，每个验证 |
| Phase 2 A1.2 | 低 | 临时重命名测试 |
| Phase 2 A1.3 | 中 | 需用户确认，有回滚点 |
| Phase 3 | 低 | 纯样式修改，不影响逻辑 |

### 5.3 检查点设计

| 检查点 | 时机 | 操作 |
|--------|------|------|
| CP-1 | Phase 2 开始前 | `git tag phase2-start` |
| CP-2 | A1.1 完成后 | `git commit` + 功能测试 |
| CP-3 | A1.3 完成后 | `git tag phase2-complete` |

---

## 六、待审批决策点

### 决策 1: Phase 2 执行范围

- [ ] **选项 A**: 完整执行 A1.1 + A1.2 + A1.3 (删除 qt_app.py)
- [ ] **选项 B**: 仅执行 A1.1 + A1.2 (保留 qt_app.py)
- [ ] **选项 C**: 暂不执行，先进行测试验证

### 决策 2: Phase 3 是否纳入当前迭代

- [ ] **是**: 在 Phase 2 后继续执行硬编码清理
- [ ] **否**: 记录为后续任务，当前迭代仅完成 Phase 2

### 决策 3: tools/ 处理方式

- [ ] **保留**: 标记为旧版调试工具
- [ ] **迁移**: 更新为 PySide6
- [ ] **归档**: 移动到 archive/

---

## 七、文件变更汇总

### 7.1 Phase 2 涉及文件

| 操作 | 文件 | 变更内容 |
|------|------|---------|
| 修改 | `scripts/python/start_app.py` | 1 行导入修改 |
| 修改 | `scripts/macos/start_mac.py` | 1 行导入修改 |
| 修改 | `packaging/zero_config_launcher.py` | 1 行导入修改 |
| 修改 | `packaging/macos/app_launcher.py` | 1 行导入修改 |
| 删除 | `qt_app.py` | ~900 行 (待确认) |

### 7.2 Phase 3 涉及文件 (预估)

| 操作 | 文件 | 变更内容 |
|------|------|---------|
| 修改 | `components/creation_components.py` | 5 处硬编码替换 |
| 审查 | `components/*/` | 待扫描 |

---

## 八、审批签字区

**规划版本**: v5.0
**提交审批日期**: 2025-12-18
**规划者**: Claude Opus 4.5

### 审批记录

| 决策点 | 选择 | 审批人 | 日期 |
|--------|------|--------|------|
| 决策 1 | | | |
| 决策 2 | | | |
| 决策 3 | | | |

### 审批意见

```
[待填写]
```

---

*文档结束*
