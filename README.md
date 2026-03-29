# 王者荣耀自动点击器 v3.0

完整的重新架构版本，修复所有已知问题。

## ✨ 新功能

### 1. 分辨率自动适配 ⭐
- 自动检测设备分辨率
- 自动适配所有坐标
- 支持720p/1080p/2K等任意分辨率
- 支持横屏/竖屏自动切换

### 2. 模拟器支持 ⭐
- 支持x86/x86_64架构
- 自动检测设备类型（真机/模拟器）
- 兼容性检查和提示
- 支持主流模拟器（雷电、夜神、MuMu等）

### 3. 横屏问题修复 ⭐
- 修复横屏切换时的闪退问题
- 悬浮窗生命周期管理
- Activity配置优化
- 支持屏幕方向变化处理

### 4. 设备检测
- 自动检测设备信息
- 架构兼容性检查
- 系统版本检测
- 屏幕参数获取

### 5. 增强稳定性
- 单例模式管理悬浮窗
- 完善的错误处理
- 详细的日志记录
- 状态监控

## 🔧 修复内容

### 启动崩溃问题 ✅
**问题**: 真机和模拟器都闪退
**原因**: `screen_width`属性未初始化
**修复**: 在`build()`方法开头初始化所有属性

```python
# 修复前
def build(self):
    self.layout = BoxLayout(...)
    # 使用self.screen_width ❌ 未初始化

# 修复后
def build(self):
    self.screen_width = Window.width if Window else 720  # ✅ 先初始化
    self.screen_height = Window.height if Window else 1280
    self.layout = BoxLayout(...)
```

### 横屏闪退问题 ✅
**问题**: 屏幕旋转时应用崩溃
**原因**: 悬浮窗重复添加
**修复**:
1. 创建`FloatWindowManager`单例管理悬浮窗
2. 配置`android:configChanges`防止Activity重建
3. 添加屏幕方向变化处理

### 模拟器架构问题 ✅
**问题**: x86模拟器无法运行ARM应用
**原因**: APK只包含ARM架构库
**修复**: 配置多架构支持
```ini
android.archs = armeabi-v7a, arm64-v8a, x86, x86_64
```

### 分辨率适配问题 ✅
**问题**: 固定坐标，其他分辨率点击不准
**原因**: 缺少分辨率适配逻辑
**修复**: 创建`ResolutionAdapter`自动缩放坐标

## 📁 项目结构

```
wangzhe_autoclicker_v3/
├── main.py                          # 主程序（已修复）
├── buildozer.spec                   # 构建配置（多架构支持）
├── scripts/
│   ├── enhanced_auto_clicker.py     # 增强版核心
│   ├── resolution_adapter.py        # 分辨率适配器
│   ├── device_detector.py           # 设备检测器
│   └── float_window_manager.py      # 悬浮窗管理器
├── README.md                        # 本文档
└── .github/
    └── workflows/
        └── build.yml                # 自动构建配置
```

## 🚀 快速开始

### 方法1: GitHub Actions自动构建（推荐）⭐

1. **创建GitHub仓库**
   - 访问 https://github.com/new
   - 创建名为 `wangzhe-autoclicker` 的仓库

2. **上传代码**
   ```bash
   cd wangzhe_autoclicker_v3
   git init
   git add .
   git commit -m "v3.0: 完整重构版本"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/wangzhe-autoclicker.git
   git push -u origin main
   ```

3. **下载APK**
   - 等待20分钟自动构建
   - 在 Actions 页面下载APK

### 方法2: 本地构建

#### Windows用户
```bash
# 安装WSL
wsl --install -d Ubuntu

# 在WSL中
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk
pip3 install buildozer cython

# 构建
cd /mnt/c/path/to/wangzhe_autoclicker_v3
buildozer android debug
```

#### Linux/Mac用户
```bash
# 安装依赖
sudo apt install -y git zip unzip openjdk-17-jdk autoconf libtool
pip3 install buildozer cython

# 构建
buildozer android debug
```

