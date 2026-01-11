# 主题系统重构规划 v6.0

> 版本: v6.0 (全面审查版)
> 创建日期: 2025-12-18
> 状态: **待审批**

---

## 一、当前状态

### 1.1 已完成

| 阶段 | Commit | 效果 |
|------|--------|------|
| C1: 调色板更新 | `b4305e7` | Linear Token 完整 |
| B1: StyleManager 删除 | `28bb029` | -265 行，统一调色板 |

### 1.2 待执行

- Phase 2: 入口迁移 (删除 qt_app.py)
- Phase 3: 硬编码清理

---

## 二、Phase 2: 入口迁移 (A1)

### 2.1 qt_app.py 依赖完整分析

**实际代码依赖** (排除 archive/):

| 文件 | 行号 | 导入内容 | 类型 | 处理方式 |
|------|------|---------|------|---------|
| `scripts/python/start_app.py` | 93 | `from qt_app import main` | 启动脚本 | 改为 `from main import main` |
| `scripts/macos/start_mac.py` | 107 | `from qt_app import main` | 启动脚本 | 改为 `from main import main` |
| `packaging/zero_config_launcher.py` | 246 | `from qt_app import main` | 打包脚本 | 改为 `from main import main` |
| `packaging/macos/app_launcher.py` | 147 | `from qt_app import main` | 打包脚本 | 改为 `from main import main` |
| `components/creation_components.py` | 1240 | `from qt_app import safe_get_open_file_name` | 功能函数 | **已有 fallback (1244-1257)，无需处理** |
| `tools/fix_video_reference_visibility.py` | 157 | `from qt_app import MainWindow` | 调试工具 | 见下方说明 |
| `tools/deep_visibility_analysis.py` | 29 | `from qt_app import MainWindow` | 调试工具 | 见下方说明 |

**注释引用** (不影响运行):
| 文件 | 内容 |
|------|------|
| `components/widgets/zoomable_text_edit.py:3` | docstring: "extracted from qt_app" |
| `components/widgets/zoomable_image_label.py:3` | docstring: "extracted from qt_app" |
| `components/widgets/clickable_label.py:3` | docstring: "extracted from qt_app" |
| `components/controllers/export_bundle_controller.py:3` | docstring: "split from qt_app" |
| `components/reference_assets/actions.py:3` | docstring: "extracted from qt_app" |
| `utils/reference_display.py:3` | docstring: "extracted from qt_app" |
| `components/main_window.py:532` | 注释: "Retained strictly from qt_app.py logic" |

### 2.2 tools/ 目录说明

**什么是 tools/?**

`tools/` 是一个包含 **60+ 个诊断、修复、迁移脚本** 的工具目录：

```
tools/
├── diagnose_*.py      # 诊断类 (API问题、字体缩放、存储路径等)
├── fix_*.py           # 修复类 (依赖、历史记录、字符串等)
├── *_migration.py     # 迁移类 (CSV→SQLite、存储迁移)
├── performance_*.py   # 性能类 (基准测试、内存泄漏检测)
└── 其他工具脚本
```

**依赖 qt_app.py 的工具** (仅 2 个):

| 文件 | 用途 | 使用 PyQt5 | 建议处理 |
|------|------|-----------|---------|
| `fix_video_reference_visibility.py` | 调试视频参考面板可见性 | 是 (line 156) | 归档 |
| `deep_visibility_analysis.py` | 深度分析组件可见性 | 是 (line 28) | 归档 |

**建议**: 这两个工具是旧版 PyQt5 调试工具，已不适用于 PySide6 架构。建议：
1. 移动到 `archive/legacy_tools/`
2. 或在文件头添加废弃警告注释

### 2.3 执行步骤

```
A1.1: 更新启动脚本 (4 个文件，各改 1 行)
  │
  ├── scripts/python/start_app.py:93
  ├── scripts/macos/start_mac.py:107
  ├── packaging/zero_config_launcher.py:246
  └── packaging/macos/app_launcher.py:147
  │
A1.2: 归档旧版调试工具 (2 个文件)
  │
  ├── tools/fix_video_reference_visibility.py → archive/legacy_tools/
  └── tools/deep_visibility_analysis.py → archive/legacy_tools/
  │
A1.3: 验证测试
  │
  ├── 临时重命名 qt_app.py → qt_app.py.bak
  ├── python main.py (验证启动)
  └── 测试图片上传 (验证 fallback)
  │
A1.4: 删除 qt_app.py
  │
  └── git rm qt_app.py (~900 行)
```

### 2.4 风险与回滚

| 步骤 | 风险 | 回滚 |
|------|------|------|
| A1.1 | 低 - 简单字符串替换 | git revert |
| A1.2 | 无 - 仅移动文件 | git revert |
| A1.3 | 无 - 仅测试 | 恢复 .bak |
| A1.4 | 中 - 删除大文件 | git revert 或从 edd075f 恢复 |

---

## 三、Phase 3: 硬编码清理 (H)

### 3.1 审查方法论

