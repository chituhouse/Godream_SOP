# 主题系统重构最终执行计划 v7.0

> 版本: v7.0 (最终执行版)
> 创建日期: 2025-12-18
> 状态: **待审批执行**
> 检查点: `checkpoint-pre-phase2` (commit: 7c4f7f8)

---

## 重要声明

**执行纪律**:
- 严格按照本文档执行，禁止偏离
- 遇到任何计划外情况，立即暂停并申请审批
- 每个阶段完成后 git commit
- 出现问题可回滚到 `checkpoint-pre-phase2`

---

## 一、当前状态

### 1.1 Git 提交历史

```
7c4f7f8 docs: 主题系统重构规划文档 v6.0
28bb029 refactor: B1 完成 - 移除 StyleManager 及其依赖
b4305e7 refactor: C1 完成 - 更新主题调色板 JSON
edd075f checkpoint: 主题系统重构执行前备份
```

### 1.2 已完成

| 阶段 | 状态 | 效果 |
|------|------|------|
| C1: 调色板更新 | ✅ | Linear Token 完整 |
| B1: StyleManager 删除 | ✅ | -265 行 |

---

## 二、Phase 2: 入口迁移 + 废弃代码清理

### 2.1 执行清单

#### A1.1: 更新启动脚本 (4 个文件)

| 文件 | 行号 | 修改前 | 修改后 |
|------|------|--------|--------|
| `scripts/python/start_app.py` | 93 | `from qt_app import main` | `from main import main` |
| `scripts/macos/start_mac.py` | 107 | `from qt_app import main` | `from main import main` |
| `packaging/zero_config_launcher.py` | 246 | `from qt_app import main` | `from main import main` |
| `packaging/macos/app_launcher.py` | 147 | `from qt_app import main` | `from main import main` |

#### A1.2: 归档旧版调试工具 (2 个文件)

| 操作 | 源文件 | 目标 |
|------|--------|------|
| 移动 | `tools/fix_video_reference_visibility.py` | `archive/legacy_tools/` |
| 移动 | `tools/deep_visibility_analysis.py` | `archive/legacy_tools/` |

#### A1.3: 验证测试

```bash
# 1. 临时重命名 qt_app.py
mv qt_app.py qt_app.py.bak

# 2. 测试启动
python main.py

# 3. 如果成功，继续；如果失败，恢复并报告
```

#### A1.4: 删除废弃入口

| 操作 | 文件 | 预估行数 |
|------|------|---------|
| 删除 | `qt_app.py` | ~900 |

#### A1.5: 删除废弃 Cards (新增)

| 操作 | 文件 | 预估行数 | 废弃标记位置 |
|------|------|---------|-------------|
| 删除 | `components/cards/placeholder_card.py` | ~130 | 文件头 DEPRECATED |
| 删除 | `components/cards/image_card.py` | ~470 | 文件头 DEPRECATED |
| 删除 | `components/cards/video_card.py` | ~570 | 文件头 DEPRECATED |
| 修改 | `components/cards/__init__.py` | 清空导出 | - |

#### A1.6: 删除废弃 WaterfallWidget (新增)

| 操作 | 文件 | 预估行数 | 废弃标记位置 |
|------|------|---------|-------------|
| 删除 | `components/layouts/waterfall_widget.py` | ~530 | `__init__.py` 注释 |
| 修改 | `components/layouts/__init__.py` | 移除导入 | - |

### 2.2 Phase 2 预期效果

| 指标 | 变化 |
|------|------|
| 删除代码 | ~2600 行 |
| 删除文件 | 5 个 |
| 移动文件 | 2 个 |
| 修改文件 | 6 个 |

### 2.3 Phase 2 提交计划

```
Commit 1: A1.1 更新启动脚本
Commit 2: A1.2 归档调试工具
Commit 3: A1.4 删除 qt_app.py
Commit 4: A1.5+A1.6 删除废弃 cards 和 waterfall
```

---

## 三、Phase 3: 硬编码清理

### 3.1 新增 Token (先执行)

**文件**: `config/themes/linear_dark.json` 和 `linear_light.json`

| Token | Dark 值 | Light 值 | 用途 |
|-------|---------|----------|------|
| `palette.special.media_bg` | `#000000` | `#000000` | 视频播放器背景 |
| `palette.state.selected_text` | `#e6f4ff` | `#1a4d8c` | 选中态文字 |

### 3.2 硬编码修复清单

#### H1: `components/creation_components.py` (P1 - 必须)

| 行号 | 当前代码 | 修改为 |
|------|---------|--------|
| 342 | `rgba(128, 128, 128, 0.2)` | 保留 (半透明边框) |
| 827 | `color: white !important;` | `color: {palette['text']} !important;` |
| 853 | `color: white !important;` | `color: {palette['text']} !important;` |
| 871 | `color: white !important;` | `color: {palette['text']} !important;` |
| 894 | `color: white !important;` | `color: {palette['text']} !important;` |

**注意**: 需要在该方法开头添加 `palette = theme_engine.get_palette()`

#### H2: `components/widgets/video_image_upload_panel.py` (P2)

| 行号 | 当前代码 | 修改为 |
|------|---------|--------|
| 78 | `QColor("#3a3a3a")` / `QColor("#2a2a2a")` | `QColor(palette['surface_hover'])` / `QColor(palette['surface'])` |
| 213 | `#2a2a2a` | `{palette['surface']}` |
| 220 | `#383838` | `{palette['surface_hover']}` |

