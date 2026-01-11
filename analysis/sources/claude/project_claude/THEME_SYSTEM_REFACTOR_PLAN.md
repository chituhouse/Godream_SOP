# 主题系统重构完整执行规划

> 版本: v4.0 (审核修订版)
> 创建日期: 2025-12-18
> 最后更新: 2025-12-18 (基于架构师审核反馈)
> 状态: 待二次审批
> 审查方式: 另开窗口审查本文档

---

## ⚠️ v4.0 重大变更说明

### 审核反馈处理

架构师审核发现 `qt_app.py` 仍使用 PyQt5，提出了 **框架混用风险**。

经代码验证后，实际情况如下：

| 审核提出的问题 | 实际代码状态 | 处理方式 |
|---------------|-------------|----------|
| qt_app.py 使用 PyQt5 | ✅ 确实如此 | **qt_app.py 是废弃的旧入口，应删除** |
| 框架混用会崩溃 | ✅ 正确 | **main.py 是真正入口，已全面 PySide6** |
| handler 函数需要提取 | ❌ 不需要 | **新架构直接实例化 DetailDialog** |
| 需要 _build_global_stylesheet | ❌ 不需要 | **MainWindow 已自行处理全局样式** |

### 代码验证结果

```
真正的主入口: main.py (PySide6) ✅
    └── MainWindow (components/main_window.py, PySide6) ✅
        ├── 第 41 行: theme_engine.load_theme("linear_dark.json")
        ├── 第 306 行: self._apply_theme_styles()
        ├── ImageModeWidget → 第 276 行直接使用 ImageDetailDialog ✅
        └── VideoModeWidget → 第 234 行直接使用 VideoDetailDialog ✅

废弃的旧入口: qt_app.py (PyQt5) ❌
    ├── 第 39-51 行: PyQt5 导入
    ├── 第 81 行: StyleManager 使用
    └── 第 96-114 行: set_*_detail_handler 注册 (废弃机制)

components/ 目录统计:
    - 41 个活跃 .py 文件
    - 168 处 PySide6 导入
    - 0 处 PyQt5 导入 ✅
```

### 计划变更摘要

| 原计划 | 新计划 | 变更原因 |
|--------|--------|----------|
| A1.1 创建 detail_handlers.py | **删除** | 新架构不需要 handler 注册机制 |
| A1.2 修改 qt_app.py 导入 | **删除** | qt_app.py 整体废弃 |
| B1.3 添加 _build_global_stylesheet | **删除** | MainWindow 已处理全局样式 |
| B1.4 修改 qt_app.py 样式逻辑 | **改为删除 qt_app.py** | 废弃文件直接删除 |
| - | **新增: 删除 qt_app.py** | 清理 PyQt5 遗留 |

---

## 目录

