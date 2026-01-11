# 鸽梦打包知识库

> 记录打包过程中的坑和注意事项，避免重复踩坑

**最后更新**: 2025-12-13
**当前版本**: v1.4.0

---

## 快速打包命令

使用 `/kim-pack [版本号]` 自动化打包，例如：
```bash
/kim-pack 1.4.0
```

---

## 🚨 已知问题和修复

### 1. 视频水印 ffmpeg @ 字符转义问题

**问题描述**：
体验版视频水印不生效，ffmpeg 报错 `No option name near 'white@0.3'`

**根因**：
ffmpeg drawtext 滤镜中 `fontcolor=white@0.3` 的 `@` 字符需要转义为 `\@`

**修复位置**：
`edition/watermark_service.py` → `_escape_text()` 方法

```python
# 修复前（缺少 @ 转义）
def _escape_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace(",", "\\,")
        .replace("'", "\\'")
    )

# 修复后
def _escape_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace(",", "\\,")
        .replace("'", "\\'")
        .replace("@", "\\@")  # ← 必须转义！
    )
```

**验证方法**：
```bash
# 测试 ffmpeg drawtext 是否正常
ffmpeg -f lavfi -i testsrc=duration=3:size=320x240:rate=25 \
  -vf "drawtext=text=PIGEON:fontcolor=white\@0.3:fontsize=24:x=10:y=10" \
  -y /tmp/test_watermark.mp4
```

**修复日期**: 2025-12-01

---

### 2. 跨平台路径存储问题

**问题描述**：
Windows 生成的记录在 Mac 上无法显示参考图缩略图

**根因**：
Windows 存储绝对路径如 `C:/Users/kyz/Documents/...`，Mac 无法识别

**修复方案**：
统一使用相对路径存储，加载时拼接当前存储目录

**修复位置**：
`modules/seedance/manager.py` → `generate_video()` 方法

**修复日期**: 2025-12-01 (commit: e26b5a8)

---

### 3. 体验版 ffmpeg 签名失败 (com.apple.provenance)

**问题描述**：
打包体验版后签名失败，报错：
```
resource fork, Finder information, or similar detritus not allowed
```

**根因**：
从网上下载的 ffmpeg 二进制文件带有 `com.apple.provenance` 扩展属性，macOS 的 codesign 不允许签名带有此属性的文件。

**修复方案**：
签名前删除 ffmpeg 文件的 provenance 属性

**修复步骤**：
```bash
# 删除 ffmpeg 的 provenance 属性
xattr -d com.apple.provenance "dist/鸽梦Godream_v1.4.0_体验版.app/Contents/MacOS/edition/resources/bin/ffmpeg"
xattr -d com.apple.provenance "dist/鸽梦Godream_v1.4.0_体验版.app/Contents/MacOS/edition/resources/bin/ffprobe"

# 然后再清理其他属性并签名
xattr -cr "dist/鸽梦Godream_v1.4.0_体验版.app"
codesign -s - --force --all-architectures --timestamp --deep "dist/鸽梦Godream_v1.4.0_体验版.app"
```

**发现日期**: 2025-12-13

---

## 📦 打包配置对照表

| 项目 | 体验版 | 正式版 |
|------|--------|--------|
| spec 文件 | `GoDream_macOS_Trial.spec` | `GoDream_macOS_Official.spec` |
| 配置文件 | `config_api_trial.py` | `config_api_production.py` |
| Runtime Hook | `hook-config_api_trial.py` | `hook-config_api.py` |
| 图标 | `godream_trial_correct.icns` | `godream_official.icns` |
| Bundle ID | `com.gemeng.ai.trial` | `com.gemeng.ai` |
| **水印** | ✅ 开启 (PIGEON, 0.3) | ❌ 关闭 |
| **FFmpeg** | ✅ 包含 (视频水印需要) | ❌ 不包含 (缩略图用 OpenCV) |
| 应用大小 | ~254MB | ~236MB |
| 压缩包大小 | ~99MB | ~92MB |

---

## 🔧 打包前检查清单

### 版本号同步
确保以下文件版本号一致：
- [ ] `GoDream_macOS_Trial.spec` (CFBundleShortVersionString)
- [ ] `GoDream_macOS_Official.spec` (CFBundleShortVersionString)
- [ ] `config_api_trial.py` (version 字段)
- [ ] `config_api_production.py` (version 字段)
- [ ] `version.py` (APP_VERSION)

### 水印功能检查（体验版）
- [ ] `config_api_trial.py` 中 `LOCAL_WATERMARK_CONFIG.enabled = True`
- [ ] `edition/watermark_service.py` 中 `_escape_text()` 包含 `@` 转义
- [ ] ffmpeg 二进制支持 drawtext 滤镜

### 路径检查
- [ ] ffmpeg 打包路径: `edition/resources/bin/ffmpeg` (仅体验版)
- [ ] 字体打包路径: `edition/resources/fonts/NotoSansSC-Regular.otf`
- [ ] Runtime hook 正确别名 config_api

---

## 🔐 签名流程（无 Apple Developer 证书）

本项目使用 **ad-hoc 签名**，无需 Apple Developer 证书。

