# 硬编码颜色详细审计清单

> 审计日期: 2025-12-18
> 范围: 仅活跃代码 (排除 DEPRECATED 文件)

---

## 一、架构确认

### 废弃文件 (不需要修复，随 Phase 2 删除)

| 文件 | 废弃标记 | 依赖链 |
|------|---------|--------|
| `components/cards/placeholder_card.py` | 文件头 DEPRECATED | → waterfall_widget → qt_app |
| `components/cards/image_card.py` | 文件头 DEPRECATED | → waterfall_widget → qt_app |
| `components/cards/video_card.py` | 文件头 DEPRECATED | → waterfall_widget → qt_app |
| `components/layouts/waterfall_widget.py` | `__init__.py` archived | → qt_app |

这些文件中的硬编码无需单独修复，随 qt_app.py 一起清理即可。

---

## 二、活跃代码硬编码详解

### 文件 1: `components/creation_components.py`

| 行号 | 代码 | 用途 | 问题 | 建议 Token |
|------|------|------|------|-----------|
| 342 | `rgba(128, 128, 128, 0.2)` | QSlider 滑槽边框 | 半透明灰色，不响应主题 | 可保留或用 `border_subtle` |
| 827 | `color: white !important;` | 自定义尺寸-比例标签 | 强制白色，Light 主题下不可见 | `palette.text.primary` |
| 853 | `color: white !important;` | 自定义尺寸-宽度标签 | 同上 | `palette.text.primary` |
| 871 | `color: white !important;` | 自定义尺寸-高度标签 | 同上 | `palette.text.primary` |
| 894 | `color: white !important;` | 自定义尺寸-锁定按钮 | 同上 | `palette.text.primary` |

**分析**: 这些 `white` 硬编码会导致 Light 主题下文字不可见（白字白底）。

---

### 文件 2: `components/widgets/video_image_upload_panel.py`

| 行号 | 代码 | 用途 | 问题 | 建议 Token |
|------|------|------|------|-----------|
| 78 | `QColor("#3a3a3a")` hover / `QColor("#2a2a2a")` normal | 上传区域背景色 | Dark 主题专用色 | `bg_hover` / `bg_card` |
| 213 | `background-color: #2a2a2a;` | 清除按钮背景 | 同上 | `bg_card` |
| 220 | `background-color: #383838;` | 清除按钮悬停 | 同上 | `bg_hover` |

**分析**: 这个面板是视频模式的图片上传区，只有 Dark 色值，Light 主题下会显得突兀。

---

### 文件 3: `components/widgets/reference_images_simple.py`

| 行号 | 代码 | 用途 | 问题 | 建议 Token |
|------|------|------|------|-----------|
| 282 | `color: #ff6b6b;` | 图片数量超限警告 (红色) | 硬编码红色 | `semantic.error` |
| 284 | `color: #0d7377;` | 图片数量正常 (青色) | 非品牌色 | `brand.main` |

**分析**: 这是参考图数量指示器，282 行是错误状态，284 行是正常状态。`#0d7377` 不是品牌色 `#5E6AD2`，应统一。

---

### 文件 4: `components/reference_assets/actions.py`

| 行号 | 代码 | 用途 | 问题 | 建议 Token |
|------|------|------|------|-----------|
| 72 | `color: #ffb347;` | 提示信息标签 (橙色) | 硬编码警告色 | `semantic.warning` 或 `accent.orange` |
| 84 | `color: #bbbbbb;` | 序号标签 (灰色) | 硬编码次要文本 | `text.secondary` |
| 86 | `color: #bbbbbb;` | 提示标签 (灰色) | 同上 | `text.secondary` |

**分析**: 这是参考资产操作相关的 UI 元素。

---

### 文件 5: `components/dialogs/image_detail_dialog.py`

