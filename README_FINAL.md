# 🎮 王者荣耀自动点击器 Android原生版 v1.0.0

## ✅ 已完成功能

### 核心功能
1. **真正的Android悬浮窗** - 使用`TYPE_APPLICATION_OVERLAY`，可在任何应用上方显示
2. **完整的11步王者荣耀自动化** - 基于1280x720分辨率的坐标
3. **智能点击策略** - 找图 > 找字 > 坐标点击（优先级递减）
4. **三层点击实现** - ROOT优先、无障碍服务备用、ADB调试兜底
5. **实时状态显示** - 状态、步骤、日志实时更新
6. **可拖动悬浮球** + 展开式控制菜单
7. **前台服务** - 保证后台不被系统杀死
8. **图像识别框架** - 预留OpenCV接口

### 技术栈
- **语言**: Kotlin
- **框架**: Android原生开发
- **目标API**: 24+ (Android 7.0+)
- **架构**: Service + Floating Window + Image Recognition

## 📱 使用步骤

### 1. 构建APK
```bash
cd wangzhe_autoclicker_native
.\build.bat
```

### 2. 安装到设备
```bash
.\install.bat
# 或手动安装
adb install app\build\outputs\apk\debug\app-debug.apk
```

### 3. 使用步骤
1. **启动应用** - 授予悬浮窗权限
2. **悬浮球出现** - 在屏幕左上角
3. **点击悬浮球** - 展开控制菜单
4. **测试功能** - 点击"🔄 Test"测试点击
5. **测试图像识别** - 点击"🖼️ Test Image"
6. **开始自动点击** - 点击"▶ Start"开始11步流程
7. **停止** - 点击"⏹ Stop"停止

## 🎯 王者荣耀11步流程

| 步骤 | 名称 | 坐标(1280x720) | 延迟 | 识别策略 |
|------|------|----------------|------|----------|
| 1 | 登录 | (641, 564) | 3秒 | 找图(login_button) > 坐标 |
| 2 | 关闭弹窗 | (1190, 112) | 2秒 | 找图(close_popup) > 坐标 |
| 3 | 游戏大厅 | (514, 544) | 2秒 | 找图(game_hall) > 坐标 |
| 4 | 王者峡谷匹配 | (398, 539) | 2秒 | 找图(match_arena) > 坐标 |
| 5 | 人机模式 | (730, 601) | 2秒 | 找图(ai_mode) > 坐标 |
| 6 | 开始游戏 | (1057, 569) | 3秒 | 找图(start_game) > 找字("开始游戏") > 坐标 |
| 7 | 准备游戏 | (775, 660) | 2秒 | 找图(ready_game) > 找字("准备") > 坐标 |
| 8 | 准备进入 | (640, 561) | 10秒 | 找图(enter_game) > 找字("确认") > 坐标 |
| 9 | 游戏中 | (640, 360) | 60秒 | 找图(in_game) > 坐标 |
| 10 | 游戏结束 | (635, 664) | 2秒 | 找图(game_over) > 找字("返回房间") > 坐标 |
| 11 | 结算英雄 | (645, 621) | 2秒 | 找图(settlement) > 坐标 |

## 🔧 技术实现

### 悬浮窗核心
```kotlin
val params = WindowManager.LayoutParams(
    WindowManager.LayoutParams.WRAP_CONTENT,
    WindowManager.LayoutParams.WRAP_CONTENT,
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
        WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY  // Android 8.0+
    } else {
        WindowManager.LayoutParams.TYPE_PHONE                 // Android 7.0+
    },
    WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
    WindowManager.LayoutParams.FLAG_WATCH_OUTSIDE_TOUCH or
    WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
    PixelFormat.TRANSLUCENT
)
```

### 智能点击策略
```kotlin
fun performSmartClick(index: Int): Boolean {
    // 1. 先尝试找图
    val imageResult = imageRecognizer.findImage(templateName)
    if (imageResult.success && imageResult.confidence >= 90) {
        return performClick(imageResult.x, imageResult.y, "找图")
    }
    
    // 2. 尝试找字
    val textResult = imageRecognizer.findText(textTemplate)
    if (textResult.success && textResult.confidence >= 90) {
        return performClick(textResult.x, textResult.y, "找字")
    }
    
    // 3. 兜底：使用固定坐标
    return performClick(fallbackCoordinate.first, fallbackCoordinate.second, "坐标点击")
}
```

### 点击方法（三层保障）
```kotlin
private fun performClick(x: Int, y: Int, source: String): Boolean {
    // 方法1: ROOT权限优先
    if (performRootClick(scaledX, scaledY)) {
        return true
    }
    
    // 方法2: 无障碍服务备用
    if (performAccessibilityClick(scaledX, scaledY)) {
        return true
    }
    
    // 方法3: ADB调试兜底
    if (performAdbClick(scaledX, scaledY)) {
        return true
    }
    
    return false
}
```

## 📁 项目结构

