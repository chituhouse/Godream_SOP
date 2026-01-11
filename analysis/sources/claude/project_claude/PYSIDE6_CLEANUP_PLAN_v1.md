# PySide6 迁移清理计划 v1.0

> 状态：待审批
> 创建时间：2025-12-18
> 前置条件：主题系统重构 Phase 1-3 已完成

---

## 背景

主题系统重构已完成，删除了 `qt_app.py` 和相关废弃代码。但仍有以下遗留问题：
1. 打包脚本使用不存在的虚拟环境 `build_env310`
2. 10 个 Spec 文件仍指向已删除的 `qt_app.py`
3. 代码中残留 PyQt5 引用和 qt_app 导入

---

## 任务清单

### Phase A：打包脚本修复（优先级：高）

#### A1. 修改 build_macos_trial.sh 使用系统 Python

**文件**：`build_macos_trial.sh`

**修改点**：
| 行号 | 当前内容 | 修改为 |
|------|----------|--------|
| 12 | `PYINSTALLER_HOOKS_DIR="build_env310/lib/python3.10/site-packages/PyInstaller/hooks"` | 动态检测系统 Python site-packages |
| 41 | `build_env310/bin/pyinstaller` | `python3 -m PyInstaller` 或 `pyinstaller` |

**新脚本逻辑**：
```bash
# 动态检测 PyInstaller hooks 目录
PYTHON_SITE=$(python3 -c "import site; print(site.getsitepackages()[0])")
PYINSTALLER_HOOKS_DIR="$PYTHON_SITE/PyInstaller/hooks"

# 使用系统 pyinstaller
python3 -m PyInstaller --clean --noconfirm GoDream_macOS_Trial.spec
```

**前提条件**：系统需安装 `pip install pyinstaller PySide6`

---

### Phase B：Spec 文件修复（优先级：高）

#### B1. 修复入口点 qt_app.py → main.py

**文件清单**（10 个）：

| 文件 | 行号 | 当前值 | 修改为 |
|------|------|--------|--------|
| `鸽梦Godream_v1.0.1_正式版.spec` | 12 | `['qt_app.py']` | `['main.py']` |
| `GoDream_Official.spec` | 17 | `['qt_app.py']` | `['main.py']` |
| `GoDream_macOS_Official.spec` | 18 | `['qt_app.py']` | `['main.py']` |
| `GeMeng.spec` | 5 | `['qt_app.py']` | `['main.py']` |
| `鸽梦 GoDream.spec` | 5 | `['qt_app.py']` | `['main.py']` |
| `packaging/macos/godream_trial.spec` | 39 | `qt_app.py` | `main.py` |
| `packaging/windows/gemeng_windows_trial.spec` | 63 | `qt_app.py` | `main.py` |
| `packaging/windows/gemeng_fixed_v2.9.spec` | 60 | `qt_app.py` | `main.py` |
| `packaging/windows/gemeng_windows_onefile.spec` | 55 | `qt_app.py` | `main.py` |
| `Win_GoDream.spec` | 5 | `['qt_app.py.backup']` | `['main.py']` |

#### B2. 修复 hiddenimports PyQt5 → PySide6

每个 Spec 文件中的 `hiddenimports` 需要检查并更新：
- `PyQt5.QtCore` → `PySide6.QtCore`
- `PyQt5.QtGui` → `PySide6.QtGui`
- `PyQt5.QtWidgets` → `PySide6.QtWidgets`
- 等...

**注意**：`GoDream_macOS_Trial.spec` 已修复，可作为参考模板。

---

### Phase C：代码清理（优先级：中）

#### C1. 清理 creation_components.py 遗留导入

**文件**：`components/creation_components.py`
**行号**：1240-1260

**当前代码**：
```python
try:
    from qt_app import safe_get_open_file_name
except ImportError:
    from PySide6.QtWidgets import QFileDialog
    def safe_get_open_file_name(parent, title, start_dir, filters):
        # fallback 实现...
```

**修改为**：
```python
from PySide6.QtWidgets import QFileDialog

def safe_get_open_file_name(parent, title, start_dir, filters):
    # 直接使用实现，删除 try-except
```

#### C2. 更新启动脚本依赖检查

**文件**：
- `scripts/python/start_app.py`
- `scripts/macos/start_mac.py`