1. [背景与需求](#一-背景与需求)
2. [审查发现汇总](#二-审查发现汇总)
3. [决策记录](#三-决策记录)
4. [A1: 废弃组件处理](#四-a1-废弃组件处理)
5. [B1: StyleManager 迁移](#五-b1-stylemanager-迁移)
6. [C1: 调色板完整更新](#六-c1-调色板完整更新)
7. [遗漏问题与后续规划](#七-遗漏问题与后续规划)
8. [执行顺序与依赖](#八-执行顺序与依赖)
9. [风险评估与回滚](#九-风险评估与回滚)
10. [审批检查清单](#十-审批检查清单)

---

## 一、背景与需求

### 1.1 用户原始需求

用户提出的原始要求：

> "检查现在所有的前端代码,看看现在的主题转换系统,有很多组件,再检查下链接信号,看看有没有哪些组件的颜色\样式还是自定义,不是用标准组件的,没有用标准组件.或者说主题转换的颜色还是自定义,没有从主题josn 调色板文件取颜色的,帮我找找,检查这些信号连接.然后把所有的问题列清单给我看,然后,现在有的问题,你也可以重点审查一下,我也给你一个我发现的问题清单,你一个一个审查,然后找出问题,以及不符合系统一致性的,地方，没有采用统一主题设置,或者自定义,或者硬编码,或者组件不是现在的 pyside6 标准组件的,或者确实内容的,都帮我列清单,提建议,说明理由,给出规划以及执行方案.我来审批."

### 1.2 需求拆解

| 需求项 | 描述 |
|--------|------|
| 检查主题转换系统 | 审查所有组件的主题信号连接情况 |
| 检查硬编码颜色 | 找出没有使用主题 JSON 调色板的颜色值 |
| 检查标准组件 | 识别非 PySide6 标准组件 |
| 检查系统一致性 | 找出不符合统一主题设置的地方 |
| 列出问题清单 | 分类整理所有发现的问题 |
| 提供建议和理由 | 说明每个修改的原因和设计考虑 |
| 给出执行方案 | 详细规划执行步骤 |
| 用户审批 | 所有修改需用户确认后执行 |

### 1.3 用户补充要求

用户后续补充：

> "详细规划上述计划,给出原因,建议\理由,以及详细规划,防止遗漏,你应该把上面发现的问题,一起保存到一个文档中,或者你的 plan 中,分类列清单,全局审视一下.然后让我选择最终决策,给出建议.我现在的系统用 dark 和 light 的主题系统是对的,而且我现在的设计风格是 linear,你可以顺便检查下主题调色板,有哪些地方是不符合linear 设计原则的,比如现在的死白背景."

### 1.4 项目技术背景

| 项目属性 | 值 |
|----------|-----|
| 项目名称 | 鸽梦 (GoDream) |
| 当前版本 | v1.4.1 |
| UI 框架 | PySide6 |
| 主题系统 | Token 化设计，支持明暗主题 |
| 设计风格 | Linear（项目管理工具风格） |
| 主题文件 | `config/themes/linear_dark.json`, `linear_light.json` |
| 样式系统 | `utils/style_system.py` (UnifiedStyleSystem) |
| 主题引擎 | `utils/theme_engine.py` (ThemeEngine) |

---

## 二、审查发现汇总

### 2.1 审查范围

审查了以下目录和文件：
- `components/` - 所有 UI 组件
- `utils/` - 工具类（style_system, theme_engine, ui_utils）
- `config/themes/` - 主题配置文件
- `qt_app.py` - 主入口

### 2.2 问题统计

| 问题类型 | 数量 | 严重程度 |
|----------|------|----------|
| 硬编码颜色（严重） | 15 处 | 🔴 高 |
| 硬编码颜色（中等） | 12 处 | 🟡 中 |
| 硬编码颜色（轻微） | 8 处 | 🟢 低 |
| 缺少信号连接 | 10 个组件 | 🟡 中 |
| 废弃组件未清理 | 4 个 | 🟢 低 |
| 调色板设计问题 | 5 处 | 🟡 中 |
| 双调色板系统并存 | 1 处 | 🔴 高 |

### 2.3 问题分布图

```
项目根目录
├── qt_app.py                      [🟡 B1] StyleManager 使用
├── components/
│   ├── cards/
│   │   ├── placeholder_card.py    [🔴 A1] 完全硬编码，废弃组件
│   │   ├── video_card.py          [🔴 A1] 完全硬编码，废弃组件
│   │   └── image_card.py          [🔴 A1] 完全硬编码，废弃组件
│   ├── widgets/
│   │   ├── image_preview_dialog.py [🔴 遗漏] 完全硬编码
│   │   ├── toast_manager.py        [🟡 遗漏] 缺信号连接
│   │   ├── video_image_upload_panel.py [🟡 遗漏] 缺信号连接
│   │   └── integrated_reference_panel.py [🟡 遗漏] 部分硬编码
│   ├── dialogs/
│   │   └── image_detail_dialog.py  [🟡 遗漏] 部分硬编码
│   ├── modes/
│   │   ├── image_mode_widget.py    [🟢 遗漏] fallback不一致
│   │   └── video_mode_widget.py    [🟢 遗漏] fallback不一致
│   ├── forms/
│   │   ├── parameter_form_standard.py [🟡 遗漏] 缺信号连接
│   │   └── schema_form_renderer.py    [🟡 遗漏] 缺信号连接
│   ├── layouts/
│   │   └── waterfall_widget.py     [🔴 A1] 废弃组件
│   └── creation_components.py      [🟡 B1] StyleManager 使用
├── utils/
│   ├── ui_utils.py                 [🔴 B1] StyleManager 定义
│   └── style_system.py             [🟡 B1] StyleManager 依赖
└── config/themes/
    ├── linear_dark.json            [🟡 C1] 缺少 token
    └── linear_light.json           [🔴 C1] 死白问题
```

### 2.4 硬编码颜色详细清单

#### 2.4.1 严重问题（完全硬编码，无主题响应）

**placeholder_card.py** (已标记 DEPRECATED):
| 行号 | 硬编码值 | 用途 | 应替换为 |
|------|----------|------|----------|
| 45 | `#242424` | 背景色 | `palette.neutral.bg_card` |
| 46 | `#555555` | 边框色 | `palette.neutral.border_strong` |
| 58 | `#d0d0d0` | 状态文本 | `palette.text.secondary` |
| 65 | `#999999` | 提示词文本 | `palette.text.disabled` |
| 70 | `#666666` | 计时器文本 | `palette.text.disabled` |
| 92 | `#d0d0d0` | pending 状态 | `palette.text.secondary` |
| 95 | `#4CAF50` | generating 状态 | `palette.semantic.success` |
| 98 | `#2196F3` | completed 状态 | `palette.semantic.info` |
| 103 | `#f44336` | failed 状态 | `palette.semantic.error` |

**video_card.py** (已标记 DEPRECATED):
| 行号 | 硬编码值 | 用途 | 应替换为 |
|------|----------|------|----------|
| 85 | `#1a1a1a` | 卡片背景 | `palette.neutral.bg_card` |
| 86 | `#3a3a5e` | 边框 | `palette.neutral.border_subtle` |
| 91 | `#FF6B35` | hover 边框 | `palette.accent.orange` |
| 107-109 | `#ccc` | 图片边框 | `palette.neutral.border_subtle` |
| 124 | `rgba(0,120,212,210)` | 徽章背景 | `palette.brand.main` |
| 125 | `#ffffff` | 徽章文字 | `palette.text.on_brand` |
| 142 | `#FF6B35`, `#2a2a2a` | 错误状态 | `palette.semantic.warning`, `palette.neutral.bg_card` |
| 156 | `#ffffff` | 提示词文字 | `palette.text.primary` |
| 174, 188, 195, 202 | `#cccccc` | 信息文字 | `palette.text.secondary` |
| 236-237 | `rgba(0,0,0,0.75)`, `#ffffff` | 遮罩 | `palette.overlay.dark`, `palette.text.on_brand` |
| 490-501 | 菜单样式 | 完全硬编码 | 统一菜单样式 |

**image_card.py** (已标记 DEPRECATED):
与 video_card.py 结构相同，硬编码位置类似。

**image_preview_dialog.py** (活跃组件):
| 行号 | 硬编码值 | 用途 | 应替换为 |
|------|----------|------|----------|
| 35 | `rgba(0,0,0,0.7)` | 控制栏背景 | `palette.overlay.dark` |
| 45-51 | `rgba(255,255,255,0.1/0.3)` | 按钮背景/hover | `palette.overlay.light` |
| 70-76 | 同上 | 同上 | 同上 |

**utils/ui_utils.py** (StyleManager):
| 行号 | 问题 | 说明 |
|------|------|------|
| 146-160 | `DARK_COLORS` 独立调色板 | 与 theme_engine 颜色不一致 |
| 164-178 | `LIGHT_COLORS` 独立调色板 | 与 theme_engine 颜色不一致 |
| 389-406 | `#DetailDialog` 样式 | 完全硬编码，颜色如 `#555`, `#2a2a3e`, `#FF6B35` |

#### 2.4.2 中等问题（部分硬编码或 fallback 不一致）

**main_window.py**:
| 行号 | 硬编码值 | 问题 |
|------|----------|------|
| 350, 367 | `rgba(128,128,128,0.1)` | 悬停背景硬编码 |
| 457 | `rgba(0,0,0,0.8)` | 遮罩硬编码 |

**video_mode_widget.py**:
| 行号 | 硬编码值 | 问题 |
|------|----------|------|
| 2270-2271 | `#666`, `#999` | 禁用状态硬编码 |
| 2336 | `#999` | 禁用文字硬编码 |

**image_mode_widget.py**:
| 行号 | 硬编码值 | 问题 |
|------|----------|------|
| 1709 | `rgba(39,201,63,0.2)` | 成功背景硬编码 |

**image_detail_dialog.py**:
| 行号 | 硬编码值 | 问题 |
|------|----------|------|
| 131 | `#bbbbbb` | 导出状态标签 |
| 177 | `#cccccc` | 缩放信息标签 |
| 527-538 | `#2a2a3e`, `#555`, `#4CAF50` | 复制按钮样式 |
| 716 | `#888` | 字体提示标签 |

**integrated_reference_panel.py**:
| 行号 | 硬编码值 | 问题 |
|------|----------|------|
| 82 | `#ffffff` | 白色常量 |
| 411-419 | `rgba(255,255,255,...)` | 拖拽区域样式 |

**reference_assets/actions.py**:
| 行号 | 硬编码值 | 问题 |
|------|----------|------|
| 72 | `#ffb347` | 信息标签（橙色） |
| 84, 86 | `#bbbbbb` | 索引和提示标签 |

#### 2.4.3 Fallback 颜色不一致

| 文件 | Token | 当前 Fallback | 主题实际值 | 问题 |
|------|-------|---------------|------------|------|
| main_window.py:337 | `text.disabled` | `#666` | `#444444` | 不一致 |
| video_mode_widget.py:128 | `bg_input` | `#2d2d2d` | `#101010` | 不一致 |
| image_mode_widget.py:173 | `bg_input` | `#2d2d2d` | `#101010` | 不一致 |

### 2.5 信号连接问题

#### 已正确连接的组件（13个）

| 组件 | 文件 | 连接代码位置 |
|------|------|--------------|
| MainWindow | main_window.py | 307 行 |
| ImageModeWidget | image_mode_widget.py | 143 行 |
| VideoModeWidget | video_mode_widget.py | 116, 199 行 |
| SettingsPage | settings_page.py | 48, 127 行 |
| ImageDetailDialog | image_detail_dialog.py | 47 行 |
| VideoDetailDialog | video_detail_dialog.py | 58 行 |
| ImageHistoryView | image_history_view.py | 66 行 |
| VideoHistoryView | video_history_view.py | 62 行 |
| ImageCardDelegate | image_card_delegate.py | 35 行 |
| VideoCardDelegate | video_card_delegate.py | 38 行 |
| ReferenceGalleryWidget | gallery.py | 174 行 |
| ReferenceAssetsPanel | reference_assets_panel.py | 42, 219 行 |
| IntegratedReferencePanel | integrated_reference_panel.py | 68, 390 行 |

#### 缺少信号连接的组件（10个）

| 组件 | 文件 | 影响 | 优先级 |
|------|------|------|--------|
| **ToastWidget** | toast_manager.py | Toast 主题切换后颜色不更新 | 🟡 中 |
| **VideoImageUploadPanel** | video_image_upload_panel.py | 上传面板不响应主题 | 🔴 高 |
| **ParameterFormWidget** | parameter_form_standard.py | 参数表单不响应主题 | 🔴 高 |
| **SchemaFormRenderer** | schema_form_renderer.py | Schema 表单不响应主题 | 🔴 高 |
| **ImagePreviewDialog** | image_preview_dialog.py | 预览对话框硬编码 | 🟡 中 |
| **ReferenceImagesWidget** | reference_images_simple.py | 参考图组件不响应主题 | 🟢 低 |
| **PlaceholderCard** | placeholder_card.py | 废弃组件 | 🟢 低 |
| **VideoCard** | video_card.py | 废弃组件 | 🟢 低 |
| **ImageCard** | image_card.py | 废弃组件 | 🟢 低 |
| **actions.py Dialog** | reference_assets/actions.py | 预览对话框硬编码 | 🟡 中 |

### 2.6 调色板问题分析

#### Linear 设计风格特点

Linear 是一款项目管理工具，以精致、现代的 UI 设计著称：

| 特性 | 描述 |
|------|------|
| 柔和背景 | 避免纯白/纯黑，使用微调的灰度 |
| 微妙层次 | 通过细微的色差创建视觉层次 |
| 低对比边框 | 边框与背景色差小，不刺眼 |
| 品牌紫色 | 主色调为紫色 (#5E6AD2) |
| 一致的圆角 | 6-8px 的圆角系统 |
| 精致阴影 | 淡阴影，不突兀 |

#### 当前调色板问题

**Light 主题 "死白" 问题**:

| Token | 当前值 | 问题 | 建议值 |
|-------|--------|------|--------|
| `neutral.bg_app` | `#FFFFFF` | 纯白太刺眼 | `#FBFBFC` |
| `neutral.bg_panel` | `#FFFFFF` | 无层次感 | `#FFFFFF` |
| `neutral.bg_input` | `#FFFFFF` | 与背景无区分 | `#F7F7F8` |
| `neutral.bg_surface` | `#FFFFFF` | 无层次感 | `#FAFAFA` |

**缺少的 Token**:

| 缺失 Token | 用途 | 建议值 (Dark) | 建议值 (Light) |
|------------|------|---------------|----------------|
| `overlay.dark` | 遮罩层 | `rgba(0,0,0,0.75)` | `rgba(0,0,0,0.5)` |
| `overlay.light` | 浅色遮罩 | `rgba(255,255,255,0.1)` | `rgba(0,0,0,0.05)` |
| `semantic.success_subtle` | 成功背景 | `rgba(39,201,63,0.15)` | `rgba(34,165,71,0.1)` |
| `semantic.warning_subtle` | 警告背景 | `rgba(255,188,46,0.15)` | `rgba(229,165,0,0.1)` |
| `semantic.error_subtle` | 错误背景 | `rgba(255,95,86,0.15)` | `rgba(229,77,66,0.1)` |
| `accent.orange` | 橙色强调 | `#FF6B35` | `#E55A2B` |
| `text.tertiary` | 三级文本 | `#666666` | `#888888` |

### 2.7 双调色板系统问题

**问题描述**:

项目中存在两套独立的调色板系统：

1. **StyleManager** (`utils/ui_utils.py`)
   - 独立的 `DARK_COLORS` 和 `LIGHT_COLORS` 字典
   - 用于生成全局样式表
   - 颜色与主题系统不一致

2. **ThemeEngine** (`utils/theme_engine.py`)
   - 从 JSON 文件加载 Token
   - 统一的主题系统
   - 正确的 Linear 设计颜色

**颜色冲突对比**:

| 颜色名 | StyleManager | ThemeEngine | 差异 |
|--------|--------------|-------------|------|
| primary | `#0078d4` (蓝) | `#5E6AD2` (紫) | 完全不同 |
| background | `#1e1e1e` | `#121212` | 不一致 |
| surface | `#2d2d2d` | `#181818` | 不一致 |
| success | `#107c10` | `#27C93F` | 不一致 |
| warning | `#ff8c00` | `#FFBC2E` | 不一致 |
| error | `#d13438` | `#FF5F56` | 不一致 |

**影响**:
- 主题切换时全局样式不更新（只在启动时设置一次）
- UI 颜色不一致（部分蓝色，部分紫色）
- 维护困难

---

## 三、决策记录

### 3.1 用户选择的方案

用户选择了以下方案：

| 决策点 | 选项 | 用户选择 | 理由 |
|--------|------|----------|------|
| **A** 废弃组件处理 | A1 删除 / A2 修复 / A3 不管 | **A1 删除** | 清理代码库 |
| **B** StyleManager 处理 | B1 删除 / B2 代理 / B3 不管 | **B1 删除** | 彻底解决技术债务 |
| **C** 调色板更新 | C1 完整更新 / C2 仅修复死白 / C3 不管 | **C1 完整更新** | 一次性解决所有设计问题 |

### 3.2 B 决策详细讨论

用户询问了 B 决策的背景：

> "我想先了解 B 决策的理由,为什么不是删除掉,而是兼容就代码,这是什么代码?为什么会存在,是什么作用?"

**调查结果**:

StyleManager 的历史和作用：
1. **起源**: 早期开发阶段创建的样式管理类
2. **核心功能**:
   - 管理深色/浅色主题的调色板
   - 生成按钮、输入框等组件的样式
   - 提供全局样式表
3. **当前使用情况**:
   - `qt_app.py:823-824` - 应用启动时生成全局样式表（**关键**）
   - `creation_components.py:56` - 获取颜色（8 处）
   - `style_system.py:78-79` - 内部 fallback
   - `settings_page.py:17` - 只导入未使用

**最终决策变更**:

原建议 B2（代理）改为 **B1（删除）**，理由：
1. StyleManager 是**技术债务**
2. 全局样式表不响应主题切换是**严重 bug**
3. 与主题系统的颜色冲突导致**视觉不一致**
4. 长远来看必须解决

### 3.3 遗漏问题决策

用户选择：**仅执行 A1+B1+C1**

遗漏问题留待后续迭代，理由：
1. 核心问题已解决
2. 降低一次性改动风险
3. 可逐步验证效果

---

## 四、A1: 废弃组件处理 (v4.0 简化版)

### 4.1 调查过程

**Step 1: 搜索废弃组件引用**

```bash
grep -r "PlaceholderCard|VideoCard|ImageCard" --include="*.py"
```

**v3.0 发现**:
- 废弃组件被 `WaterfallWidget` 使用
- `WaterfallWidget` 也已废弃，被 `HistoryViewAdapter` 替代
- ~~`set_image_detail_handler` 和 `set_video_detail_handler` 函数仍在使用~~

**v4.0 更正** (基于架构师审核):

经验证，`set_*_detail_handler` 只被 **废弃的 qt_app.py** 使用：
```python
# qt_app.py:96-97 (废弃文件，使用 PyQt5)
from components.cards.image_card import set_image_detail_handler
from components.cards.video_card import set_video_detail_handler
```

**真正的主入口 main.py** 使用的 **新架构**：
```python
# components/modes/image_mode_widget.py:276
dialog = ImageDetailDialog(rec, all_images, current_index, self)

# components/modes/video_mode_widget.py:234
self._cached_detail_dialog = VideoDetailDialog(rec, all_videos, current_index, self)
```

**结论**: handler 注册机制是废弃架构的一部分，**不需要提取**，可直接删除。

### 4.2 废弃组件清单 (v4.0 更新)

| 组件 | 文件路径 | 状态 | 说明 |
|------|----------|------|------|
| PlaceholderCard | `components/cards/placeholder_card.py` | DEPRECATED | 第 6 行标注 |
| VideoCard | `components/cards/video_card.py` | DEPRECATED | 第 6-7 行标注 |
| ImageCard | `components/cards/image_card.py` | DEPRECATED | 第 6-7 行标注 |
| WaterfallWidget | `components/layouts/waterfall_widget.py` | DEPRECATED | 被 HistoryViewAdapter 替代 |
| **qt_app.py** | `qt_app.py` | **DEPRECATED (新增)** | PyQt5 旧入口，应删除 |

### 4.3 执行方案 (v4.0 简化版)

> ⚠️ **变更说明**: 原 A1.1 (创建 detail_handlers.py) 和 A1.2 (修改 qt_app.py 导入) 已删除。
> 原因：新架构不依赖 handler 注册机制，qt_app.py 本身也是废弃文件。

#### Step A1.1: 删除废弃卡片组件

**删除文件**:
- `components/cards/placeholder_card.py` (126 行)
- `components/cards/video_card.py` (585 行)
- `components/cards/image_card.py` (506 行)

**删除原因**:
- 已标记为 DEPRECATED
- 被 Delegate 模式替代
- 包含 35+ 处硬编码颜色
- 新架构 (main.py → MainWindow) 不使用这些组件

#### Step A1.2: 更新 cards/__init__.py

**当前内容**:
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cards module"""

from .video_card import VideoCard
from .image_card import ImageCard

__all__ = ['VideoCard', 'ImageCard']
```

**修改后** (v4.0 简化):
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cards module - 已迁移到 Delegate 模式"""

# 注意: VideoCard, ImageCard, PlaceholderCard 已废弃并删除
# 详情对话框现由 mode_widget 直接实例化 DetailDialog
# 参见: components/modes/image_mode_widget.py:276
#       components/modes/video_mode_widget.py:234

__all__ = []
```

#### Step A1.3: 删除 WaterfallWidget

**删除文件**: `components/layouts/waterfall_widget.py` (510 行)

**删除原因**:
- `qt_app.py:99` 声明 "WaterfallWidget 已废弃，现使用 HistoryViewAdapter"
- `components/layouts/__init__.py` 声明 "WaterfallWidget has been archived"
- 是废弃卡片组件的唯一使用者

#### Step A1.4: 更新 layouts/__init__.py

**检查当前内容**:
```python
# WaterfallWidget has been archived to archive/legacy/
```

**确认**: 如果已经注释或移除了 WaterfallWidget 的导出，则无需修改。否则需要清理。

#### Step A1.5: 删除废弃的旧入口 qt_app.py (v4.0 新增)

**删除文件**: `qt_app.py` (~900 行)

**删除原因**:
- 仍使用 **PyQt5**（第 39-51 行），与项目其他部分的 PySide6 不兼容
- 框架混用会导致 Segmentation Fault 或类型不匹配错误
- 真正的主入口已迁移到 **main.py**
- 包含对废弃组件的引用 (StyleManager, set_*_detail_handler)
- 保留会造成维护混乱

**替代方案** (如需保留历史):
```bash
# 可选：移到 archive 目录而非直接删除
mv qt_app.py archive/legacy/qt_app_pyqt5.py
```

### 4.4 A1 影响分析 (v4.0 更新)

| 操作 | 文件 | 类型 | 行数变化 |
|------|------|------|----------|
| 修改 | `components/cards/__init__.py` | ✏️ | ~10 行 |
| 删除 | `components/cards/placeholder_card.py` | 🗑️ | -126 |
| 删除 | `components/cards/video_card.py` | 🗑️ | -585 |
| 删除 | `components/cards/image_card.py` | 🗑️ | -506 |
| 删除 | `components/layouts/waterfall_widget.py` | 🗑️ | -510 |
| **删除** | **`qt_app.py`** | 🗑️ | **-900** |
| 可能修改 | `components/layouts/__init__.py` | ✏️ | ~2 行 |

**净变化**: 减少约 **2627** 行代码 (原 1680 + qt_app.py 900)

### 4.5 A1 解决的问题 (v4.0 更新)

| 问题 | 解决方式 |
|------|----------|
| 35+ 处硬编码颜色 | 删除文件，无需修复 |
| 废弃组件占用代码库 | 清理干净 |
| 潜在的混淆和误用 | 移除风险 |
| 维护负担 | 减少需维护的代码 |
| **PyQt5/PySide6 框架混用风险** | **删除 PyQt5 旧入口** |
| **StyleManager 在旧入口的使用** | **随 qt_app.py 一起删除** |

---

## 五、B1: StyleManager 迁移

### 5.1 调查过程

**Step 1: 搜索 StyleManager 引用**

```bash
grep -r "StyleManager" --include="*.py"
```

**活跃代码中的引用** (排除 archive、backup):

| 文件 | 行号 | 使用方式 |
|------|------|----------|
| `qt_app.py` | 81 | import |
| `qt_app.py` | 823 | 实例化 |
| `qt_app.py` | 824 | 生成全局样式表 |
| `creation_components.py` | 23 | import |
| `creation_components.py` | 56 | 实例化 |
| `creation_components.py` | 345, 349, 350, 356, 357, 360 | 获取颜色 (slider 样式) |
| `creation_components.py` | 812 | 获取颜色 (容器背景) |
| `creation_components.py` | 1412 | 获取颜色 (预览标签) |
| `settings_page.py` | 17 | import (未使用) |
| `style_system.py` | 78-79 | 内部实例化 |
| `style_system.py` | 117-119 | setter 方法 |

**Step 2: 分析 build_global_stylesheet**

`DpiScaler.build_global_stylesheet(style_manager)` 生成的样式包括：

| 组件 | 样式内容 |
|------|----------|
| QMainWindow | 背景色 |
| QWidget | 文字颜色、字号 |
| QFrame | 背景、边框、圆角 |
| QPushButton | 按钮样式（来自 generate_button_style） |
| QLineEdit/QTextEdit | 输入框样式（来自 generate_input_style） |
| QScrollBar | 滚动条样式 |
| QMenu | 菜单样式 |
| QMessageBox | 消息框样式 |
| #ParamPanel | 参数面板作用域样式 |
| #DetailDialog | 详情对话框作用域样式 |

**关键问题**: 这些样式只在启动时设置一次，主题切换时不会更新！

### 5.2 颜色映射表

StyleManager 颜色 → Theme Engine Token：

| StyleManager Key | StyleManager 值 | Theme Token | JSON 值 (Dark) | 差异 |
|------------------|-----------------|-------------|----------------|------|
| `primary` | `#0078d4` | `palette.brand.main` | `#5E6AD2` | 🔴 蓝→紫 |
| `primary_hover` | `#106ebe` | `palette.brand.hover` | `#6F7BF4` | 🔴 不同 |
| `primary_pressed` | `#005a9e` | `palette.brand.pressed` | `#4C55AA` | 🔴 不同 |
| `background` | `#1e1e1e` | `palette.neutral.bg_app` | `#121212` | 🟡 略深 |
| `surface` | `#2d2d2d` | `palette.neutral.bg_card` | `#181818` | 🟡 略深 |
| `surface_hover` | `#3a3a3a` | `palette.neutral.bg_hover` | `#242424` | 🟡 略深 |
| `border` | `#3a3a3a` | `palette.neutral.border_subtle` | `#2A2A2A` | 🟡 略深 |
| `text` | `#ffffff` | `palette.text.primary` | `#EEEEEE` | 🟢 接近 |
| `text_secondary` | `#cccccc` | `palette.text.secondary` | `#888888` | 🟡 不同 |
| `text_disabled` | `#888888` | `palette.text.disabled` | `#444444` | 🟡 不同 |
| `success` | `#107c10` | `palette.semantic.success` | `#27C93F` | 🔴 不同 |
| `warning` | `#ff8c00` | `palette.semantic.warning` | `#FFBC2E` | 🟡 接近 |
| `error` | `#d13438` | `palette.semantic.error` | `#FF5F56` | 🟡 不同 |
| `info` | `#0078d4` | `palette.semantic.info` | `#5E6AD2` | 🔴 蓝→紫 |

**重要**: 迁移后颜色会从蓝色系变为 Linear 紫色系，这是**预期行为**。

### 5.3 执行方案

#### Step B1.0: Git 备份

```bash
git add -A
git commit -m "backup: 准备执行主题系统重构 (A1+B1+C1)"
```

**原因**: 确保可以回滚。

#### Step B1.1: 修改 creation_components.py

**5.3.1.1 删除导入和实例化**

| 行号 | 当前代码 | 修改 |
|------|----------|------|
| 23 | `from utils.ui_utils import StyleManager` | 删除此行 |
| 56 | `self.style_manager = StyleManager('dark')` | 删除此行 |

**5.3.1.2 添加主题信号连接**

在 `__init__` 方法中，第 58 行附近添加：

```python
# 连接主题切换信号
unified_style_system.styleChanged.connect(self._on_theme_changed)
```

**5.3.1.3 添加主题响应方法**

在类中添加以下方法：

```python
def _on_theme_changed(self):
    """响应主题切换，更新动态样式"""
    self._update_slider_style()
    self._update_container_styles()

def _update_slider_style(self):
    """更新 slider 样式（支持主题切换）"""
    colors = unified_style_system.get_colors()
    self.guidance_slider.setStyleSheet(f"""
    QSlider::groove:horizontal {{
        border: 1px solid rgba(128, 128, 128, 0.2);
        height: 4px;
        background: {colors.get('palette.neutral.bg_card')};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {colors.get('palette.brand.main')};
        border: 2px solid {colors.get('palette.brand.main')};
        width: 14px;
        margin: -5px 0;
        border-radius: 7px;
    }}
    QSlider::handle:horizontal:hover {{
        background: {colors.get('palette.brand.hover')};
        border-color: {colors.get('palette.brand.hover')};
    }}
    QSlider::sub-page:horizontal {{
        background: {colors.get('palette.brand.main')};
        border-radius: 2px;
    }}
    """)

def _update_container_styles(self):
    """更新容器样式（支持主题切换）"""
    colors = unified_style_system.get_colors()
    # 更新自定义尺寸容器
    if hasattr(self, '_custom_size_container'):
        self._custom_size_container.setStyleSheet(f"""
        QWidget {{
            background-color: {colors.get('palette.neutral.bg_app')};
            border: none;
            border-radius: 8px;
            padding: 0px;
            margin: 8px 0;
        }}
        """)
```

**5.3.1.4 替换颜色获取**

| 行号 | 原代码 | 新代码 | 说明 |
|------|--------|--------|------|
| 341-363 | slider 样式设置 | 调用 `self._update_slider_style()` | 提取为方法，初始化时调用 |
| 345 | `self.style_manager.get_color('surface')` | `colors.get('palette.neutral.bg_card')` | 槽背景 |
| 349 | `self.style_manager.get_color('primary')` | `colors.get('palette.brand.main')` | 滑块背景 |
| 350 | `self.style_manager.get_color('primary')` | `colors.get('palette.brand.main')` | 滑块边框 |
| 356 | `self.style_manager.get_color('primary_hover')` | `colors.get('palette.brand.hover')` | 滑块 hover 背景 |
| 357 | `self.style_manager.get_color('primary_hover')` | `colors.get('palette.brand.hover')` | 滑块 hover 边框 |
| 360 | `self.style_manager.get_color('primary')` | `colors.get('palette.brand.main')` | 进度条颜色 |
| 812 | `self.style_manager.get_color('background')` | `colors.get('palette.neutral.bg_app')` | 容器背景 |
| 1412 | `self.style_manager.get_color('border')` | `colors.get('palette.neutral.border_subtle')` | 预览边框 |
| 1412 | `self.style_manager.get_color('surface')` | `colors.get('palette.neutral.bg_card')` | 预览背景 |

**设计考虑**:
- 将样式设置提取为独立方法，便于主题切换时调用
- 使用 `unified_style_system.get_colors()` 统一获取颜色
- 保持原有的视觉效果，只是颜色来源改变

#### Step B1.2: 修改 settings_page.py

**修改位置**: 第 17 行

**当前代码**:
```python
from utils.ui_utils import StyleManager, IconManager
```

**修改后**:
```python
from utils.ui_utils import IconManager
```

**原因**: StyleManager 只是导入但从未使用，清理无用导入。

#### Step B1.3: 修改 style_system.py (v4.0 简化版)

**移除 StyleManager 依赖（死代码清理）**

经验证，`_style_manager` 属性在 `style_system.py` 中只被设置，从未被实际使用：

| 行号 | 当前代码 | 修改 |
|------|----------|------|
| 45 | `self._style_manager = None` | 删除此行 |
| 78-79 | `from utils.ui_utils import StyleManager`<br>`self._style_manager = StyleManager()` | 删除这两行 |
| 117-119 | `def set_style_manager(self, style_manager):...` | 删除整个方法 |

> ⚠️ **v4.0 变更**: 原计划的 `_build_global_stylesheet` 方法**已删除**。
>
> **原因**: 经代码验证，`MainWindow._apply_theme_styles()` (main_window.py:309)
> 已经处理了全局样式应用，包括：
> - 窗口背景 (第 315 行)
> - 侧边栏样式 (第 329 行)
> - 按钮样式 (第 340, 357 行)
> - 状态栏样式 (第 380 行)
>
> 不需要在 `style_system.py` 中重复实现。

#### ~~Step B1.4: 修改 qt_app.py~~ (v4.0 删除)

> ⚠️ **v4.0 变更**: 此步骤已删除。
>
> **原因**: `qt_app.py` 是废弃的 PyQt5 旧入口，将在 **A1.5** 中直接删除，
> 无需修改。真正的主入口 `main.py` 不使用 StyleManager。

#### Step B1.4: 清理 ui_utils.py (原 B1.5)

**5.3.5.1 删除 StyleManager 类**

删除第 137-353 行的 `StyleManager` 类（约 216 行）。

**5.3.5.2 删除 build_global_stylesheet 方法**

删除第 360-408 行的 `DpiScaler.build_global_stylesheet` 方法（约 48 行）。

**验证**: 确保没有其他地方引用这些代码。

### 5.4 B1 影响分析 (v4.0 更新)

| 操作 | 文件 | 类型 | 变化 |
|------|------|------|------|
| 修改 | `components/creation_components.py` | ✏️ | 删除导入，替换 8 处颜色获取，添加主题响应 |
| 修改 | `components/settings_page.py` | ✏️ | 删除 1 行导入 |
| 修改 | `utils/style_system.py` | ✏️ | 删除 StyleManager 死代码依赖 |
| ~~修改~~ | ~~`qt_app.py`~~ | ~~✏️~~ | ~~已移至 A1.5 删除~~ |
| 修改 | `utils/ui_utils.py` | ✏️ | 删除 StyleManager 类和 build_global_stylesheet 方法 |

**净变化**: 减少约 **264** 行代码，增加约 **50** 行新代码
(v4.0: 原计划的 _build_global_stylesheet 80 行不再需要)

### 5.5 B1 解决的问题 (v4.0 更新)

| 问题 | 解决方式 |
|------|----------|
| 双调色板系统并存 | 删除 StyleManager，统一使用 theme_engine |
| ~~主题切换全局样式不更新~~ | ~~已由 MainWindow._apply_theme_styles() 处理~~ |
| 颜色不一致（蓝 vs 紫） | 统一使用 Linear 紫色 |
| 技术债务 | 清理遗留代码 |
| **style_system.py 死代码** | **删除未使用的 _style_manager** |

### 5.6 预期视觉变化

迁移后，以下元素的颜色会从蓝色变为 Linear 紫色：

| 元素 | 变化 |
|------|------|
| 主按钮背景 | `#0078d4` → `#5E6AD2` |
| 主按钮 hover | `#106ebe` → `#6F7BF4` |
| Slider 滑块 | `#0078d4` → `#5E6AD2` |
| 菜单选中项 | `#0078d4` → `#5E6AD2` |
| 背景色 | `#1e1e1e` → `#121212` (略深) |

**这是预期行为**，使 UI 与 Linear 设计风格一致。

---

## 六、C1: 调色板完整更新

### 6.1 更新目标

| 目标 | 说明 |
|------|------|
| 修复死白问题 | Light 主题背景从纯白改为微灰 |
| 添加缺失 Token | overlay、subtle、accent、tertiary |
| 提高层次感 | 输入框、表面等有区分 |
| 符合 Linear 设计 | 柔和、不刺眼 |

### 6.2 执行方案

#### Step C1.1: 更新 linear_light.json

**文件路径**: `config/themes/linear_light.json`

**完整替换内容**:
```json
{
    "name": "Linear Light",
    "type": "light",
    "palette": {
        "brand": {
            "main": "#5E6AD2",
            "hover": "#4B56B2",
            "pressed": "#3A4391",
            "subtle": "rgba(94, 106, 210, 0.08)"
        },
        "semantic": {
            "success": "#22A547",
            "success_subtle": "rgba(34, 165, 71, 0.1)",
            "warning": "#E5A500",
            "warning_subtle": "rgba(229, 165, 0, 0.1)",
            "error": "#E54D42",
            "error_subtle": "rgba(229, 77, 66, 0.1)",
            "info": "#5E6AD2"
        },
        "overlay": {
            "dark": "rgba(0, 0, 0, 0.5)",
            "light": "rgba(0, 0, 0, 0.05)"
        },
        "accent": {
            "orange": "#E55A2B"
        },
        "scrollbar": {
            "bg": "#F5F5F5",
            "handle": "#D1D1D1",
            "handle_hover": "#A8A8A8"
        },
        "neutral": {
            "bg_app": "#FBFBFC",
            "bg_panel": "#FFFFFF",
            "bg_card": "#F7F7F8",
            "bg_input": "#F7F7F8",
            "bg_hover": "#EFEFEF",
            "bg_sidebar": "#F5F5F5",
            "border_subtle": "#E5E5E5",
            "border_strong": "#D4D4D4",
            "border_sidebar": "#E0E0E0",
            "bg_surface": "#FAFAFA"
        },
        "text": {
            "primary": "#121212",
            "secondary": "#666666",
            "tertiary": "#888888",
            "disabled": "#AAAAAA",
            "on_brand": "#FFFFFF"
        }
    },
    "fonts": {
        "family_base": "System-UI"
    }
}
```

**变更明细**:

| Token | 原值 | 新值 | 原因 |
|-------|------|------|------|
| `neutral.bg_app` | `#FFFFFF` | `#FBFBFC` | 修复死白，微灰更柔和 |
| `neutral.bg_input` | `#FFFFFF` | `#F7F7F8` | 与背景区分 |
| `neutral.bg_surface` | `#FFFFFF` | `#FAFAFA` | 层次感 |
| `semantic.success` | `#27C93F` | `#22A547` | 亮色背景上更易读 |
| `semantic.warning` | `#FFBC2E` | `#E5A500` | 亮色背景上更易读 |
| `semantic.error` | `#FF5F56` | `#E54D42` | 亮色背景上更易读 |
| `text.disabled` | `#999999` | `#AAAAAA` | 更淡，符合 disabled 语义 |
| (新增) `semantic.success_subtle` | - | `rgba(34, 165, 71, 0.1)` | 成功状态背景 |
| (新增) `semantic.warning_subtle` | - | `rgba(229, 165, 0, 0.1)` | 警告状态背景 |
| (新增) `semantic.error_subtle` | - | `rgba(229, 77, 66, 0.1)` | 错误状态背景 |
| (新增) `overlay.dark` | - | `rgba(0, 0, 0, 0.5)` | 深色遮罩 |
| (新增) `overlay.light` | - | `rgba(0, 0, 0, 0.05)` | 浅色遮罩 |
| (新增) `accent.orange` | - | `#E55A2B` | 橙色强调 |
| (新增) `text.tertiary` | - | `#888888` | 三级文本 |

#### Step C1.2: 更新 linear_dark.json

**文件路径**: `config/themes/linear_dark.json`

**完整替换内容**:
```json
{
    "name": "Linear Dark",
    "type": "dark",
    "palette": {
        "brand": {
            "main": "#5E6AD2",
            "hover": "#6F7BF4",
            "pressed": "#4C55AA",
            "subtle": "rgba(94, 106, 210, 0.15)"
        },
        "semantic": {
            "success": "#27C93F",
            "success_subtle": "rgba(39, 201, 63, 0.15)",
            "warning": "#FFBC2E",
            "warning_subtle": "rgba(255, 188, 46, 0.15)",
            "error": "#FF5F56",
            "error_subtle": "rgba(255, 95, 86, 0.15)",
            "info": "#5E6AD2"
        },
        "overlay": {
            "dark": "rgba(0, 0, 0, 0.75)",
            "light": "rgba(255, 255, 255, 0.1)"
        },
        "accent": {
            "orange": "#FF6B35"
        },
        "scrollbar": {
            "bg": "#121212",
            "handle": "#333333",
            "handle_hover": "#555555"
        },
        "neutral": {
            "bg_app": "#121212",
            "bg_panel": "#141414",
            "bg_card": "#181818",
            "bg_input": "#1A1A1A",
            "bg_hover": "#242424",
            "bg_sidebar": "#141414",
            "border_subtle": "#2A2A2A",
            "border_strong": "#333333",
            "border_sidebar": "#2A2A2A",
            "bg_surface": "#181818"
        },
        "text": {
            "primary": "#EEEEEE",
            "secondary": "#888888",
            "tertiary": "#666666",
            "disabled": "#444444",
            "on_brand": "#FFFFFF"
        }
    },
    "fonts": {
        "family_base": "System-UI"
    }
}
```

**变更明细**:

| Token | 原值 | 新值 | 原因 |
|-------|------|------|------|
| `neutral.bg_input` | `#101010` | `#1A1A1A` | 与 bg_app 有区分 |
| `brand.subtle` | `rgba(..., 0.1)` | `rgba(..., 0.15)` | 深色背景上更明显 |
| (新增) `semantic.success_subtle` | - | `rgba(39, 201, 63, 0.15)` | 成功状态背景 |
| (新增) `semantic.warning_subtle` | - | `rgba(255, 188, 46, 0.15)` | 警告状态背景 |
| (新增) `semantic.error_subtle` | - | `rgba(255, 95, 86, 0.15)` | 错误状态背景 |
| (新增) `overlay.dark` | - | `rgba(0, 0, 0, 0.75)` | 深色遮罩 |
| (新增) `overlay.light` | - | `rgba(255, 255, 255, 0.1)` | 浅色遮罩 |
| (新增) `accent.orange` | - | `#FF6B35` | 橙色强调 |
| (新增) `text.tertiary` | - | `#666666` | 三级文本 |

### 6.3 C1 影响分析

| 操作 | 文件 | 类型 |
|------|------|------|
| 修改 | `config/themes/linear_light.json` | ✏️ |
| 修改 | `config/themes/linear_dark.json` | ✏️ |

### 6.4 C1 解决的问题

| 问题 | 解决方式 |
|------|----------|
| Light 主题死白 | bg_app 改为 #FBFBFC |
| 缺少层次感 | bg_input、bg_surface 有区分 |
| 缺少 overlay token | 添加 dark/light overlay |
| 缺少 subtle 语义色 | 添加 success/warning/error_subtle |
| 缺少 accent 色 | 添加 orange |
| 缺少三级文本 | 添加 tertiary |

### 6.5 新增 Token 使用场景

| 新 Token | 使用场景 |
|----------|----------|
| `overlay.dark` | 模态框遮罩、图片预览背景 |
| `overlay.light` | 按钮 hover 效果、拖拽区域 |
| `semantic.success_subtle` | 成功消息背景、完成状态卡片 |
| `semantic.warning_subtle` | 警告消息背景 |
| `semantic.error_subtle` | 错误消息背景 |
| `accent.orange` | 视频卡片边框、特殊强调 |
| `text.tertiary` | 时间戳、次要信息 |

---

## 七、遗漏问题与后续规划

### 7.1 本次未处理的问题

#### 7.1.1 高优先级遗漏

| 问题 | 文件 | 描述 | 建议处理时间 |
|------|------|------|--------------|
| ToastWidget 缺信号 | `toast_manager.py` | Toast 主题切换后不更新 | 下一迭代 |
| VideoImageUploadPanel 缺信号 | `video_image_upload_panel.py` | 上传面板不响应主题 | 下一迭代 |
| ParameterFormWidget 缺信号 | `parameter_form_standard.py` | 参数表单不响应主题 | 下一迭代 |
| SchemaFormRenderer 缺信号 | `schema_form_renderer.py` | Schema 表单不响应主题 | 下一迭代 |
| ImagePreviewDialog 硬编码 | `image_preview_dialog.py` | 完全硬编码颜色 | 下一迭代 |

#### 7.1.2 中优先级遗漏

| 问题 | 文件 | 描述 | 建议处理时间 |
|------|------|------|--------------|
| actions.py 硬编码 | `reference_assets/actions.py` | `#ffb347`, `#bbbbbb` | Phase 2 |
| image_detail_dialog 硬编码 | `image_detail_dialog.py` | 多处硬编码 | Phase 2 |
| integrated_reference_panel 硬编码 | `integrated_reference_panel.py` | overlay 硬编码 | Phase 2 |
| main_window 硬编码 | `main_window.py` | rgba 硬编码 | Phase 2 |
| fallback 颜色不统一 | 多文件 | 不同 fallback 值 | Phase 2 |

#### 7.1.3 低优先级遗漏

| 问题 | 文件 | 描述 | 建议处理时间 |
|------|------|------|--------------|
| video_mode_widget 硬编码 | `video_mode_widget.py` | `#666`, `#999` | Phase 3 |
| image_mode_widget 硬编码 | `image_mode_widget.py` | rgba 硬编码 | Phase 3 |

### 7.2 后续迭代建议

**Phase 2 计划** (建议在 A1+B1+C1 稳定后执行):

| 任务 | 预估时间 |
|------|----------|
| 为 5 个高优先级组件添加主题信号 | 2 小时 |
| 修复 ImagePreviewDialog 硬编码 | 30 分钟 |
| 修复 actions.py 硬编码 | 15 分钟 |
| 统一 fallback 颜色 | 1 小时 |

**Phase 3 计划** (可选):

| 任务 | 预估时间 |
|------|----------|
| 修复 image_detail_dialog 硬编码 | 30 分钟 |
| 修复 integrated_reference_panel 硬编码 | 30 分钟 |
| 修复 main_window 硬编码 | 15 分钟 |
| 修复 mode_widget 硬编码 | 30 分钟 |

### 7.3 为什么本次不处理

1. **范围可控**: A1+B1+C1 已经是较大改动，需要稳定后再继续
2. **风险管理**: 分批修改便于定位问题
3. **验证效果**: 先验证核心修改的效果
4. **用户体验**: 遗漏问题影响较小，不阻塞正常使用

---

## 八、执行顺序与依赖

### 8.1 依赖关系

```
┌─────────────────────────────────────────────────────────────┐
│  C1 调色板更新                                              │
│  - 无前置依赖                                               │
│  - 为 B1 提供正确的颜色值                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  B1 StyleManager 迁移                                       │
│  - 依赖 C1: 需要正确的调色板                                │
│  - 为 A1 无关，但建议先执行                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  A1 废弃组件清理                                            │
│  - 独立任务                                                 │
│  - 最后执行，便于回滚                                       │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 详细执行流程 (v4.0 简化版)

```
┌─────────────────────────────────────────────────────────────┐
│  Step 0: Git 备份 (必须)                                    │
│  git add -A                                                 │
│  git commit -m "backup: 准备执行主题系统重构 (A1+B1+C1)"    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  C1.1: 更新 linear_light.json                               │
│  C1.2: 更新 linear_dark.json                                │
│                                                             │
│  [验证点] python main.py 启动，检查颜色是否正确加载         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  B1.1: 修改 creation_components.py                          │
│        - 删除 StyleManager 导入和实例化                     │
│        - 添加主题信号连接                                   │
│        - 替换 8 处颜色获取                                  │
│        - 添加主题响应方法                                   │
│                                                             │
│  [验证点] 检查创作面板是否正常显示                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  B1.2: 修改 settings_page.py                                │
│        - 删除无用的 StyleManager 导入                       │
│                                                             │
│  [验证点] 检查设置页面是否正常                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  B1.3: 修改 style_system.py (v4.0 简化)                     │
│        - 删除 _style_manager 死代码 (3 处)                  │
│        - 删除 set_style_manager 方法                        │
│        (不再需要添加 _build_global_stylesheet)              │
│                                                             │
│  [验证点] 确认无导入错误                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  B1.4: 清理 ui_utils.py (原 B1.5)                           │
│        - 删除 StyleManager 类 (~216 行)                     │
│        - 删除 build_global_stylesheet 方法 (~48 行)         │
│                                                             │
│  [验证点] python main.py 启动测试                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  A1.1: 删除废弃卡片组件 (v4.0 简化)                         │
│        - placeholder_card.py                                │
│        - video_card.py                                      │
│        - image_card.py                                      │
│  A1.2: 更新 cards/__init__.py                               │
│        (不再需要创建 detail_handlers.py)                    │
│                                                             │
│  [验证点] 无导入错误                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  A1.3: 删除 waterfall_widget.py                             │
│  A1.4: 更新 layouts/__init__.py (如需要)                    │
│                                                             │
│  [验证点] 无导入错误                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  A1.5: 删除 qt_app.py (v4.0 新增)                           │
│        - 删除或移动到 archive/legacy/qt_app_pyqt5.py        │
│                                                             │
│  [验证点] 无 PyQt5 残留，python main.py 正常                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  最终验证                                                   │
│  - python main.py 启动测试                                  │
│  - 深色主题测试                                             │
│  - 浅色主题测试                                             │
│  - 主题切换测试                                             │
│  - 组件样式测试                                             │
│  - 回归测试                                                 │
└─────────────────────────────────────────────────────────────┘
```

### 8.3 文件修改汇总 (v4.0 更新)

| 文件 | C1 | B1 | A1 | 操作类型 | 变化描述 |
|------|----|----|-----|----------|----------|
| `config/themes/linear_light.json` | ✏️ | - | - | 修改 | 修复死白，添加新 token |
| `config/themes/linear_dark.json` | ✏️ | - | - | 修改 | 添加新 token |
| `utils/ui_utils.py` | - | ✏️ | - | 修改 | 删除 StyleManager 类 |
| `utils/style_system.py` | - | ✏️ | - | 修改 | 删除死代码依赖 |
| `components/creation_components.py` | - | ✏️ | - | 修改 | 替换颜色获取，添加主题响应 |
| `components/settings_page.py` | - | ✏️ | - | 修改 | 删除无用导入 |
| `components/cards/__init__.py` | - | - | ✏️ | 修改 | 清空导出 |
| `components/cards/placeholder_card.py` | - | - | 🗑️ | 删除 | 废弃组件 |
| `components/cards/video_card.py` | - | - | 🗑️ | 删除 | 废弃组件 |
| `components/cards/image_card.py` | - | - | 🗑️ | 删除 | 废弃组件 |
| `components/layouts/waterfall_widget.py` | - | - | 🗑️ | 删除 | 废弃组件 |
| `components/layouts/__init__.py` | - | - | ✏️ | 可能修改 | 清理导出 |
| **`qt_app.py`** | - | - | **🗑️** | **删除** | **PyQt5 旧入口 (v4.0 新增)** |

**v4.0 统计**:
- 新建: **0** 个文件 (原 detail_handlers.py 不再需要)
- 修改: **6** 个文件
- 删除: **5** 个文件 (原 4 + qt_app.py)
- 净变化: 约 **-2891** 行代码
  - 废弃 Card 组件: -1217 行
  - WaterfallWidget: -510 行
  - qt_app.py: -900 行
  - StyleManager: -264 行

---

## 九、风险评估与回滚

### 9.1 风险矩阵 (v4.0 更新)

| 风险 | 可能性 | 影响 | 严重程度 | 缓解措施 |
|------|--------|------|----------|----------|
| 应用无法启动 | 低 | 高 | 🔴 严重 | Git 备份，分步执行，每步验证 |
| 颜色显示异常 | 中 | 中 | 🟡 中等 | 颜色映射表已准备，可快速调整 |
| 主题切换失效 | 低 | 中 | 🟡 中等 | 验证步骤包含主题切换测试 |
| 删除文件导致导入错误 | **极低** | 高 | 🟡 中等 | **v4.0: 已验证新架构不依赖废弃组件** |
| ~~废弃组件仍有使用~~ | ~~极低~~ | ~~中~~ | ~~🟡~~ | **v4.0: 已确认只被废弃的 qt_app.py 使用** |
| Slider 样式异常 | 低 | 低 | 🟢 轻微 | 有独立更新方法，易于调试 |
| **删除 qt_app.py 后脚本失效** | **中** | **低** | **🟢 轻微** | **更新 scripts/ 中的启动脚本指向 main.py** |

### 9.2 回滚方案

#### 完全回滚

如果出现严重问题：

```bash
git reset --hard HEAD~1
```

#### 部分回滚

如果特定文件有问题：

```bash
# 回滚单个文件
git checkout HEAD~1 -- <file_path>

# 示例
git checkout HEAD~1 -- components/creation_components.py
git checkout HEAD~1 -- utils/style_system.py
```

#### 分阶段回滚 (v4.0 简化)

如果需要回滚特定阶段：

```bash
# 回滚 A1（恢复删除的文件）
git checkout HEAD~1 -- components/cards/placeholder_card.py
git checkout HEAD~1 -- components/cards/video_card.py
git checkout HEAD~1 -- components/cards/image_card.py
git checkout HEAD~1 -- components/layouts/waterfall_widget.py
git checkout HEAD~1 -- qt_app.py  # v4.0: 包括旧入口
# 同时恢复 __init__.py
```

### 9.3 验证检查点 (v4.0 更新)

| 阶段 | 检查点 | 验证方法 |
|------|--------|----------|
| C1 后 | 调色板加载 | `python main.py` 启动，观察颜色 |
| B1.1 后 | creation_components | 打开创作面板，检查 slider |
| B1.3 后 | style_system | 无导入错误 |
| B1.4 后 | ui_utils | `python main.py` 正常启动 |
| A1.2 后 | cards 目录 | 无导入错误 |
| A1.4 后 | layouts 目录 | 无导入错误 |
| **A1.5 后** | **qt_app.py 删除** | **无 PyQt5 残留，`python main.py` 正常** |
| 全部完成 | 主题切换 | 在设置页切换主题 |

---

## 十、审批检查清单 (v4.0 更新)

### 10.1 C1 调色板更新

- [ ] C1.1: 同意更新 `linear_light.json`
  - [ ] 理解 bg_app 从 #FFFFFF 改为 #FBFBFC 的原因（修复死白）
  - [ ] 理解语义色调整的原因（亮色背景可读性）
  - [ ] 理解新增 token 的用途

- [ ] C1.2: 同意更新 `linear_dark.json`
  - [ ] 理解 bg_input 从 #101010 改为 #1A1A1A 的原因（与 bg_app 区分）
  - [ ] 理解新增 token 与 light 主题对应

### 10.2 B1 StyleManager 迁移 (v4.0 简化)

- [ ] B1.0: 同意创建 Git 备份

- [ ] B1.1: 同意修改 `creation_components.py`
  - [ ] 理解删除 StyleManager 的原因（消除双调色板）
  - [ ] 理解添加主题信号的原因（支持主题切换）
  - [ ] 理解颜色映射（从蓝色变为紫色是预期行为）

- [ ] B1.2: 同意修改 `settings_page.py`
  - [ ] 理解删除无用导入

- [ ] B1.3: 同意修改 `style_system.py` (v4.0 简化)
  - [ ] 理解删除死代码 `_style_manager` 的原因
  - [ ] ~~理解 _build_global_stylesheet 的作用~~ (v4.0: 已由 MainWindow 处理)

- [ ] ~~B1.4: 同意修改 `qt_app.py`~~ (v4.0: 改为在 A1 中删除)

- [ ] B1.4: 同意删除 StyleManager 类 (原 B1.5)
  - [ ] 理解这会永久移除约 264 行代码

### 10.3 A1 废弃组件清理 (v4.0 简化)

- [ ] ~~A1.1: 同意创建 `detail_handlers.py`~~ (v4.0: 不再需要)

- [ ] A1.1: 同意删除 `placeholder_card.py`
- [ ] A1.2: 同意删除 `video_card.py`
- [ ] A1.3: 同意删除 `image_card.py`
- [ ] A1.4: 同意删除 `waterfall_widget.py`

- [ ] **A1.5: 同意删除 `qt_app.py`** (v4.0 新增)
  - [ ] 理解 qt_app.py 是废弃的 PyQt5 旧入口
  - [ ] 理解真正的主入口是 main.py (PySide6)
  - [ ] 理解这会永久移除约 900 行 PyQt5 代码

- [ ] A1.6: 同意更新 `cards/__init__.py`
- [ ] A1.7: 同意更新 `layouts/__init__.py`（如需要）

**v4.0 删除代码统计**:
- 废弃 Card 组件: ~1217 行
- WaterfallWidget: ~510 行
- qt_app.py: ~900 行
- StyleManager: ~264 行
- **总计: ~2891 行**

### 10.4 遗漏问题确认

- [ ] 确认仅执行 A1+B1+C1
- [ ] 理解以下问题留待后续处理:
  - [ ] ToastWidget 缺信号连接
  - [ ] VideoImageUploadPanel 缺信号连接
  - [ ] ParameterFormWidget 缺信号连接
  - [ ] SchemaFormRenderer 缺信号连接
  - [ ] ImagePreviewDialog 硬编码
  - [ ] 其他中低优先级问题

### 10.5 最终确认

- [ ] 同意执行顺序: C1 → B1 → A1
- [ ] 理解 main.py 是真正的主入口 (v4.0 关键点)
- [ ] 理解回滚方案
- [ ] 理解验证检查点

---

## 附录 (v4.0 更新)

### A. 参考文档

- `.claude/THEME_AUDIT_PLAN.md` - 原始审查报告（已合并到本文档）
- **v4.0 审核反馈** - PySide6/Qt 架构师审核发现

### B. 相关代码位置速查

| 内容 | 文件 | 行号 | v4.0 状态 |
|------|------|------|----------|
| StyleManager 类定义 | `utils/ui_utils.py` | 137-353 | 待删除 |
| build_global_stylesheet | `utils/ui_utils.py` | 360-408 | 待删除 |
| UnifiedStyleSystem 类 | `utils/style_system.py` | 全文件 | 清理死代码 |
| ThemeEngine 类 | `utils/theme_engine.py` | 全文件 | 保留 |
| ~~qt_app 全局样式~~ | ~~`qt_app.py`~~ | ~~818-829~~ | **废弃，待删除** |
| creation_components StyleManager 使用 | `components/creation_components.py` | 56, 345-363, 812, 1412 | 迁移 |
| **MainWindow 主题样式 (v4.0)** | **`components/main_window.py`** | **41, 306-380** | **保留** |
| **main.py 入口 (v4.0)** | **`main.py`** | **1-63** | **真正的主入口** |

### C. 颜色对照表完整版

**Dark 主题**:

| Token 路径 | 原值 | 新值 | 用途 |
|------------|------|------|------|
| palette.brand.main | #5E6AD2 | #5E6AD2 | 主色调 |
| palette.brand.hover | #6F7BF4 | #6F7BF4 | hover 状态 |
| palette.brand.pressed | #4C55AA | #4C55AA | pressed 状态 |
| palette.brand.subtle | rgba(94,106,210,0.1) | rgba(94,106,210,0.15) | 微弱背景 |
| palette.semantic.success | #27C93F | #27C93F | 成功 |
| palette.semantic.warning | #FFBC2E | #FFBC2E | 警告 |
| palette.semantic.error | #FF5F56 | #FF5F56 | 错误 |
| palette.semantic.info | #5E6AD2 | #5E6AD2 | 信息 |
| palette.neutral.bg_app | #121212 | #121212 | 应用背景 |
| palette.neutral.bg_panel | #141414 | #141414 | 面板背景 |
| palette.neutral.bg_card | #181818 | #181818 | 卡片背景 |
| palette.neutral.bg_input | #101010 | #1A1A1A | 输入框背景 |
| palette.neutral.bg_hover | #242424 | #242424 | hover 背景 |
| palette.neutral.border_subtle | #2A2A2A | #2A2A2A | 细边框 |
| palette.neutral.border_strong | #333333 | #333333 | 粗边框 |
| palette.text.primary | #EEEEEE | #EEEEEE | 主文本 |
| palette.text.secondary | #888888 | #888888 | 次文本 |
| palette.text.disabled | #444444 | #444444 | 禁用文本 |
| palette.text.on_brand | #FFFFFF | #FFFFFF | 品牌色上的文本 |
| (新增) palette.semantic.success_subtle | - | rgba(39,201,63,0.15) | 成功背景 |
| (新增) palette.semantic.warning_subtle | - | rgba(255,188,46,0.15) | 警告背景 |
| (新增) palette.semantic.error_subtle | - | rgba(255,95,86,0.15) | 错误背景 |
| (新增) palette.overlay.dark | - | rgba(0,0,0,0.75) | 深遮罩 |
| (新增) palette.overlay.light | - | rgba(255,255,255,0.1) | 浅遮罩 |
| (新增) palette.accent.orange | - | #FF6B35 | 橙色强调 |
| (新增) palette.text.tertiary | - | #666666 | 三级文本 |

**Light 主题**:

| Token 路径 | 原值 | 新值 | 用途 |
|------------|------|------|------|
| palette.brand.main | #5E6AD2 | #5E6AD2 | 主色调 |
| palette.brand.hover | #4B56B2 | #4B56B2 | hover 状态 |
| palette.brand.pressed | #3A4391 | #3A4391 | pressed 状态 |
| palette.brand.subtle | rgba(94,106,210,0.08) | rgba(94,106,210,0.08) | 微弱背景 |
| palette.semantic.success | #27C93F | #22A547 | 成功 |
| palette.semantic.warning | #FFBC2E | #E5A500 | 警告 |
| palette.semantic.error | #FF5F56 | #E54D42 | 错误 |
| palette.semantic.info | #5E6AD2 | #5E6AD2 | 信息 |
| palette.neutral.bg_app | #FFFFFF | #FBFBFC | 应用背景 |
| palette.neutral.bg_panel | #FFFFFF | #FFFFFF | 面板背景 |
| palette.neutral.bg_card | #F7F7F8 | #F7F7F8 | 卡片背景 |
| palette.neutral.bg_input | #FFFFFF | #F7F7F8 | 输入框背景 |
| palette.neutral.bg_hover | #F0F0F0 | #EFEFEF | hover 背景 |
| palette.neutral.border_subtle | #E5E5E5 | #E5E5E5 | 细边框 |
| palette.neutral.border_strong | #D4D4D4 | #D4D4D4 | 粗边框 |
| palette.neutral.bg_surface | #FFFFFF | #FAFAFA | 表面背景 |
| palette.text.primary | #121212 | #121212 | 主文本 |
| palette.text.secondary | #666666 | #666666 | 次文本 |
| palette.text.disabled | #999999 | #AAAAAA | 禁用文本 |
| palette.text.on_brand | #FFFFFF | #FFFFFF | 品牌色上的文本 |
| (新增) palette.semantic.success_subtle | - | rgba(34,165,71,0.1) | 成功背景 |
| (新增) palette.semantic.warning_subtle | - | rgba(229,165,0,0.1) | 警告背景 |
| (新增) palette.semantic.error_subtle | - | rgba(229,77,66,0.1) | 错误背景 |
| (新增) palette.overlay.dark | - | rgba(0,0,0,0.5) | 深遮罩 |
| (新增) palette.overlay.light | - | rgba(0,0,0,0.05) | 浅遮罩 |
| (新增) palette.accent.orange | - | #E55A2B | 橙色强调 |
| (新增) palette.text.tertiary | - | #888888 | 三级文本 |

---

**全部确认后，回复"批准执行 A1+B1+C1 v4.0"开始执行。**

如需调整任何步骤，请指出具体项目。

---

*文档版本: v4.0 (审核修订版)*
*最后更新: 2025-12-18*
*创建者: Claude Code*
*审核者: PySide6/Qt 架构师*
*审批状态: ✅ 已批准*

---

## 审批记录

### 二次审核结论 (v4.0)

**结果**: ✅ **批准执行 v4.0**

### 核心验证发现

1. **主入口确认** ✅
   - `main.py` (PySide6) 是唯一活跃的主入口
   - `qt_app.py` (PyQt5) 确实是废弃代码
   - 删除 qt_app.py 是最安全、最彻底的解决方案

2. **简化方案评估** ✅
   - `detail_handlers.py`: 不需要（新架构直接实例化）
   - `_build_global_stylesheet`: 不需要（MainWindow 已处理）

3. **风险评估** ✅
   - ImageCardDelegate 完全独立，不依赖废弃组件
   - 执行顺序安全，中间步骤也不会崩溃

### 批准理由

1. **第一性原理**: 通过删除废弃代码解决问题，是处理技术债务的最佳实践
2. **架构一致性**: 强制全项目统一使用 PySide6，消除 Segfault 风险
3. **极简主义**: 去除过度工程，直接复用现有 MainWindow 逻辑

### 补充检查

**启动脚本检查**: 无引用 `qt_app.py` 的脚本 ✅

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v3.0 | 2025-12-18 | 初始详细版本 |
| v4.0 | 2025-12-18 | 基于架构师审核修订：确认 main.py 是主入口，qt_app.py 废弃，简化 A1/B1 计划 |