### 正式版签名
```bash
# 清理元数据
find "dist/鸽梦Godream_v1.4.0_正式版.app" -name "._*" -delete
find "dist/鸽梦Godream_v1.4.0_正式版.app" -name ".DS_Store" -delete
xattr -cr "dist/鸽梦Godream_v1.4.0_正式版.app"

# Ad-hoc 签名
codesign -s - --force --all-architectures --timestamp --deep "dist/鸽梦Godream_v1.4.0_正式版.app"
```

### 体验版签名（重要：先处理 ffmpeg）
```bash
# 1. 删除 ffmpeg 的 provenance 属性（关键！）
xattr -d com.apple.provenance "dist/鸽梦Godream_v1.4.0_体验版.app/Contents/MacOS/edition/resources/bin/ffmpeg" 2>/dev/null || true
xattr -d com.apple.provenance "dist/鸽梦Godream_v1.4.0_体验版.app/Contents/MacOS/edition/resources/bin/ffprobe" 2>/dev/null || true

# 2. 清理其他元数据
find "dist/鸽梦Godream_v1.4.0_体验版.app" -name "._*" -delete
find "dist/鸽梦Godream_v1.4.0_体验版.app" -name ".DS_Store" -delete
xattr -cr "dist/鸽梦Godream_v1.4.0_体验版.app"

# 3. Ad-hoc 签名
codesign -s - --force --all-architectures --timestamp --deep "dist/鸽梦Godream_v1.4.0_体验版.app"
```

### 用户首次打开方式
Ad-hoc 签名的应用会被 Gatekeeper 阻止，用户需要：

1. 解压 zip 文件
2. 将 .app 拖入「应用程序」文件夹
3. **右键点击** .app → 选择「打开」
4. 在弹出的对话框中点击「打开」
5. 之后可正常双击打开

或使用命令行：
```bash
xattr -d com.apple.quarantine /Applications/鸽梦Godream*.app
```

---

## 🧪 打包后验证步骤

### 1. 基本功能
```bash
# 启动应用
open "dist/鸽梦Godream_v1.4.0_体验版.app"
```

### 2. 水印验证（体验版）
- 生成一张图片 → 检查是否有 "PIGEON" 水印
- 生成一个视频 → 检查是否有 "PIGEON" 水印

### 3. 跨平台数据
- 导入 Windows 生成的 SQLite 数据库
- 检查参考图缩略图是否正常显示

---

## 📝 打包命令

### 使用 slash command（推荐）
```bash
/kim-pack 1.4.0
```

### 手动打包

```bash
# 切换到项目目录
cd /Users/yunchang/Documents/GitHub/gemeng2

# 清理旧构建
rm -rf build/
rm -rf dist/鸽梦Godream*

# 打包正式版
pyinstaller --clean GoDream_macOS_Official.spec

# 签名正式版
find "dist/鸽梦Godream_v1.4.0_正式版.app" -name "._*" -delete
find "dist/鸽梦Godream_v1.4.0_正式版.app" -name ".DS_Store" -delete
xattr -cr "dist/鸽梦Godream_v1.4.0_正式版.app"
codesign -s - --force --all-architectures --timestamp --deep "dist/鸽梦Godream_v1.4.0_正式版.app"

# 创建正式版 zip
cd dist && zip -r -y "鸽梦Godream_v1.4.0_正式版_macOS.zip" "鸽梦Godream_v1.4.0_正式版.app"
cd ..

# 打包体验版
pyinstaller --clean GoDream_macOS_Trial.spec

# 签名体验版（注意 ffmpeg provenance）
xattr -d com.apple.provenance "dist/鸽梦Godream_v1.4.0_体验版.app/Contents/MacOS/edition/resources/bin/ffmpeg" 2>/dev/null || true
xattr -d com.apple.provenance "dist/鸽梦Godream_v1.4.0_体验版.app/Contents/MacOS/edition/resources/bin/ffprobe" 2>/dev/null || true
find "dist/鸽梦Godream_v1.4.0_体验版.app" -name "._*" -delete
find "dist/鸽梦Godream_v1.4.0_体验版.app" -name ".DS_Store" -delete
xattr -cr "dist/鸽梦Godream_v1.4.0_体验版.app"
codesign -s - --force --all-architectures --timestamp --deep "dist/鸽梦Godream_v1.4.0_体验版.app"

# 创建体验版 zip
cd dist && zip -r -y "鸽梦Godream_v1.4.0_体验版_macOS.zip" "鸽梦Godream_v1.4.0_体验版.app"
```

---

## 🔗 相关文件

- [watermark_service.py](../edition/watermark_service.py) - 水印服务
- [resources.py](../edition/resources.py) - 资源路径解析
- [GoDream_macOS_Trial.spec](../GoDream_macOS_Trial.spec) - 体验版打包配置
- [GoDream_macOS_Official.spec](../GoDream_macOS_Official.spec) - 正式版打包配置
- [kim-pack.md](.claude/commands/kim-pack.md) - 打包 slash command
- [macOS 首次使用指南](../docs/macOS_首次使用指南.md) - 用户文档

---

*每次遇到新的打包问题，请更新此文档！*