| 行号 | 代码 | 用途 | 问题 | 建议 Token |
|------|------|------|------|-----------|
| 131 | `color: #bbbbbb;` | 导出状态标签 | 次要文本 | `text.secondary` |
| 177 | `color: #cccccc;` | 缩放信息标签 | 次要文本 | `text.secondary` |
| 527-528 | `#2a2a3e`, `#ffffff` | Toast 提示样式 | 硬编码背景和文字 | 使用 colors.get() |
| 538 | `#4CAF50` | 复制成功按钮 | 硬编码成功色 | `semantic.success` |

**分析**: 对话框中的信息显示元素。

---

### 文件 6: `components/dialogs/video_detail_dialog.py`

| 行号 | 代码 | 用途 | 问题 | 建议 Token |
|------|------|------|------|-----------|
| 164-165 | `#000000`, `#ffffff` | 视频播放器背景和文字 | **有意设计** | 保留 (播放器特殊) |
| 179 | `#000000` | 缩略图容器背景 | **有意设计** | 保留 (播放器特殊) |
| 276 | `color: #bbbbbb;` | 导出状态标签 | 次要文本 | `text.secondary` |
| 322 | `color: #cccccc;` | 音量标签 | 次要文本 | `text.secondary` |

**分析**: 164-179 是视频播放器区域，黑色背景是行业标准，建议保留。其他为信息标签。

---

### 文件 7: `components/delegates/image_card_delegate.py`

| 行号 | 代码 | 用途 | 问题 | 建议 |
|------|------|------|------|------|
| 278 | `QColor('#e6f4ff')` | 卡片选中时的文字颜色 | 特殊选中态 | 新增 Token 或保留 |

**分析**: `#e6f4ff` 是浅蓝色，用于选中卡片时的文字高亮。这是 UI 交互状态。

---

### 文件 8: `components/delegates/video_card_delegate.py`

| 行号 | 代码 | 用途 | 问题 | 建议 |
|------|------|------|------|------|
| 183 | `QColor('#e6f4ff')` | 卡片选中时的文字颜色 | 同上 | 同上 |

---

## 三、统计汇总

### 按文件

| 文件 | 硬编码数 | 优先级 |
|------|---------|--------|
| creation_components.py | 5 | P1 (影响 Light 主题) |
| video_image_upload_panel.py | 3 | P2 |
| reference_images_simple.py | 2 | P2 |
| reference_assets/actions.py | 3 | P2 |
| dialogs/image_detail_dialog.py | 4 | P2 |
| dialogs/video_detail_dialog.py | 2 (排除播放器) | P2 |
| delegates/image_card_delegate.py | 1 | P3 |
| delegates/video_card_delegate.py | 1 | P3 |
| **总计** | **21** | |

### 按问题类型

| 问题类型 | 数量 | 影响 |
|---------|------|------|
| Light 主题不可见 (white) | 4 | 严重 |
| 颜色不一致 (非品牌色) | 3 | 中等 |
| 不响应主题切换 | 12 | 中等 |
| 特殊选中态 | 2 | 低 |

### 特殊保留项

| 位置 | 颜色 | 原因 |
|------|------|------|
| video_detail_dialog.py:164-179 | `#000000` | 视频播放器背景，行业标准 |

---

## 四、修复优先级建议

### P1 (必须修复 - 影响功能)

- `creation_components.py` 的 `white` 硬编码 (Light 主题下不可见)

### P2 (建议修复 - 影响一致性)

- 所有 `#bbbbbb`, `#cccccc` → `text.secondary`
- 所有 `#2a2a2a`, `#3a3a3a` → `bg_card`, `bg_hover`
- 语义色统一 (`#4CAF50` → `semantic.success` 等)

### P3 (可选 - 特殊状态)

- Delegate 选中态 `#e6f4ff` - 可新增 Token 或保留

### 保留不改

- 视频播放器背景 `#000000`

---

## 五、与废弃代码对比

| 分类 | 文件数 | 硬编码数 | 处理方式 |
|------|--------|---------|---------|
| 活跃代码 | 8 | 21 | 修复 |
| 废弃代码 | 4 | ~20 | 随 qt_app 删除 |

**结论**: 实际需要修复的硬编码从 ~35 处减少到 ~21 处，且集中在 8 个活跃文件中。

---

*文档结束*
