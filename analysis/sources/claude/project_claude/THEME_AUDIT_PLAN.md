# 主题系统全面审查与修复规划

> 版本: v1.0
> 创建日期: 2025-12-18
> 状态: 待审批

---

## 目录

1. [问题总览](#一-问题总览)
2. [硬编码颜色详细清单](#二-硬编码颜色详细清单)
3. [信号连接问题](#三-信号连接问题)
4. [Linear 设计一致性分析](#四-linear-设计一致性分析)
5. [调色板优化建议](#五-调色板优化建议)
6. [修复执行计划](#六-修复执行计划)
7. [决策点](#七-决策点)

---

## 一、问题总览

### 统计数据

| 类别 | 数量 | 严重程度 |
|------|------|----------|
| 硬编码颜色（严重） | 15 处 | 🔴 高 |
| 硬编码颜色（中等） | 12 处 | 🟡 中 |
| 硬编码颜色（轻微） | 8 处 | 🟢 低 |
| 缺少信号连接 | 10 个组件 | 🟡 中 |
| 废弃组件未清理 | 3 个 | 🟢 低 |
| 调色板设计问题 | 5 处 | 🟡 中 |

### 问题分布图

```
components/
├── cards/
│   ├── placeholder_card.py    [🔴 严重] 完全硬编码，废弃组件
│   ├── video_card.py          [🔴 严重] 完全硬编码，废弃组件
│   └── image_card.py          [🔴 严重] 完全硬编码，废弃组件
├── widgets/
│   ├── image_preview_dialog.py [🔴 严重] 完全硬编码
│   ├── toast_manager.py        [🟡 中等] 缺信号连接
│   ├── video_image_upload_panel.py [🟡 中等] 缺信号连接
│   └── integrated_reference_panel.py [🟡 中等] 部分硬编码
├── dialogs/
│   └── image_detail_dialog.py  [🟡 中等] 部分硬编码
├── modes/
│   ├── image_mode_widget.py    [🟢 轻微] fallback不一致
│   └── video_mode_widget.py    [🟢 轻微] fallback不一致
├── forms/
│   ├── parameter_form_standard.py [🟡 中等] 缺信号连接
│   └── schema_form_renderer.py    [🟡 中等] 缺信号连接
└── reference_assets/
    └── actions.py              [🟡 中等] 标签硬编码

utils/
├── ui_utils.py                 [🔴 严重] 独立调色板系统
└── style_system.py             [🟢 轻微] 滚动条fallback
```

---

## 二、硬编码颜色详细清单

### 2.1 🔴 严重问题（完全硬编码，无主题响应）

#### A. placeholder_card.py（已废弃但仍在代码库）

| 行号 | 硬编码值 | 应替换为 |
|------|----------|----------|
| 45 | `#242424` | `palette.neutral.bg_card` |
| 46 | `#555555` | `palette.neutral.border_strong` |
| 58 | `#d0d0d0` | `palette.text.secondary` |
| 65 | `#999999` | `palette.text.disabled` |
| 70 | `#666666` | `palette.text.disabled` |
| 92 | `#d0d0d0` | `palette.text.secondary` |
| 95 | `#4CAF50` | `palette.semantic.success` |
| 98 | `#2196F3` | `palette.semantic.info` |
| 103 | `#f44336` | `palette.semantic.error` |

**原因**: 该组件注释标记为 DEPRECATED，但仍存在于代码库，可能被旧代码引用。

**建议**:
- 方案A: 彻底删除该文件（如果确认无引用）
- 方案B: 添加主题响应以保持一致性

---

#### B. video_card.py（已废弃但仍在代码库）

| 行号 | 硬编码值 | 应替换为 |
|------|----------|----------|
| 85-86 | `#1a1a1a`, `#3a3a5e` | `palette.neutral.bg_card`, `palette.neutral.border_subtle` |
| 91 | `#FF6B35` | `palette.brand.main` 或新增 `palette.accent.orange` |
| 107-109 | `#ccc` | `palette.neutral.border_subtle` |
| 124-125 | `rgba(0,120,212,210)`, `#ffffff` | `palette.brand.main + alpha`, `palette.text.on_brand` |
| 142 | `#FF6B35`, `#2a2a2a` | `palette.semantic.warning`, `palette.neutral.bg_card` |
| 156-204 | `#ffffff`, `#cccccc` | `palette.text.primary`, `palette.text.secondary` |
| 236-237 | `rgba(0,0,0,0.75)`, `#ffffff` | 新增 `palette.overlay.dark`, `palette.text.on_brand` |
| 283, 319 | `#ccc`, `#888`, `#2a2a2a` | 对应 token |
| 490-501 | 菜单样式全部硬编码 | 应使用 `unified_style_system.get_widget_style('QMenu')` |

**原因**: 该组件已被 VideoCardDelegate 替代，但 `set_video_detail_handler` 函数仍在使用。

**建议**:
- 保留 handler 函数，删除 VideoCard 类
- 或添加完整主题响应

---

#### C. image_card.py（已废弃但仍在代码库）

与 video_card.py 结构相同，问题相同。

| 行号 | 硬编码值 | 应替换为 |
|------|----------|----------|
| 117-123 | `#1a1a1a`, `#3a3a5e`, `#4CAF50` | 对应 token |
| 138 | `#ccc` | `palette.neutral.border_subtle` |
| 153-154 | `rgba(255,140,0,210)`, `#ffffff` | 新增 `palette.accent.orange`, `palette.text.on_brand` |
| 176-205 | `#ffffff`, `#cccccc` | `palette.text.primary`, `palette.text.secondary` |
| 233-234 | `rgba(0,0,0,0.72)`, `#ffffff` | `palette.overlay.dark`, `palette.text.on_brand` |
| 483-494 | 菜单样式 | 统一菜单样式 |

---

#### D. image_preview_dialog.py（活跃组件）

| 行号 | 硬编码值 | 应替换为 |
|------|----------|----------|
| 35 | `rgba(0,0,0,0.7)` | `palette.overlay.dark` |
| 45-51 | `rgba(255,255,255,0.1/0.3)` | 新增 `palette.overlay.light_subtle/light_hover` |
| 70-76 | 同上 | 同上 |

**原因**: 这是活跃组件，用于图片预览，但完全硬编码。

**建议**: 必须修复，添加主题响应。

---

#### E. utils/ui_utils.py（遗留系统）

```python
# 行 145-178: 独立的调色板系统
DARK_COLORS = {
    'primary': '#0078d4',      # 与主题 #5E6AD2 不一致！
    'primary_hover': '#106ebe',
    'primary_pressed': '#005a9e',
    'background': '#1e1e1e',   # 与主题 #121212 不一致！
    'surface': '#2d2d2d',      # 与主题 #181818 不一致！
    ...
}
```

| 问题 | 说明 |
|------|------|
| primary 颜色冲突 | ui_utils 用 `#0078d4`（蓝色），主题用 `#5E6AD2`（Linear 紫色）|
| background 不一致 | ui_utils 用 `#1e1e1e`，主题用 `#121212` |
| 独立系统 | StyleManager 类与 UnifiedStyleSystem 完全独立，切换主题时不同步 |

**原因**: 历史遗留代码，早期开发时创建，后来引入了统一主题系统但未清理。

**建议**:
- 方案A: 删除 StyleManager 类，所有引用迁移到 unified_style_system
- 方案B: 重构 StyleManager 作为 unified_style_system 的代理

---

### 2.2 🟡 中等问题（部分硬编码或 fallback 不一致）

#### A. main_window.py

| 行号 | 问题 | 建议 |
|------|------|------|
| 350, 367 | `rgba(128,128,128,0.1)` 悬停背景 | 新增 `palette.neutral.bg_hover_subtle` |
| 457 | `rgba(0,0,0,0.8)` 遮罩 | 使用 `palette.overlay.dark` |

#### B. video_mode_widget.py

| 行号 | 问题 | 建议 |
|------|------|------|
| 2270-2271 | `#666`, `#999` 禁用状态 | 使用 `palette.text.disabled` |
| 2336 | `#999` | 同上 |

#### C. image_mode_widget.py

| 行号 | 问题 | 建议 |
|------|------|------|
| 1709 | `rgba(39,201,63,0.2)` 成功背景 | 新增 `palette.semantic.success_subtle` |

#### D. image_detail_dialog.py

| 行号 | 硬编码值 | 建议 |
|------|----------|------|
| 131 | `#bbbbbb` | `palette.text.secondary` |
| 177 | `#cccccc` | `palette.text.secondary` |
| 527-538 | `#2a2a3e`, `#555`, `#4CAF50` | 对应 token |
| 716 | `#888` | `palette.text.disabled` |

#### E. integrated_reference_panel.py

| 行号 | 硬编码值 | 建议 |
|------|----------|------|
| 82 | `#ffffff` | `palette.text.on_brand` |
| 411-419 | `rgba(255,255,255,...)` | 新增 overlay tokens |

#### F. reference_assets/actions.py

| 行号 | 硬编码值 | 建议 |
|------|----------|------|
| 72 | `#ffb347` | `palette.semantic.warning` 或 accent |
| 84, 86 | `#bbbbbb` | `palette.text.secondary` |

---

### 2.3 🟢 轻微问题（Fallback 颜色不一致）

#### Fallback 颜色对照表

| 文件 | Token | 当前 Fallback | 应统一为 |
|------|-------|---------------|----------|
| main_window.py:314 | `bg_app` | `#121212` | ✅ 正确 |
| main_window.py:337 | `text.disabled` | `#666` | ❌ 应为 `#444444` |
| video_mode_widget.py:124 | `bg_app` | `#121212` | ✅ 正确 |
| video_mode_widget.py:128 | `bg_input` | `#2d2d2d` | ❌ 应为 `#101010` |
| image_mode_widget.py:173 | `bg_input` | `#2d2d2d` | ❌ 应为 `#101010` |
| image_mode_widget.py:229 | `text.secondary` | `#888888` | ✅ 正确 |

**建议**: 创建统一的 fallback 常量模块，避免分散定义。

---

## 三、信号连接问题

### 3.1 已正确连接的组件（13个）

| 组件 | 连接位置 |
|------|----------|
| MainWindow | main_window.py:307 |
| ImageModeWidget | image_mode_widget.py:143 |
| VideoModeWidget | video_mode_widget.py:116 |
| SettingsPage | settings_page.py:48,127 |
| ImageDetailDialog | image_detail_dialog.py:47 |
| VideoDetailDialog | video_detail_dialog.py:58 |
| ImageHistoryView | image_history_view.py:66 |
| VideoHistoryView | video_history_view.py:62 |
| ImageCardDelegate | image_card_delegate.py:35 |
| VideoCardDelegate | video_card_delegate.py:38 |
| ReferenceGalleryWidget | gallery.py:174 |
| ReferenceAssetsPanel | reference_assets_panel.py:42,219 |
| IntegratedReferencePanel | integrated_reference_panel.py:68,390 |

### 3.2 缺少信号连接的组件（10个）

| 组件 | 文件 | 影响描述 | 优先级 |
|------|------|----------|--------|
| **ToastWidget** | toast_manager.py | Toast 在主题切换后颜色不更新，需关闭重开 | 🟡 中 |
| **VideoImageUploadPanel** | video_image_upload_panel.py | 视频模式的图片上传面板不响应主题 | 🔴 高 |
| **ParameterFormWidget** | parameter_form_standard.py | 参数表单样式不更新 | 🔴 高 |
| **SchemaFormRenderer** | schema_form_renderer.py | Schema 表单样式不更新 | 🔴 高 |
| **ImagePreviewDialog** | image_preview_dialog.py | 图片预览对话框硬编码 | 🟡 中 |
| **ReferenceImagesWidget** | reference_images_simple.py | 简化版参考图组件 | 🟢 低 |
| **PlaceholderCard** | placeholder_card.py | 废弃组件 | 🟢 低 |
| **VideoCard** | video_card.py | 废弃组件 | 🟢 低 |
| **ImageCard** | image_card.py | 废弃组件 | 🟢 低 |
| **actions.py Dialog** | reference_assets/actions.py | 参考图预览对话框 | 🟡 中 |

### 3.3 信号连接修复模板

```python
# 标准模板 - 添加到组件的 __init__ 方法
from utils.style_system import unified_style_system

class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 1. 连接信号
        unified_style_system.styleChanged.connect(self._on_theme_changed)

        # 2. 初始化 UI
        self._init_ui()

        # 3. 应用初始主题
        self._apply_theme()

    def _on_theme_changed(self):
        """响应主题变更"""
        self._apply_theme()

    def _apply_theme(self):
        """应用当前主题样式"""
        colors = unified_style_system.get_colors()

        # 使用 token 获取颜色
        bg_color = colors.get('palette.neutral.bg_card')
        text_color = colors.get('palette.text.primary')

        # 应用样式
        self.setStyleSheet(f"""
            MyWidget {{
                background-color: {bg_color};
                color: {text_color};
            }}
        """)
```

---

## 四、Linear 设计一致性分析

### 4.1 什么是 Linear 设计风格？

Linear 是一款项目管理工具，以其精致、现代的 UI 设计著称。核心特点：

| 特性 | 描述 |
|------|------|
| **柔和背景** | 避免纯白/纯黑，使用微调的灰度 |
| **微妙层次** | 通过细微的色差创建视觉层次 |
| **低对比边框** | 边框与背景色差小，不刺眼 |
| **品牌紫色** | 主色调为紫色 (#5E6AD2) |
| **一致的圆角** | 6-8px 的圆角系统 |
| **精致阴影** | 淡阴影，不突兀 |

### 4.2 当前调色板问题分析

#### 🔴 Light 主题的"死白"问题

**当前配置 (linear_light.json)**:
```json
"neutral": {
    "bg_app": "#FFFFFF",      // ❌ 纯白，太刺眼
    "bg_panel": "#FFFFFF",    // ❌ 纯白，无层次
    "bg_card": "#F7F7F8",     // ✅ 微灰，正确
    "bg_input": "#FFFFFF",    // ❌ 纯白
    "bg_surface": "#FFFFFF"   // ❌ 纯白
}
```

**Linear 实际使用的颜色**:
```json
"neutral": {
    "bg_app": "#FBFBFC",      // 极浅灰，不刺眼
    "bg_panel": "#FFFFFF",    // 卡片可用纯白凸显
    "bg_card": "#F7F7F8",     // 微灰卡片
    "bg_input": "#F7F7F8",    // 输入框用微灰
    "bg_surface": "#FAFAFA"   // 表面用极浅灰
}
```

#### 🟡 Dark 主题的层次问题

**当前配置 (linear_dark.json)**:
```json
"neutral": {
    "bg_app": "#121212",      // ✅ 正确
    "bg_panel": "#141414",    // ✅ 微浅，有层次
    "bg_card": "#181818",     // ✅ 再浅一点
    "bg_input": "#101010",    // ⚠️ 太深，与 bg_app 对比不明显
    "bg_hover": "#242424",    // ✅ 正确
    "bg_surface": "#181818"   // ✅ 正确
}
```

**建议调整**:
```json
"bg_input": "#1A1A1A",        // 调浅一点，与 bg_app 有区分
```

#### 🟡 语义色的亮度问题

**当前语义色（两个主题共用）**:
```json
"semantic": {
    "success": "#27C93F",     // ✅ 正确，Linear 风格绿色
    "warning": "#FFBC2E",     // ⚠️ 在亮色背景上可能太亮
    "error": "#FF5F56",       // ✅ 正确
    "info": "#5E6AD2"         // ✅ 与 brand 一致
}
```

**建议**: Light 主题的语义色可以适当调暗，提高可读性。

#### 🔴 缺少的 Token

当前调色板缺少以下常用 Token：

| 缺失 Token | 用途 | 建议值 (Dark) | 建议值 (Light) |
|------------|------|---------------|----------------|
| `overlay.dark` | 遮罩层 | `rgba(0,0,0,0.75)` | `rgba(0,0,0,0.5)` |
| `overlay.light` | 浅色遮罩 | `rgba(255,255,255,0.1)` | `rgba(0,0,0,0.05)` |
| `semantic.success_subtle` | 成功背景 | `rgba(39,201,63,0.15)` | `rgba(39,201,63,0.1)` |
| `semantic.warning_subtle` | 警告背景 | `rgba(255,188,46,0.15)` | `rgba(255,188,46,0.1)` |
| `semantic.error_subtle` | 错误背景 | `rgba(255,95,86,0.15)` | `rgba(255,95,86,0.1)` |
| `accent.orange` | 橙色强调 | `#FF6B35` | `#E55A2B` |
| `text.tertiary` | 三级文本 | `#555555` | `#888888` |

---

## 五、调色板优化建议

### 5.1 Light 主题修复方案

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
    }
}
```

### 5.2 Dark 主题优化方案

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
    }
}
```

---

## 六、修复执行计划

### Phase 0: 调色板优化（建议优先执行）

| 任务 | 文件 | 工作量 | 说明 |
|------|------|--------|------|
| 0.1 更新 Light 主题调色板 | linear_light.json | 5分钟 | 修复死白问题 |
| 0.2 更新 Dark 主题调色板 | linear_dark.json | 5分钟 | 添加新 token |
| 0.3 验证主题切换 | 手动测试 | 10分钟 | 确保不破坏现有功能 |

**理由**: 调色板是基础设施，先修复可以为后续组件修复提供正确的颜色值。

---

### Phase 1: 高优先级组件修复

| 任务 | 文件 | 工作量 | 说明 |
|------|------|--------|------|
| 1.1 ToastWidget 添加主题响应 | toast_manager.py | 15分钟 | 全局通知组件 |
| 1.2 VideoImageUploadPanel 添加主题响应 | video_image_upload_panel.py | 20分钟 | 视频模式核心组件 |
| 1.3 ParameterFormWidget 添加主题响应 | parameter_form_standard.py | 20分钟 | 参数表单 |
| 1.4 SchemaFormRenderer 添加主题响应 | schema_form_renderer.py | 20分钟 | Schema 表单 |
| 1.5 ImagePreviewDialog 添加主题响应 | image_preview_dialog.py | 15分钟 | 图片预览 |

**理由**: 这些是活跃组件，直接影响用户体验。

---

### Phase 2: 中优先级修复

| 任务 | 文件 | 工作量 | 说明 |
|------|------|--------|------|
| 2.1 修复 actions.py 硬编码 | reference_assets/actions.py | 10分钟 | 参考图预览对话框 |
| 2.2 修复 image_detail_dialog.py 硬编码 | image_detail_dialog.py | 15分钟 | 图片详情对话框 |
| 2.3 修复 integrated_reference_panel.py 硬编码 | integrated_reference_panel.py | 15分钟 | 参考图面板 |
| 2.4 统一 fallback 颜色 | 多文件 | 30分钟 | 创建常量模块 |
| 2.5 修复 main_window.py 硬编码 | main_window.py | 10分钟 | 遮罩和悬停色 |

**理由**: 这些问题影响主题一致性，但不是关键路径。

---

### Phase 3: 低优先级清理

| 任务 | 文件 | 工作量 | 决策 |
|------|------|--------|------|
| 3.1 处理废弃卡片组件 | placeholder_card.py, video_card.py, image_card.py | 取决于决策 | 见决策点 A |
| 3.2 处理 StyleManager | utils/ui_utils.py | 取决于决策 | 见决策点 B |
| 3.3 清理 video_mode_widget 硬编码 | video_mode_widget.py | 15分钟 | - |
| 3.4 清理 image_mode_widget 硬编码 | image_mode_widget.py | 15分钟 | - |

**理由**: 这些是废弃代码或边缘情况，优先级最低。

---

## 七、决策点

### 决策 A: 废弃卡片组件处理

**背景**: `PlaceholderCard`、`VideoCard`、`ImageCard` 已标记为 DEPRECATED，被 Delegate 替代。

| 选项 | 操作 | 优点 | 缺点 |
|------|------|------|------|
| A1. 彻底删除 | 删除三个文件 | 清理代码库 | 可能有未知引用 |
| A2. 添加主题响应 | 修复硬编码 | 保持一致性 | 维护废弃代码 |
| A3. 保持现状 | 不做处理 | 零风险 | 代码不一致 |

**建议**: A1（彻底删除），但需先全局搜索确认无引用。

---

### 决策 B: StyleManager 处理

**背景**: `utils/ui_utils.py` 中的 `StyleManager` 类与主题系统独立，颜色不一致。

| 选项 | 操作 | 优点 | 缺点 |
|------|------|------|------|
| B1. 删除 StyleManager | 迁移所有引用到 unified_style_system | 统一系统 | 工作量大 |
| B2. 改为代理 | StyleManager 内部调用 theme_engine | 兼容旧代码 | 间接层 |
| B3. 保持现状 | 不做处理 | 零风险 | 双系统并存 |

**建议**: B2（改为代理），平衡兼容性和一致性。

---

### 决策 C: 调色板更新范围

| 选项 | 操作 | 优点 | 缺点 |
|------|------|------|------|
| C1. 完整更新 | 按第五节建议更新 | 完全符合 Linear | 需测试 |
| C2. 仅修复死白 | 只改 bg_app 等 | 改动小 | 不完整 |
| C3. 保持现状 | 不做处理 | 零风险 | 死白问题 |

**建议**: C1（完整更新），一次性解决所有设计问题。

---

## 附录：颜色对照表

### Dark 主题颜色对照

| Token | 当前值 | 建议值 | 变化 |
|-------|--------|--------|------|
| brand.main | #5E6AD2 | #5E6AD2 | 不变 |
| neutral.bg_app | #121212 | #121212 | 不变 |
| neutral.bg_input | #101010 | #1A1A1A | 调浅 |
| text.disabled | #444444 | #444444 | 不变 |
| (新增) overlay.dark | - | rgba(0,0,0,0.75) | 新增 |
| (新增) semantic.success_subtle | - | rgba(39,201,63,0.15) | 新增 |
| (新增) accent.orange | - | #FF6B35 | 新增 |

### Light 主题颜色对照

| Token | 当前值 | 建议值 | 变化 |
|-------|--------|--------|------|
| brand.main | #5E6AD2 | #5E6AD2 | 不变 |
| neutral.bg_app | #FFFFFF | #FBFBFC | 微灰 |
| neutral.bg_input | #FFFFFF | #F7F7F8 | 微灰 |
| neutral.bg_surface | #FFFFFF | #FAFAFA | 微灰 |
| text.disabled | #999999 | #AAAAAA | 调淡 |
| (新增) overlay.dark | - | rgba(0,0,0,0.5) | 新增 |
| (新增) semantic.success_subtle | - | rgba(34,165,71,0.1) | 新增 |
| (新增) accent.orange | - | #E55A2B | 新增 |

---

*文档结束*
