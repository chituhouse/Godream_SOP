# UI 主题系统设计模式

> 从硬编码地狱到 Token 系统的演进之路

---

## 1. 问题描述：硬编码的危害

### 1.1 问题表现

在 GoDream 项目开发过程中，UI 样式硬编码问题经历了从"无意识积累"到"爆发式失控"再到"系统性治理"的完整生命周期。

**早期阶段（2025年9月）**：
- 每次修改 UI 时直接硬编码颜色值、字体大小
- `qt_app.py`（9075行）中存在 **86处硬编码 font-size**
- `components/cards/video_card.py` 使用硬编码 `font-size: {DpiScaler.px(12)}px`
- 全项目累计 **539个硬编码样式问题** 分散在 34 个文件中

**用户真实痛点描述**：
```
用户反馈字体系统"治标不治本"，参数栏（下拉菜单）字体未跟随系统变化，
不同区域字体不一致。
```

### 1.2 具体案例

#### 案例1：字体缩放功能失效（2025-09-25）
```
问题：Mac 用户使用 Cmd++ 无法缩放字体
根因：
1. qt_app.py 第8638行缺少 Mac 系统 Cmd 快捷键配置
2. 86处硬编码 font-size 覆盖了统一样式系统
修复：扫描191个Python文件，修复25个文件中的204个硬编码样式问题
```

#### 案例2：样式"三权分立"混乱（2025-11-14）
用户截图反馈参数区样式问题后，深度分析发现：
```
样式架构（混乱）：
├─ 1. UnifiedStyleSystem
│  └─ 基础定义，但不完善
│     ├─ ComboBox view样式未生效
│     ├─ 边框颜色太暗
│     └─ 缺少focus状态
├─ 2. schema_form_renderer.py
│  └─ 绑定时额外setStyleSheet
│     └─ 覆盖了统一系统的样式
└─ 3. qt_app.py各处
      └─ 用setStyleSheet覆盖统一样式
```

#### 案例3：视频详情页配色割裂（2025-12月）

用户原话：
> "方案 B，播放器黑底没问题，但其他部件的底色应该纳入统一主题。其他部分的地址应该纳入到整体的主题系统，而不是部分自定义。另外现在就是参数区有两三种颜色造成比较割裂，比如参数名和参数内容颜色就不一样。"

> "视频详情页的背景色，好像不是白色，或者跟背景不一致的色彩...跟图片详情页的颜色有什么区别，是不是两套颜色配置？"

---

## 2. Token 系统设计原则

### 2.1 核心原则：单一样式真源

**统一样式系统绝对主权**：所有组件 -> `unified_style_system.apply_to_widget()`

```python
# 正确做法
from utils.style_system import unified_style_system
unified_style_system.apply_to_widget(widget)

# 错误做法 - 直接硬编码
widget.setStyleSheet("font-size: 12px; color: #333333;")
```

### 2.2 Token 层次结构

基于 Ant Design 设计体系的 Token 分层：

```typescript
// godream-electron-client/src/theme/tokens.ts
const darkTheme = {
  // 基础 Token - 语义化颜色
  colorTextBase: '#f4f6ff',
  colorText: 'rgba(244, 246, 255, 0.88)',
  colorTextSecondary: 'rgba(233, 238, 255, 0.62)',

  // 组件 Token - 统一由 ConfigProvider 注入
  colorPrimary: '#7285FF',  // 主色调
  colorInfo: '#7285FF',

  // 边框、圆角、阴影等均走 Token
}
```

### 2.3 样式注入规范

**唯一注入方式**：应用根部的 `ConfigProvider.theme.token`

```typescript
// 正确 - 通过 ConfigProvider 统一注入
<ConfigProvider theme={{ token: darkTheme }}>
  <App />
</ConfigProvider>

// 禁止 - 组件内硬编码
<div style={{ color: '#333333', backgroundColor: '#f5f5f5' }}>
```

**禁止事项**：
- 禁止页面/组件硬编码颜色、圆角、阴影、字号
- 禁止在 CSS 文件中直接写入 `#0F1116`、`rgba(255,255,255,0.04)` 等色值
- 禁止绕过 `ConfigProvider Token` 输出样式

---

## 3. 用户真实案例（附对话片段）

### 案例1：下拉菜单背景色异常（2025-10-19）

**用户反馈**：
> "下拉菜单，当我选项的时候背景变成白色了，说明这个颜色应该不是标准的，不是符合标准的颜色，你排查一下，我希望这个颜色能够统一一下。"

**问题诊断**：
```
godream-electron-client/src/App.css 与 src/styles/antd-components.css
大量直接写入 #0F1116、rgba(255,255,255,0.04) 等色值，
未通过 ConfigProvider Token 输出，违背"仅用 Token 调整"的规范；
标准组件因此呈现与文档不同的底色/边框。
```

**用户确认解决方向**：
> "好，我大概明白了，其实就是还是把自定义的颜色，改成跟Token相似的暗色对吗？就可以保证是暗色的主题又是标准的方案标准的颜色是这样吗？"

### 案例2：边框对比度问题（2025-11-14）

**Serena 记忆记录**：
```
### 问题2：参数输入框没有明显边框
**症状**：用户不知道哪里可以操作
**根因**：border颜色 #3a3a3a 在 #2d2d2d 背景上对比度太低
**位置**：utils/style_system.py Line 134, 201

### 问题3：模型版本/分辨率下拉菜单样式不统一
**症状**：不同模式下样式跳变
**根因**：某些ComboBox可能绕过了统一样式系统
```

### 案例3：跨平台样式差异（2025-12月）