**分类标准**:
- **类型 A (良好)**: 使用 `colors.get('token', '#fallback')` - 无需修改
- **类型 B (硬编码)**: 直接使用 `#XXXXXX` - 需要修复
- **类型 C (特殊)**: 有意的固定颜色 (如播放器黑色背景) - 评估后决定

### 3.2 全量硬编码审查结果

#### 3.2.1 高优先级 (P1) - 完全硬编码

| 文件 | 行号 | 硬编码值 | 建议 Token |
|------|------|---------|-----------|
| **cards/placeholder_card.py** | | | |
| | 45 | `#242424` | `palette.neutral.bg_card` |
| | 46 | `#555555` | `palette.neutral.border_strong` |
| | 58 | `#d0d0d0` | `palette.text.secondary` |
| | 65 | `#999999` | `palette.text.tertiary` |
| | 70 | `#666666` | `palette.text.disabled` |
| | 92 | `#d0d0d0` | `palette.text.secondary` |
| | 95 | `#4CAF50` | `palette.semantic.success` |
| | 98 | `#2196F3` | `palette.semantic.info` |
| | 103 | `#f44336` | `palette.semantic.error` |
| **cards/image_card.py** | | | |
| | 117 | `#1a1a1a` | `palette.neutral.bg_card` |
| | 118 | `#3a3a5e` | `palette.neutral.border_subtle` |
| | 123 | `#4CAF50` | `palette.semantic.success` |
| | 154 | `#ffffff` | `palette.text.on_brand` |
| | 176 | `#ffffff` | `palette.text.primary` |
| | 191 | `#cccccc` | `palette.text.secondary` |
| | 205 | `#cccccc` | `palette.text.secondary` |
| **widgets/video_image_upload_panel.py** | | | |
| | 78 | `#3a3a3a`, `#2a2a2a` | `palette.neutral.bg_hover`, `bg_card` |
| | 213 | `#2a2a2a` | `palette.neutral.bg_card` |
| | 220 | `#383838` | `palette.neutral.bg_hover` |
| **widgets/reference_images_simple.py** | | | |
| | 282 | `#ff6b6b` | `palette.semantic.error` |
| | 284 | `#0d7377` | `palette.brand.main` |
| **reference_assets/actions.py** | | | |
| | 72 | `#ffb347` | `palette.semantic.warning` |
| | 84, 86 | `#bbbbbb` | `palette.text.secondary` |
| **creation_components.py** | | | |
| | 827, 853, 871, 894 | `white` | `palette.text.primary` (Dark) |
| | 342 | `rgba(128,128,128,0.2)` | `palette.neutral.border_subtle` |

#### 3.2.2 中优先级 (P2) - 对话框硬编码

| 文件 | 行号 | 硬编码值 | 建议 Token |
|------|------|---------|-----------|
| **dialogs/image_detail_dialog.py** | | | |
| | 131 | `#bbbbbb` | `palette.text.secondary` |
| | 177 | `#cccccc` | `palette.text.secondary` |
| | 527-528 | `#2a2a3e`, `#ffffff` | 使用 colors.get() |
| | 538 | `#4CAF50` | `palette.semantic.success` |
| **dialogs/video_detail_dialog.py** | | | |
| | 164-165 | `#000000`, `#ffffff` | **保留** (播放器背景) |
| | 179 | `#000000` | **保留** (播放器背景) |
| | 276 | `#bbbbbb` | `palette.text.secondary` |
| | 322 | `#cccccc` | `palette.text.secondary` |

#### 3.2.3 低优先级 (P3) - Delegate 选中态

| 文件 | 行号 | 硬编码值 | 建议 |
|------|------|---------|------|
| `delegates/image_card_delegate.py` | 278 | `#e6f4ff` | 新增 `palette.brand.selected_text` |
| `delegates/video_card_delegate.py` | 183 | `#e6f4ff` | 新增 `palette.brand.selected_text` |

### 3.3 统计汇总

| 优先级 | 文件数 | 硬编码处数 | 工作量 |
|--------|--------|-----------|--------|
| P1 高 | 6 | ~25 | 中 |
| P2 中 | 2 | ~8 | 低 |
| P3 低 | 2 | 2 | 低 |
| **总计** | **10** | **~35** | **中** |

### 3.4 是否纳入统一管理?

**结论: 是**

**理由**:
1. **一致性**: 硬编码颜色不响应主题切换
2. **维护性**: 分散的颜色难以批量调整
3. **可追溯**: 使用 Token 可以快速定位所有使用点

**建议方案**:
- 所有硬编码改为 `colors.get('palette.xxx', '#fallback')` 模式
- 保留 fallback 确保向后兼容
- 对于新 Token (如 `selected_text`)，先在 JSON 中添加

### 3.5 执行策略

