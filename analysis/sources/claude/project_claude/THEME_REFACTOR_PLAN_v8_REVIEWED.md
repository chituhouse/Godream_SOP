# 主题系统重构计划 v8.0 (审查修订版)

> 版本: v8.0 (整合 Gemini 审查建议)
> 创建日期: 2025-12-18
> 状态: **待审批执行**
> 审查评分: 8.5/10
> 检查点: `checkpoint-pre-phase2` (commit: 7c4f7f8)

---

## 审查报告关键改进 (已采纳)

| 审查建议 | 状态 | 处理方式 |
|----------|------|---------|
| 增加"搜索引用"步骤 | ✅ 已执行 | 见下方排查结果 |
| 细化入口校验 | ✅ 已执行 | main.py 初始化完整 |
| Token 命名改进 | ✅ 采纳 | `special.media_bg` → `component.player_bg` |
| 增加 checkpoint-phase2-complete | ✅ 采纳 | 见执行序列 |
| 额外归档 tools/integrate_adapters.py | ✅ 新增 | 迁移工具也归档 |

---

## 一、全局搜索排查结果

### 1.1 WaterfallWidget 引用 (排除 archive/)

| 位置 | 类型 | 影响 |
|------|------|------|
| `qt_app.py:99` | 注释 | 随 qt_app 删除 |
| `components/adapters/history_adapter.py:3,182,255` | 注释 | 无影响，兼容说明 |
| `components/layouts/waterfall_widget.py` | 定义 | 待删除 |
| `components/layouts/__init__.py:3` | 注释 | 无影响 |
| `tools/integrate_adapters.py:32,44-60` | 字符串 | **新增归档** |

### 1.2 ImageCard/VideoCard/PlaceholderCard 引用 (排除 archive/)

| 位置 | 类型 | 影响 |
|------|------|------|
| `components/cards/*.py` | 定义 | 待删除 |
| `components/cards/__init__.py` | 导出 | 待清空 |
| `components/layouts/waterfall_widget.py:10-12,169,171,178,311,313` | 导入+使用 | 随 waterfall 删除 |
| `qt_app.py:96-97` | 导入 | 随 qt_app 删除 |
| `components/delegates/*_delegate.py` | **不同类** | ImageCardDelegate ≠ ImageCard，保留 |
| `components/modes/video_mode_widget.py:1021` | 注释 | 无影响 |

### 1.3 main.py vs qt_app.py 初始化差异

| 功能 | qt_app.py (PyQt5) | main.py (PySide6) | 状态 |
|------|-------------------|-------------------|------|
| High DPI | `setup_high_dpi_support()` | 不需要 (Qt6 默认) | ✅ 安全 |
| DPI Scaler | `DpiScaler.init(app)` | `font_scaler` in MainWindow | ✅ 已迁移 |
| 信号处理 | 无 | `signal.signal(SIGINT)` | ✅ 更好 |
| 异常处理 | 未知 | `try/except` 包裹 | ✅ 有 |

**结论**: main.py 初始化完整，可安全切换。

### 1.4 tests/ 目录检查

| 文件 | 引用废弃代码 | 状态 |
|------|-------------|------|
| `tests/reproduce_type_error.py` | 否 | ✅ 安全 |

### 1.5 __init__.py 检查

| 文件 | 内容 | 处理 |
|------|------|------|
| `components/cards/__init__.py` | 导出 VideoCard, ImageCard | **需要清空** |
| `components/layouts/__init__.py` | 注释说明 | 无需修改 |

---

## 二、Phase 2: 入口迁移 + 废弃代码删除

### 2.1 完整执行清单

#### A1.1: 更新启动脚本 (4 个文件)

```python
# 修改前
from qt_app import main
# 修改后
from main import main
```

| 文件 | 行号 |
|------|------|
| `scripts/python/start_app.py` | 93 |
| `scripts/macos/start_mac.py` | 107 |
| `packaging/zero_config_launcher.py` | 246 |
| `packaging/macos/app_launcher.py` | 147 |