```
wangzhe_autoclicker_native/
├── app/
│   ├── src/main/java/com/wangzhe/autoclicker/
│   │   ├── FloatingWindowService.kt    # 主悬浮窗服务 (567行)
│   │   ├── ImageRecognizer.kt          # 图像识别框架 (348行)
│   │   ├── AccessibilityService.kt     # 无障碍服务 (65行)
│   │   └── MainActivity.kt             # 主Activity (54行)
│   ├── src/main/res/layout/
│   │   ├── floating_window.xml         # 悬浮窗布局
│   │   └── activity_main.xml           # 主界面
│   └── build.gradle                    # 构建配置
├── build.bat                           # 构建脚本
├── install.bat                         # 安装脚本
├── README_updated.md                   # 详细说明
├── BUILD_WITH_OPENCV.md                # OpenCV集成指南
└── gradlew.bat                         # Gradle wrapper
```

## 🔄 图像识别框架

### 当前状态：模拟版本
- **找图**: 基于颜色匹配的模拟识别（置信度90%+）
- **找字**: 基于文字模板的模拟识别（置信度90%+）
- **智能策略**: 找图失败则找字，都失败则使用坐标

### 升级到真实OpenCV版本
参考`BUILD_WITH_OPENCV.md`，需要：
1. 集成OpenCV Android SDK
2. 实现真正的模板匹配
3. 集成Tesseract OCR文字识别
4. 优化性能

## ⚙️ 权限要求

### 必需权限
```xml
<!-- 悬浮窗权限 -->
<uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />

<!-- 前台服务权限 -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
```

### 可选权限
```xml
<!-- 无障碍服务（无ROOT时使用） -->
<uses-permission android:name="android.permission.BIND_ACCESSIBILITY_SERVICE" />

<!-- 屏幕截图（图像识别需要） -->
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

## 🚀 快速开始

### 第一次使用
```bash
# 1. 构建APK
.\build.bat

# 2. 安装到设备
.\install.bat

# 3. 授予权限
#    - 在其他应用上层显示
#    - 无障碍服务（可选）
#    - 存储权限（图像识别需要）
```

### 测试流程
1. 启动王者荣耀游戏
2. 确保游戏窗口为1280x720分辨率
3. 启动悬浮窗服务
4. 点击悬浮球展开菜单
5. 点击"Test"按钮测试点击功能
6. 点击"Start"开始自动11步
7. 观察日志输出

## 📊 日志说明

```
[时间戳] [来源] 点击坐标: (x, y)
[时间戳] [找图] 找到登录按钮, 置信度: 95%
[时间戳] [找字] 找到文字"开始游戏", 置信度: 92%
[时间戳] [坐标点击] 使用兜底坐标
[时间戳] [状态] 正在执行: 登录
[时间戳] [状态] 步骤1完成: 登录
```

## 🐛 故障排除

### 悬浮窗不显示
1. 检查是否授予"在其他应用上层显示"权限
2. 重启应用
3. 检查Android版本（需要7.0+）

### 点击无效
1. 有ROOT权限：自动使用ROOT点击
2. 无ROOT权限：需要开启无障碍服务
3. 调试模式：确保ADB调试已开启

### 坐标不准
1. 确保游戏分辨率1280x720
2. 不同分辨率需要修改坐标
3. 后续版本会添加分辨率自动适配

## 🔮 后续开发计划

### 高优先级
1. **分辨率自动适配** - 自动计算不同屏幕的坐标
2. **图像识别增强** - 集成OpenCV真实识别
3. **文字识别增强** - 集成Tesseract OCR
4. **配置界面** - 图形化坐标配置

### 中优先级
1. **脚本录制** - 录制点击坐标生成脚本
2. **多分辨率模板** - 支持多种分辨率
3. **云配置同步** - 同步配置到云端
4. **高级脚本编辑** - 复杂的脚本逻辑

### 低优先级
1. **AI识别** - 使用AI识别游戏状态
2. **智能策略** - 根据游戏状态自动调整
3. **多游戏支持** - 扩展到其他游戏
4. **社区功能** - 共享脚本和配置

## 📞 技术支持

### GitHub仓库
https://github.com/diskk-create/wangzhe-autoclicker

### 问题反馈
1. 查看日志输出
2. 检查权限设置
3. 确认游戏分辨率
4. 在GitHub提交Issue

### 联系方式
- **GitHub**: diskk-create
- **邮箱**: 577112825@qq.com

## 📄 许可证

MIT License - 详见LICENSE文件

## ⭐ 更新日志

### v1.0.0 (2026-03-31)
- ✅ 实现真正的Android原生悬浮窗
- ✅ 完整的11步王者荣耀自动点击
- ✅ 智能点击策略（找图>找字>坐标）
- ✅ 三层点击实现（ROOT+无障碍+ADB）
- ✅ 实时状态和日志显示
- ✅ 图像识别框架（模拟版）
- ✅ 可拖动悬浮球+控制菜单
- ✅ 前台服务保证后台运行

---

**项目状态**: ✅ 基础功能完成，可立即测试使用  
**预计测试时间**: 10-15分钟构建和初步验证  
**下一步**: 集成OpenCV实现真正的图像识别