```
H1: cards/ 硬编码修复 (P1)
  │
  ├── placeholder_card.py (~9 处)
  └── image_card.py (~7 处)
  │
H2: widgets/ 硬编码修复 (P1)
  │
  ├── video_image_upload_panel.py (~3 处)
  └── reference_images_simple.py (~2 处)
  │
H3: reference_assets/ 硬编码修复 (P1)
  │
  └── actions.py (~3 处)
  │
H4: creation_components.py 硬编码修复 (P1)
  │
  └── (~5 处，B1 遗留)
  │
H5: dialogs/ 硬编码修复 (P2)
  │
  ├── image_detail_dialog.py (~4 处)
  └── video_detail_dialog.py (~2 处，排除播放器)
  │
H6: delegates/ 选中态 Token (P3, 可选)
  │
  ├── 新增 JSON Token: palette.brand.selected_text
  ├── image_card_delegate.py (1 处)
  └── video_card_delegate.py (1 处)
```

---

## 四、执行计划总览

### 4.1 推荐顺序

```
Step 1: [测试] 运行 python main.py 验证当前状态
    ↓
Step 2: [Phase 2] A1.1 → A1.2 → A1.3 → A1.4
    ↓
Step 3: [测试] 验证启动脚本和应用功能
    ↓
Step 4: [Phase 3] H1 → H2 → H3 → H4 → H5 → H6(可选)
    ↓
Step 5: [测试] 主题切换测试
    ↓
Step 6: [归档] 更新文档，关闭任务
```

### 4.2 检查点设计

| 检查点 | 时机 | 操作 |
|--------|------|------|
| CP-0 | 执行前 | `git tag phase2-start` |
| CP-1 | A1.1 后 | commit "更新启动脚本" |
| CP-2 | A1.2 后 | commit "归档旧版调试工具" |
| CP-3 | A1.4 后 | commit "删除 qt_app.py" |
| CP-4 | H1-H4 后 | commit "P1 硬编码修复" |
| CP-5 | H5-H6 后 | commit "P2/P3 硬编码修复" |

### 4.3 文件变更汇总

**Phase 2 (入口迁移)**:

| 操作 | 文件 | 变更 |
|------|------|------|
| 修改 | `scripts/python/start_app.py` | 1 行 |
| 修改 | `scripts/macos/start_mac.py` | 1 行 |
| 修改 | `packaging/zero_config_launcher.py` | 1 行 |
| 修改 | `packaging/macos/app_launcher.py` | 1 行 |
| 移动 | `tools/fix_video_reference_visibility.py` | → archive/ |
| 移动 | `tools/deep_visibility_analysis.py` | → archive/ |
| 删除 | `qt_app.py` | ~900 行 |

**Phase 3 (硬编码清理)**:

| 操作 | 文件 | 变更处数 |
|------|------|---------|
| 修改 | `components/cards/placeholder_card.py` | ~9 |
| 修改 | `components/cards/image_card.py` | ~7 |
| 修改 | `components/widgets/video_image_upload_panel.py` | ~3 |
| 修改 | `components/widgets/reference_images_simple.py` | ~2 |
| 修改 | `components/reference_assets/actions.py` | ~3 |
| 修改 | `components/creation_components.py` | ~5 |
| 修改 | `components/dialogs/image_detail_dialog.py` | ~4 |
| 修改 | `components/dialogs/video_detail_dialog.py` | ~2 |
| 修改 | `components/delegates/image_card_delegate.py` | 1 (可选) |
| 修改 | `components/delegates/video_card_delegate.py` | 1 (可选) |
| 修改 | `config/themes/linear_*.json` | 新增 Token (可选) |

---

## 五、审批决策点

### 决策 1: Phase 2 执行确认

- [ ] **确认执行** A1.1-A1.4 完整流程
- [ ] **调整**: ________________

### 决策 2: tools/ 处理方式

- [ ] **归档**: 移动到 `archive/legacy_tools/`
- [ ] **保留**: 添加废弃警告注释
- [ ] **其他**: ________________

### 决策 3: Phase 3 范围

- [ ] **完整执行**: H1-H6 全部
- [ ] **仅 P1**: H1-H4
- [ ] **分批执行**: 先 P1，后续再处理 P2/P3
- [ ] **其他**: ________________

### 决策 4: 播放器黑色背景处理

`dialogs/video_detail_dialog.py` 中 `#000000` (播放器背景):
- [ ] **保留硬编码**: 播放器背景固定为黑色是合理的
- [ ] **新增 Token**: 添加 `palette.special.video_bg: #000000`
- [ ] **其他**: ________________

---

## 六、预期成果

### 6.1 代码清理

| 指标 | 当前 | 目标 |
|------|------|------|
| qt_app.py | ~900 行 | 删除 |
| 硬编码颜色点 | ~35 处 | 0 处 |
| 未托管组件 | 10+ 文件 | 0 文件 |

### 6.2 架构改进

- 单一入口: `main.py` (PySide6)
- 统一调色板: `theme_engine` 单一来源
- 主题响应: 所有组件跟随主题切换

---

## 七、签字区

**规划版本**: v6.0
**提交日期**: 2025-12-18
**规划者**: Claude Opus 4.5

### 审批记录

| 决策点 | 选择 | 审批人 | 日期 |
|--------|------|--------|------|
| 决策 1 | | | |
| 决策 2 | | | |
| 决策 3 | | | |
| 决策 4 | | | |

---

*文档结束*