#### A1.2: 归档工具 (3 个文件 → 新增 1 个)

| 源文件 | 目标 |
|--------|------|
| `tools/fix_video_reference_visibility.py` | `archive/legacy_tools/` |
| `tools/deep_visibility_analysis.py` | `archive/legacy_tools/` |
| `tools/integrate_adapters.py` | `archive/legacy_tools/` **(新增)** |

#### A1.3: 验证测试

```bash
# 1. 临时重命名 qt_app.py
mv qt_app.py qt_app.py.bak

# 2. 测试启动
python main.py

# 3. 如果成功，继续；如果失败，恢复并报告
```

#### A1.4: 删除废弃入口

| 文件 | 行数 |
|------|------|
| `qt_app.py` | 884 |

#### A1.5: 删除废弃 Cards

| 文件 | 行数 |
|------|------|
| `components/cards/placeholder_card.py` | 125 |
| `components/cards/image_card.py` | 505 |
| `components/cards/video_card.py` | 584 |

#### A1.6: 清空 cards/__init__.py

```python
# 修改后
"""
DEPRECATED: Card classes have been removed.
Use components/delegates/ for modern views.
"""
__all__ = []
```

#### A1.7: 删除废弃 WaterfallWidget

| 文件 | 行数 |
|------|------|
| `components/layouts/waterfall_widget.py` | 673 |

### 2.2 Phase 2 提交序列

```
Commit 1: A1.1 更新启动脚本
Commit 2: A1.2 归档工具 (3个文件)
Commit 3: A1.4 删除 qt_app.py
Commit 4: A1.5-A1.7 删除废弃 cards 和 waterfall

→ 创建 Tag: checkpoint-phase2-complete
```

### 2.3 Phase 2 预期效果

| 指标 | 变化 |
|------|------|
| 删除代码 | ~2771 行 |
| 删除文件 | 5 个 |
| 归档文件 | 3 个 |
| 修改文件 | 5 个 |

---

## 三、Phase 3: 硬编码清理

### 3.1 新增 Token (采纳审查建议)

**文件**: `config/themes/linear_dark.json` 和 `linear_light.json`

| Token | Dark 值 | Light 值 | 用途 | 说明 |
|-------|---------|----------|------|------|
| `palette.component.player_bg` | `#000000` | `#000000` | 视频播放器背景 | 改自 special.media_bg |
| `palette.state.selected_text` | `#e6f4ff` | `#1a4d8c` | 选中态文字 | - |

**JSON 结构变更**:
```json
{
  "palette": {
    "component": {
      "player_bg": "#000000"
    },
    "state": {
      "selected_text": "#e6f4ff"
    }
  }
}
```

### 3.2 硬编码修复清单 (21 处)

#### H1: `components/creation_components.py` (P1 - 5处)

| 行号 | 当前 | 修改为 |
|------|------|--------|
| 827 | `color: white` | `color: {palette['text']['primary']}` |
| 853 | `color: white` | `color: {palette['text']['primary']}` |
| 871 | `color: white` | `color: {palette['text']['primary']}` |
| 894 | `color: white` | `color: {palette['text']['primary']}` |
| 342 | `rgba(128,128,128,0.2)` | 保留 (半透明边框) |

#### H2: `components/widgets/video_image_upload_panel.py` (P2 - 3处)

| 行号 | 当前 | 修改为 |
|------|------|--------|
| 78 | `#3a3a3a`/`#2a2a2a` | `{palette['neutral']['bg_hover']}`/`{palette['neutral']['bg_card']}` |
| 213 | `#2a2a2a` | `{palette['neutral']['bg_card']}` |
| 220 | `#383838` | `{palette['neutral']['bg_hover']}` |

#### H3: `components/widgets/reference_images_simple.py` (P2 - 2处)

| 行号 | 当前 | 修改为 |
|------|------|--------|
| 282 | `#ff6b6b` | `{colors.get('palette.semantic.error', '#ff6b6b')}` |
| 284 | `#0d7377` | `{colors.get('palette.brand.main', '#5E6AD2')}` |