**修改点**：
| 文件 | 行号 | 当前值 | 修改为 |
|------|------|--------|--------|
| `start_app.py` | 16 | `'PyQt5'` | `'PySide6'` |
| `start_app.py` | 29-30 | `from PyQt5.QtWidgets` | `from PySide6.QtWidgets` |
| `start_mac.py` | 27 | `'PyQt5'` | `'PySide6'` |
| `start_mac.py` | 40-41 | `from PyQt5.QtWidgets` | `from PySide6.QtWidgets` |

#### C3. 更新配置文件描述

**文件**：
- `config_api_trial.py:23`
- `config_api_production.py:22`

**修改**：`"PyQt5 local AI content tool"` → `"PySide6 local AI content tool"`

---

### Phase D：Hooks 迁移（优先级：低）

#### D1. 创建 PySide6 Hooks（可选）

当前 `hooks/` 目录包含 PyQt5 专用 hooks。PySide6 通常不需要自定义 hooks，PyInstaller 内置支持较好。

**建议**：先尝试不使用自定义 hooks 打包，如果失败再创建。

#### D2. 归档或删除 PyQt5 Hooks

**文件**：
- `hooks/hook-PyQt5.QtCore.py`
- `hooks/hook-PyQt5.QtGui.py`
- `hooks/hook-PyQt5.QtWidgets.py`
- `hooks/hook-PyQt5.QtMultimedia.py`
- `hooks/hook-PyQt5.QtNetwork.py`
- `hooks/hook-PyQt5.QtPrintSupport.py`

**处理方式**：移动到 `archive/legacy_hooks/`

---

### Phase E：工具清理（优先级：低）

#### E1. 归档废弃 tools/ 脚本

约 20+ 个脚本仍引用 `qt_app.py`，建议批量移动到 `archive/legacy_tools/`。

**待归档列表**：
- `tools/fix_all_unterminated_strings.py`
- `tools/fix_inline_docstrings.py`
- `tools/fix_line_*.py` (多个)
- `tools/repair_top.py`
- `tools/sanitize_docstrings.py`
- `tools/strip_triple_blocks.py`
- `tools/fix_all_string_errors.py`
- `tools/diagnose_reference_display.py`
- `tools/verify_waterfall_changes.py`
- `tools/diagnose_visibility_rules.py`
- `tools/diagnose_video_reference_panel.py`
- `tools/system_diagnosis.py`
- `tools/fix_final_dependencies.py`
- `tools/quick_test_reference.py`
- `tools/waterfall_loading_analysis.py`
- `tools/history_virtualization_smoke.py`

---

## 执行顺序

```
Phase A (打包脚本)
    ↓
Phase B (Spec 文件)
    ↓
[打包测试验证]
    ↓
Phase C (代码清理)
    ↓
Phase D (Hooks 迁移) - 可选
    ↓
Phase E (工具清理) - 可选
```

---

## Git 提交策略

| Phase | Commit Message |
|-------|----------------|
| A1 | `fix: 打包脚本使用系统 Python` |
| B1-B2 | `fix: Spec 文件入口点和依赖更新 (qt_app→main, PyQt5→PySide6)` |
| C1-C3 | `refactor: 清理 PyQt5 遗留引用` |
| D1-D2 | `chore: 归档 PyQt5 hooks` |
| E1 | `chore: 归档废弃 tools 脚本` |

---

## 验收标准

- [ ] `./build_macos_trial.sh` 可成功执行
- [ ] 生成的 .app 可正常启动
- [ ] 无 PyQt5 相关导入错误
- [ ] 无 qt_app 相关导入错误

---

## 回滚点

在执行前创建 checkpoint：
```bash
git add -A && git commit -m "checkpoint: PySide6 清理执行前"
git tag checkpoint-pre-pyside6-cleanup
```

---

## 风险评估

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| Spec 修改后打包失败 | 中 | 高 | 以 GoDream_macOS_Trial.spec 为模板 |
| PySide6 缺少自定义 hooks | 低 | 中 | 按需从 PyQt5 hooks 迁移 |
| 遗漏的 qt_app 引用 | 低 | 低 | 全局搜索已覆盖 |

---

**审批状态**：⏳ 待用户审批

**审批后执行命令**：
```
确认后，我将按 Phase A → B → C 顺序执行
```