## 📱 测试

### 安装APK
```bash
# 真机
adb install bin/wangzheautoclicker-3.0.0-debug.apk

# 模拟器
adb -s 127.0.0.1:21503 install bin/wangzheautoclicker-3.0.0-debug.apk
```

### 启动应用
```bash
adb shell am start -n org.wangzhe.wangzheautoclicker/org.kivy.android.PythonActivity
```

### 查看日志
```bash
adb logcat | grep -i python
```

## 🎯 架构选择

编辑 `buildozer.spec` 第79行：

```ini
# ARM真机（推荐）
android.archs = armeabi-v7a, arm64-v8a

# x86模拟器
android.archs = x86, x86_64

# 全架构（最大兼容，但APK较大）
android.archs = armeabi-v7a, arm64-v8a, x86, x86_64
```

## 📊 功能对比

| 功能 | v1.0 | v2.0 | v3.0 |
|------|------|------|------|
| 启动稳定性 | ❌ 崩溃 | ⚠️ 部分修复 | ✅ 完全修复 |
| 分辨率适配 | ❌ 固定720p | ⚠️ 手动 | ✅ 自动 |
| 模拟器支持 | ❌ 不支持 | ❌ 不支持 | ✅ 支持 |
| 横屏模式 | ❌ 闪退 | ⚠️ 临时修复 | ✅ 完全支持 |
| 设备检测 | ❌ 无 | ❌ 无 | ✅ 完整 |
| 架构支持 | ARM only | ARM only | ARM + x86 |
| 代码质量 | ⚠️ 一般 | ⚠️ 一般 | ✅ 优秀 |

## 🔍 核心模块

### 1. ResolutionAdapter - 分辨率适配器
```python
from scripts.resolution_adapter import ResolutionAdapter

adapter = ResolutionAdapter()
adapter.detect_resolution()  # 自动检测
x, y = adapter.adapt_coordinate(640, 360)  # 坐标适配
```

### 2. DeviceDetector - 设备检测器
```python
from scripts.device_detector import DeviceDetector

detector = DeviceDetector()
devices = detector.get_connected_devices()
compat = detector.check_compatibility()
```

### 3. FloatWindowManager - 悬浮窗管理器
```python
from scripts.float_window_manager import FloatWindowManager

manager = FloatWindowManager.get_instance()
manager.add_float_window(window)
manager.handle_orientation_change('landscape')
```

### 4. EnhancedAutoClicker - 增强版核心
```python
from scripts.enhanced_auto_clicker import EnhancedAutoClicker

clicker = EnhancedAutoClicker(config_path='config.json')
clicker.start(script_name='default', max_loops=10)
```

## 🐛 常见问题

### Q1: 构建失败？
```bash
# 清理缓存
buildozer android clean
buildozer android debug
```

### Q2: APK安装失败？
检查架构是否匹配：
```bash
# 真机架构
adb shell getprop ro.product.cpu.abi

# 模拟器架构
adb -s 127.0.0.1:21503 shell getprop ro.product.cpu.abi
```

### Q3: 分辨率检测不准确？
手动设置：
```python
adapter.current_width = 1080
adapter.current_height = 2340
adapter.update_device_info()
```

### Q4: 横屏还是闪退？
检查配置：
```ini
# buildozer.spec
android.manifest_activity_attributes = android:configChanges="orientation|screenSize|keyboardHidden"
orientation = portrait  # 或 landscape
```

## 📝 更新日志

### v3.0.0 (2026-03-30)
- ✅ 完全重构项目架构
- ✅ 修复启动崩溃问题
- ✅ 添加分辨率自动适配
- ✅ 添加模拟器支持（x86/x86_64）
- ✅ 修复横屏闪退问题
- ✅ 添加设备检测和兼容性检查
- ✅ 优化代码结构和文档

## 📄 许可

MIT License - 仅供学习研究使用

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**版本**: v3.0.0
**日期**: 2026-03-30
**状态**: ✅ 生产就绪