**用户反馈**：
> "现在图片和视频页参数区的所有组件边框，是不是都是 Mac 电脑上自定义的，我在 Windows 端打开，都是没有边框的，尤其是提示词框和参考图画廊，视频模式下边框是靠组件背景色不同跟父组件容器背景做区分的。但是在 Mac 电脑上，UI 显示是正常的。这是什么原因，你排查下这些边框是不是都是自定义的。是不是跟 Windows 不兼容？"

---

## 4. 最佳实践

### 4.1 样式迁移流程

当发现硬编码样式时，使用工具化方式批量迁移：

```bash
# 预演模式 - 查看将修改的内容
python tools/style_migration_tool.py --dry-run

# 实际修复
python tools/style_migration_tool.py
```

**样式迁移成果示例**（2025-09-25）：
- 修复 **539个硬编码样式问题**
- qt_app.py: 110个样式问题 -> 已迁移到统一系统
- 34个文件完成自动迁移
- 备份保存在 `.style_backup` 目录

### 4.2 新组件开发规范

```python
# Qt/PySide 组件开发
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        # 必须：应用统一样式系统
        unified_style_system.apply_to_widget(self)

        # 禁止：直接设置样式表
        # self.setStyleSheet("font-size: 14px;")  # 错误!
```

```typescript
// React 组件开发
const MyComponent: React.FC = () => {
  // 必须：使用 theme token
  const { token } = theme.useToken();

  return (
    <div style={{
      color: token.colorText,           // 正确
      // color: '#333333',               // 错误!
      backgroundColor: token.colorBgContainer
    }}>
      内容
    </div>
  );
};
```

### 4.3 主题切换支持

确保 Light/Dark 模式切换时，所有组件正确响应：

```typescript
// tokens.ts 需要同时定义 light 和 dark 主题
export const lightTheme = { /* ... */ };
export const darkTheme = { /* ... */ };

// App.tsx 根据系统偏好切换
const currentTheme = isDarkMode ? darkTheme : lightTheme;
```

### 4.4 文档规范对齐

所有颜色值必须与设计规范文档对齐：

```
设计规范：docs/design-system/one-pager.md
主色要求：#5B8CFF

实际检查：godream-electron-client/src/theme/tokens.ts
当前值：colorPrimary: '#7285FF'  <- 不一致!

修复：将 colorPrimary/colorInfo 设为 #5B8CFF
```

---

## 5. 检查清单

### 5.1 开发前检查

- [ ] 确认设计规范文档（`docs/design-system/`）中的 Token 定义
- [ ] 确认 `theme/tokens.ts` 中已定义所需的语义化 Token
- [ ] 确认 `ConfigProvider` 已在根组件正确配置

### 5.2 编码时检查

- [ ] 所有颜色值使用 Token 而非硬编码十六进制值
- [ ] 所有字体大小使用 Token 或组件默认值
- [ ] 所有边框、圆角、阴影使用 Token
- [ ] Qt 组件调用 `unified_style_system.apply_to_widget()`
- [ ] React 组件使用 `theme.useToken()` 获取 Token

### 5.3 提交前检查

- [ ] 运行 `python tools/style_migration_tool.py --dry-run` 检查新增硬编码
- [ ] 在 Light 和 Dark 模式下均测试 UI 显示
- [ ] 在 Windows 和 macOS 上验证样式一致性
- [ ] 确认新组件样式与现有组件视觉一致

### 5.4 Code Review 检查点

- [ ] 禁止 PR 中包含新的硬编码颜色值
- [ ] 禁止 `setStyleSheet()` 中包含 `font-size` 或颜色值
- [ ] 禁止 CSS 文件中新增十六进制颜色值
- [ ] 确认使用的 Token 名称符合语义化命名规范

---

## 6. 参考文档

- **设计规范**：`docs/design-system/one-pager.md`
- **Token 定义**：`godream-electron-client/src/theme/tokens.ts`
- **样式迁移工具**：`tools/style_migration_tool.py`
- **统一样式系统**：`utils/style_system.py`
- **相关 ADR**：`sop/adr/0002-pyqt5-to-pyside6.md`（Token theme 迁移）

---

## 7. 时间线总结

| 时间 | 事件 | 硬编码数量 |
|------|------|-----------|
| 2025-09-23 | 发现字体系统问题 | 539+ |
| 2025-09-25 | 执行样式迁移工具 | 修复 204 处 |
| 2025-10-09 | 样式治理草案 | 残留 86 处 |
| 2025-10-13 | 确认 Ant Design Token 方案 | 规划中 |
| 2025-10-19 | Token 系统初步落地 | 大幅减少 |
| 2025-11-14 | 参数区样式深度重构 | 局部清零 |
| 2025-12 月 | 主题系统基本成熟 | 持续优化 |

---

## 8. 教训总结

### 8.1 技术债的积累规律

1. **无意识阶段**：每次"快速修复"添加一个硬编码值，看起来无害
2. **隐患积累**：硬编码值分散在数十个文件，无人察觉规模
3. **问题爆发**：用户反馈"样式不统一""缩放不生效""跨平台不一致"
4. **代价昂贵**：需要扫描 191 个文件，修复 539 处问题

### 8.2 核心教训

> "样式架构的一致性问题，越早建立规范，代价越小。"

1. **先建规范，再写代码**：在项目初期就定义 Token 系统和统一样式入口
2. **工具化守护**：通过 lint 规则、样式扫描工具防止硬编码回归
3. **单一入口原则**：所有样式修改必须通过统一系统，禁止绕道
4. **跨平台验证**：每次 UI 修改都需在 Windows/macOS 双端验证

---

*文档版本：v1.0*
*创建日期：2026-01-11*
*基于对话记录：conversations/serena/2025-09-25、2025-10-13、2025-11-14、conversations/codex/history.jsonl*
