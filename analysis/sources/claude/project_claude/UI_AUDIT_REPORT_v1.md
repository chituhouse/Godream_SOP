# UI 架构全面审计与重构规划 (UI Audit & Refactor Plan)

**日期**: 2025-12-18
**状态**: 执行中 (In Progress)
**责任人**: Gemini CLI
**相关文档**: 
- `.claude/UI_AUDIT_REPORT_v1.md` (本文档)
- `utils/style_system.py`

---

## 1. 核心问题诊断摘要 (Executive Summary)

经过深度代码审计，我们发现当前 UI 系统存在三个层级的断裂，导致了用户反馈的崩溃、样式混乱和布局挤压问题。

| 优先级 | Bug / 现象 | 根本原因 (Root Cause) | 涉及文件 | 修复策略 |
| :--- | :--- | :--- | :--- | :--- |
| **P0** | **详情页关闭崩溃** | `VideoDetailDialog` 存在重复的 `closeEvent` (Zombie Code)，引用了不存在的变量 `is_using_opencv`。 | `components/dialogs/video_detail_dialog.py` | **外科手术式切除**：直接删除文件末尾的重复代码。 |
| **P0** | **参数区主题失效** | `SchemaFormRenderer` 初始化时未连接 `unified_style_system` 的信号，组件创建即“死”在初始主题。导致 Light 模式下输入框仍为黑底。 | `components/forms/schema_form_renderer.py` | **接入生命线**：连接 `styleChanged` 信号，实现 `_on_theme_changed` 方法刷新样式。 |
| **P1** | **亮色模式显示异常** | `ImageDetailDialog` 参数区使用了 f-string 硬编码颜色，且默认回退色为深色。 | `components/dialogs/image_detail_dialog.py` | **去硬编码**：移除 f-string 样式注入，改用动态 QSS 类或在 `update_theme` 中重刷。 |
| **P2** | **参数区布局挤压** | `QVBoxLayout` + 硬编码绿色边框。未使用 Grid 或 FormLayout 导致垂直空间利用率低。 | `components/dialogs/image_detail_dialog.py` | **布局重构**：改用双列 `QGridLayout`；移除突兀的绿色边框，使用主题定义的 subtle border。 |

---

## 2. 深度分析与解决方案 (Deep Dive & Solutions)

### 2.1 问题一：`VideoDetailDialog` 崩溃修复 (P0)
*   **现象**: 关闭视频详情页时程序崩溃。
*   **分析**: Python 类定义中，后定义的 `closeEvent` 覆盖了先定义的。文件末尾残留了旧版代码（L1230+），引用了已被重构移除的 `self.is_using_opencv`。
*   **方案**: 删除 L1231-L1252 的 `closeEvent` 方法。

### 2.2 问题二：`SchemaFormRenderer` 主题失联 (P0)
*   **现象**: 切换主题后，参数配置区（Schema 渲染区域）无变化；Light 模式下输入框背景为黑色（#000/深色），导致文字不可见。
*   **分析**: `SchemaFormRenderer` 是动态生成表单的核心组件，但它没有订阅 `styleChanged` 信号。组件在 `__init__` 时根据当时的主题生成样式后，就再也不会更新。
*   **方案**:
    1.  引入 `unified_style_system`。
    2.  在 `__init__` 连接信号: `unified_style_system.styleChanged.connect(self._on_theme_changed)`。
    3.  实现 `_on_theme_changed`: 重新获取颜色表，并调用 `setStyleSheet` 或重刷子组件样式。

### 2.3 问题三：参数区布局与绿色边框 (P1/P2)
*   **现象**: 图片详情页右侧参数区有刺眼的绿色边框；参数多时组件从上到下挤压，无法显示完整。
*   **分析**:
    *   **绿色边框**: 硬编码了 `border-color: #4CAF50` (Material Green)。
    *   **布局**: 使用 `QVBoxLayout` 线性堆叠，空间利用率低。
*   **方案**:
    *   **布局**: 改为 `QGridLayout`，实现双列布局 (Label: Value | Label: Value)。
    *   **样式**: 移除硬编码颜色，使用 `unified_style_system` 提供的 `border_subtle` 和 `bg_input`。

---

## 3. 执行计划 (Execution Roadmap)

1.  **Fix Crash**: Remove zombie code in `VideoDetailDialog`.
2.  **Fix Theme**: Connect `SchemaFormRenderer` to theme signals.
3.  **Refactor UI**: Improve `ImageDetailDialog` layout and remove green borders.
4.  **Verify**: Run basic tests to ensure no regressions.