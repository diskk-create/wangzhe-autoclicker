# WangZhe Auto Clicker - Android原生版本

## 项目概述

这是一个使用Kotlin编写的Android原生应用，实现了**真正的悬浮窗**功能。

## 功能特性

### ✅ 核心功能
- **悬浮窗**: 真正的Android悬浮窗，可以在任何应用上显示
- **可拖动**: 悬浮球可以自由拖动
- **菜单展开**: 点击悬浮球展开操作菜单
- **后台运行**: 使用前台服务保持后台运行
- **自动点击**: 支持ROOT和无障碍服务两种模式

### 🎯 悬浮窗特性
- 使用WindowManager实现
- TYPE_APPLICATION_OVERLAY类型（Android 8.0+）
- 支持拖动和点击
- 通知栏常驻

### 🔐 权限要求
- `SYSTEM_ALERT_WINDOW` - 悬浮窗权限
- `FOREGROUND_SERVICE` - 前台服务权限
- `BIND_ACCESSIBILITY_SERVICE` - 无障碍服务（可选，用于非ROOT设备）

## 技术栈

- **语言**: Kotlin
- **最低版本**: Android 7.0 (API 24)
- **目标版本**: Android 14 (API 34)
- **构建工具**: Gradle 8.2.0

## 项目结构

```
wangzhe-autoclicker-native/
├── app/
│   ├── src/main/
│   │   ├── java/com/wangzhe/autoclicker/
│   │   │   ├── MainActivity.kt              # 主Activity
│   │   │   ├── FloatingWindowService.kt     # 悬浮窗服务
│   │   │   └── AccessibilityService.kt      # 无障碍服务
│   │   ├── res/
│   │   │   ├── layout/
│   │   │   │   ├── activity_main.xml        # 主布局
│   │   │   │   └── floating_window.xml      # 悬浮窗布局
│   │   │   ├── drawable/
│   │   │   │   ├── floating_ball_bg.xml     # 悬浮球背景
│   │   │   │   ├── menu_bg.xml              # 菜单背景
│   │   │   │   └── btn_*.xml                # 按钮样式
│   │   │   └── values/
│   │   │       ├── strings.xml              # 字符串
│   │   │       └── themes.xml               # 主题
│   │   └── AndroidManifest.xml              # 清单文件
│   └── build.gradle                         # 应用构建配置
├── build.gradle                             # 项目构建配置
├── settings.gradle                          # 项目设置
└── gradle.properties                        # Gradle属性
```

## 如何构建

### 方法1：使用Android Studio

1. 打开Android Studio
2. 选择 `Open an Existing Project`
3. 选择 `wangzhe-autoclicker-native` 目录
4. 等待Gradle同步完成
5. 点击 `Build > Build APK(s)`
6. APK位置: `app/build/outputs/apk/debug/app-debug.apk`

### 方法2：使用命令行

```bash
# Windows
gradlew.bat assembleDebug

# Linux/macOS
./gradlew assembleDebug
```

APK位置: `app/build/outputs/apk/debug/app-debug.apk`

## 如何安装

### 方法1：通过ADB安装

```bash
adb install app-debug.apk
```

### 方法2：通过文件管理器

将APK复制到手机，点击安装。

## 使用说明

### 1. 授予悬浮窗权限

首次启动应用时，会提示授予悬浮窗权限：

1. 点击"授予悬浮窗权限"
2. 找到"WangZhe Auto Clicker"
3. 开启权限

### 2. 启动悬浮窗

授予权限后，应用会自动启动悬浮窗服务：

- 屏幕上会出现一个蓝色悬浮球
- 点击悬浮球展开操作菜单
- 拖动悬浮球可以移动位置

### 3. 使用功能

#### Start - 开始自动点击
- 开始执行预设的点击流程
- 循环运行直到点击Stop

#### Stop - 停止自动点击
- 停止当前运行的点击流程

#### Test - 测试点击
- 执行一次测试点击（屏幕中心）

#### Close - 收起菜单
- 收起菜单，只显示悬浮球

#### Exit - 退出应用
- 停止所有操作并退出

## 自定义点击坐标

编辑 `FloatingWindowService.kt` 中的 `clickCoordinates` 列表：

```kotlin
private val clickCoordinates = listOf(
    Pair(100, 200),   // 步骤1: 点击(100, 200)
    Pair(200, 300),   // 步骤2: 点击(200, 300)
    Pair(300, 400),   // 步骤3: 点击(300, 400)
    // 添加更多坐标...
)
```

## ROOT vs 无障碍服务

### ROOT模式
- 需要设备已ROOT
- 执行速度更快
- 更稳定

### 无障碍服务模式
- 不需要ROOT
- 需要手动开启无障碍服务
- Android 7.0+支持

开启无障碍服务：
1. 设置 > 无障碍 > WangZhe Auto Clicker
2. 开启服务

## 注意事项

1. **Android 10+**: 需要授予"在其他应用上层显示"权限
2. **后台限制**: 部分厂商ROM可能限制后台服务，请添加到白名单
3. **省电模式**: 请将应用加入省电白名单

## 常见问题

### Q: 悬浮球不显示？
A: 检查是否授予了悬浮窗权限。

### Q: 点击无反应？
A: 
- ROOT设备：检查是否授予了ROOT权限
- 非ROOT设备：检查是否开启了无障碍服务

### Q: 应用自动关闭？
A: 
- 检查是否在省电白名单中
- 检查是否有后台限制

## 版本历史

### v1.0.0 (2026-03-31)
- ✅ 首次发布
- ✅ 真正的悬浮窗
- ✅ 可拖动悬浮球
- ✅ 自动点击功能
- ✅ ROOT和无障碍服务双模式
- ✅ 前台服务保持后台运行

## 下一步开发

- [ ] 添加图形化坐标编辑器
- [ ] 添加循环次数设置
- [ ] 添加延迟时间设置
- [ ] 添加点击日志
- [ ] 添加截图识别功能

## 许可证

MIT License

## 作者

diskk-create
Email: 577112825@qq.com
GitHub: https://github.com/diskk-create