#### H3: `components/widgets/reference_images_simple.py` (P2)

| 行号 | 当前代码 | 修改为 |
|------|---------|--------|
| 282 | `#ff6b6b` | `{colors.get('palette.semantic.error', '#ff6b6b')}` |
| 284 | `#0d7377` | `{colors.get('palette.brand.main', '#5E6AD2')}` |

#### H4: `components/reference_assets/actions.py` (P2)

| 行号 | 当前代码 | 修改为 |
|------|---------|--------|
| 72 | `#ffb347` | `{colors.get('palette.semantic.warning', '#ffb347')}` 或 `{colors.get('palette.accent.orange', '#FF6B35')}` |
| 84 | `#bbbbbb` | `{colors.get('palette.text.secondary', '#888888')}` |
| 86 | `#bbbbbb` | `{colors.get('palette.text.secondary', '#888888')}` |

#### H5: `components/dialogs/image_detail_dialog.py` (P2)

| 行号 | 当前代码 | 修改为 |
|------|---------|--------|
| 131 | `#bbbbbb` | `{colors.get('palette.text.secondary', '#888888')}` |
| 177 | `#cccccc` | `{colors.get('palette.text.secondary', '#888888')}` |
| 527 | `#2a2a3e` | `{colors.get('palette.neutral.bg_card', '#2a2a3e')}` |
| 528 | `#ffffff` | `{colors.get('palette.text.primary', '#ffffff')}` |
| 538 | `#4CAF50` | `{colors.get('palette.semantic.success', '#27C93F')}` |

#### H6: `components/dialogs/video_detail_dialog.py` (P2)

| 行号 | 当前代码 | 修改为 |
|------|---------|--------|
| 164-179 | `#000000` | `{colors.get('palette.special.media_bg', '#000000')}` |
| 276 | `#bbbbbb` | `{colors.get('palette.text.secondary', '#888888')}` |
| 322 | `#cccccc` | `{colors.get('palette.text.secondary', '#888888')}` |

#### H7: `components/delegates/*.py` (P3 - 选中态)

| 文件 | 行号 | 当前代码 | 修改为 |
|------|------|---------|--------|
| `image_card_delegate.py` | 278 | `QColor('#e6f4ff')` | `QColor(colors.get('palette.state.selected_text', '#e6f4ff'))` |
| `video_card_delegate.py` | 183 | `QColor('#e6f4ff')` | `QColor(colors.get('palette.state.selected_text', '#e6f4ff'))` |

### 3.3 Phase 3 提交计划

```
Commit 1: 新增 Token (media_bg, selected_text)
Commit 2: H1 creation_components.py P1 修复
Commit 3: H2-H4 widgets 和 actions 修复
Commit 4: H5-H6 dialogs 修复
Commit 5: H7 delegates 修复
```

### 3.4 Phase 3 预期效果

| 指标 | 变化 |
|------|------|
| 新增 Token | 2 个 |
| 修复硬编码 | 21 处 |
| 修改文件 | 10 个 |

---

## 四、执行顺序总览

```
[检查点已创建: checkpoint-pre-phase2]
        │
        ▼
Step 1: Phase 2 执行
        │
        ├── A1.1: 更新启动脚本 → commit
        ├── A1.2: 归档调试工具 → commit
        ├── A1.3: 验证测试
        ├── A1.4: 删除 qt_app.py → commit
        └── A1.5+A1.6: 删除废弃代码 → commit
        │
        ▼
Step 2: 功能测试
        │
        └── python main.py 验证启动
        │
        ▼
Step 3: Phase 3 执行
        │
        ├── Token 新增 → commit
        ├── H1 P1 修复 → commit
        ├── H2-H4 修复 → commit
        ├── H5-H6 修复 → commit
        └── H7 修复 → commit
        │
        ▼
Step 4: 最终测试
        │
        ├── 启动测试
        ├── Light 主题切换测试
        └── Dark 主题切换测试
        │
        ▼
[完成]
```

---

## 五、回滚方案

| 问题 | 回滚命令 |
|------|---------|
| Phase 2 任何步骤失败 | `git checkout checkpoint-pre-phase2` |
| Phase 3 任何步骤失败 | `git revert <commit>` |
| 全部回滚 | `git reset --hard checkpoint-pre-phase2` |

---

## 六、风险评估

| 阶段 | 风险 | 缓解措施 |
|------|------|---------|
| A1.1 启动脚本 | 低 - 简单替换 | 逐个修改验证 |
| A1.4 删除 qt_app | 中 - 大文件删除 | 有检查点可回滚 |
| A1.5-A1.6 删除废弃代码 | 中 - 多文件删除 | 先验证无活跃引用 |
| H1 白色修复 | 低 - 样式修改 | 逐行修改 |
| H2-H7 其他修复 | 低 - 样式修改 | 按文件提交 |

---

## 七、审批确认

### 执行内容确认

- [待确认] Phase 2: 删除 qt_app.py + cards/ + waterfall_widget
- [待确认] Phase 3: 新增 2 个 Token + 修复 21 处硬编码
- [待确认] 特殊处理: 播放器背景用 Token 但两主题都是黑色
- [待确认] 特殊处理: 选中态新增 Token，Dark 浅蓝 Light 深蓝

### 审批签字

```
审批人: ________________
日期: ________________
备注: ________________
```

---

*文档结束*