#### H4: `components/reference_assets/actions.py` (P2 - 3处)

| 行号 | 当前 | 修改为 |
|------|------|--------|
| 72 | `#ffb347` | `{colors.get('palette.accent.orange', '#FF6B35')}` |
| 84 | `#bbbbbb` | `{colors.get('palette.text.secondary', '#888888')}` |
| 86 | `#bbbbbb` | `{colors.get('palette.text.secondary', '#888888')}` |

#### H5: `components/dialogs/image_detail_dialog.py` (P2 - 5处)

| 行号 | 当前 | 修改为 |
|------|------|--------|
| 131 | `#bbbbbb` | `{colors.get('palette.text.secondary', '#888888')}` |
| 177 | `#cccccc` | `{colors.get('palette.text.secondary', '#888888')}` |
| 527 | `#2a2a3e` | `{colors.get('palette.neutral.bg_card', '#2a2a3e')}` |
| 528 | `#ffffff` | `{colors.get('palette.text.primary', '#ffffff')}` |
| 538 | `#4CAF50` | `{colors.get('palette.semantic.success', '#27C93F')}` |

#### H6: `components/dialogs/video_detail_dialog.py` (P2 - 3处)

| 行号 | 当前 | 修改为 |
|------|------|--------|
| 164-179 | `#000000` | `{colors.get('palette.component.player_bg', '#000000')}` |
| 276 | `#bbbbbb` | `{colors.get('palette.text.secondary', '#888888')}` |
| 322 | `#cccccc` | `{colors.get('palette.text.secondary', '#888888')}` |

#### H7: `components/delegates/*.py` (P3 - 2处)

| 文件 | 行号 | 当前 | 修改为 |
|------|------|------|--------|
| image_card_delegate.py | 278 | `#e6f4ff` | `colors.get('palette.state.selected_text', '#e6f4ff')` |
| video_card_delegate.py | 183 | `#e6f4ff` | `colors.get('palette.state.selected_text', '#e6f4ff')` |

### 3.3 Phase 3 提交序列

```
Commit 1: 新增 Token (component.player_bg, state.selected_text)
Commit 2: H1 creation_components.py P1 修复
Commit 3: H2-H4 widgets 和 actions 修复
Commit 4: H5-H6 dialogs 修复
Commit 5: H7 delegates 修复
```

---

## 四、执行序列 (修订版)

```
[检查点: checkpoint-pre-phase2]
        │
        ▼
Phase 2 执行
├── A1.1: 更新启动脚本 → commit
├── A1.2: 归档工具 (3个) → commit
├── A1.3: 验证测试 (python main.py)
├── A1.4: 删除 qt_app.py → commit
└── A1.5-A1.7: 删除废弃代码 → commit
        │
        ▼
[新增检查点: checkpoint-phase2-complete]
        │
        ▼
Phase 3 执行
├── Token 新增 → commit
├── H1 修复 → commit
├── H2-H4 修复 → commit
├── H5-H6 修复 → commit
└── H7 修复 → commit
        │
        ▼
最终验证
├── python main.py 启动测试
├── Light 主题切换测试
├── Dark 主题切换测试
└── ./build_macos_trial.sh 打包测试 (确保 packaging/ 修改生效)
        │
        ▼
[完成]
```

---

## 五、回滚方案

| 场景 | 命令 |
|------|------|
| Phase 2 失败 | `git reset --hard checkpoint-pre-phase2` |
| Phase 3 失败 | `git reset --hard checkpoint-phase2-complete` |
| 单个 commit 问题 | `git revert <commit>` |

---

## 六、待确认事项

1. [待确认] Token 命名: `palette.component.player_bg` (审查建议)
2. [待确认] 新增归档: `tools/integrate_adapters.py`
3. [待确认] Light 主题播放器黑色背景 (行业标准，无违和感)

---

## 七、审批签字

```
审批人: ________________
日期: ________________
备注: ________________
```

---

*文档结束*
