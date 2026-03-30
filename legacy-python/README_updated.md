# 王者荣耀自动点击器 Android原生版 - 修复报告

## ✅ 已完成修复的问题

### 1. **补全了11步王者荣耀坐标**
- 完整添加了11个步骤的实际游戏坐标
- 基于1280x720分辨率（后续需要添加分辨率适配）
- 每个步骤都有适当的延迟时间

### 2. **增强了点击功能**
- **ROOT点击优先**：使用 `su -c input tap x y`
- **无障碍服务备用**：无ROOT时使用无障碍服务
- **普通ADB点击兜底**：调试模式时可用

### 3. **添加了完整的状态显示**
- 状态指示器：Ready / Running / Stopped
- 当前步骤显示：显示正在执行的步骤名称
- 日志区域：显示详细的点击日志和状态

### 4. **优化了循环逻辑**
- 每步之间使用预设延迟时间
- 登录：3秒，游戏中：60秒等
- 一轮结束后等待2秒重新开始

### 5. **增强的用户界面**
- 悬浮球可拖动
- 点击展开菜单面板
- 完整的控制按钮：Start / Stop / Test / Close / Exit
- 实时状态显示

## 📱 使用流程

### 1. **构建APK**
```bash
cd wangzhe_autoclicker_native
build.bat
```

### 2. **安装到设备**
```bash
install.bat
```
或手动安装：
```bash
adb install app-debug.apk
```

### 3. **使用步骤**
1. 打开应用 → 自动请求悬浮窗权限
2. 授予"在其他应用上层显示"权限
3. 悬浮球出现在屏幕上
4. 点击悬浮球展开菜单
5. 点击"Test"按钮测试点击功能
6. 点击"Start"开始自动点击（11步循环）
7. 点击"Stop"停止点击
8. 点击"Close"收起菜单
9. 点击"Exit"退出应用

## 🔧 文件结构说明

```
wangzhe_autoclicker_native/
├── app/src/main/java/com/wangzhe/autoclicker/
│   ├── MainActivity.kt              # 主Activity（权限检查）
│   ├── FloatingWindowService.kt     # 悬浮窗服务（核心文件）⭐已修复
│   └── AccessibilityService.kt      # 无障碍服务（点击实现）
├── app/src/main/res/layout/
│   ├── activity_main.xml            # 主界面布局（仅权限检查）
│   └── floating_window.xml          # 悬浮窗布局 ⭐已增强
├── app/src/main/AndroidManifest.xml # 权限配置
├── build.bat                        # 构建脚本
└── install.bat                      # 安装脚本
```

## 🎮 王者荣耀11步坐标

| 步骤 | 名称 | 坐标(1280x720) | 延迟 | 说明 |
|------|------|----------------|------|------|
| 1 | 登录 | (641, 564) | 3秒 | 点击"开始游戏" |
| 2 | 关闭弹窗 | (1190, 112) | 2秒 | 关闭活动弹窗 |
| 3 | 游戏大厅 | (514, 544) | 2秒 | 点击"对战" |
| 4 | 王者峡谷匹配 | (398, 539) | 2秒 | 点击"王者峡谷" |
| 5 | 人机模式 | (730, 601) | 2秒 | 选择"人机" |
| 6 | 开始游戏 | (1057, 569) | 3秒 | 点击"开始" |
| 7 | 准备游戏 | (775, 660) | 2秒 | 点击"准备" |
| 8 | 准备进入 | (640, 561) | 10秒 | 确认进入游戏 |
| 9 | 游戏中 | (640, 360) | 60秒 | 等待游戏结束 |
| 10 | 游戏结束 | (635, 664) | 2秒 | 确认结束 |
| 11 | 结算英雄 | (645, 621) | 2秒 | 查看结算 |

**注意**：第12步"返回房间"(739, 651)未包含，因为游戏可能自动返回

## ⚙️ 技术实现细节

### 1. **悬浮窗核心代码**
```kotlin
val params = WindowManager.LayoutParams(
    WindowManager.LayoutParams.WRAP_CONTENT,
    WindowManager.LayoutParams.WRAP_CONTENT,
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
        WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY  // Android 8.0+
    } else {
        WindowManager.LayoutParams.TYPE_PHONE                 // 旧版本
    },
    WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
    WindowManager.LayoutParams.FLAG_WATCH_OUTSIDE_TOUCH or
    WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
    PixelFormat.TRANSLUCENT
)
```

### 2. **点击执行策略**
```kotlin
// 1. 优先使用ROOT权限
val process = Runtime.getRuntime().exec(arrayOf("su", "-c", "input tap $x $y"))

// 2. 备用无障碍服务
AccessibilityService.performClick(x, y)

// 3. 兜底ADB调试模式
val process = Runtime.getRuntime().exec("input tap $x $y")
```

### 3. **权限要求**
- 悬浮窗权限：`SYSTEM_ALERT_WINDOW`
- 前台服务权限：`FOREGROUND_SERVICE`
- 无障碍服务权限（可选）：`BIND_ACCESSIBILITY_SERVICE`
- ROOT权限（可选，推荐）

## 🚀 下一步计划

### 高优先级
1. **添加分辨率适配** - 自动适配不同屏幕尺寸
2. **添加配置界面** - 允许修改坐标和延迟
3. **增强错误处理** - 更好的权限提示和错误恢复

### 中等优先级
1. **图像识别集成** - 添加OpenCV找图功能
2. **文字识别集成** - 添加Tesseract找字功能
3. **脚本录制功能** - 录制点击坐标生成脚本

### 低优先级
1. **多分辨率模板** - 支持多种分辨率模板
2. **云配置同步** - 同步配置到云端
3. **高级脚本编辑** - 复杂的脚本逻辑

## 🔍 调试技巧

### 查看悬浮窗层级
```bash
adb shell dumpsys window windows | grep -A 10 "WangZhe"
```

### 查看应用权限
```bash
adb shell dumpsys package com.wangzhe.autoclicker | grep permission
```

### 实时日志
```bash
adb logcat -s WangZheAutoClicker:V
```

### 安装应用
```bash
adb install app-debug.apk
```

### 卸载应用
```bash
adb uninstall com.wangzhe.autoclicker
```

## 📝 注意事项

### 1. **悬浮窗权限**
第一次启动需要手动授予悬浮窗权限：
- 设置 → 应用 → WangZhe Auto Clicker → 权限
- 开启"在其他应用上层显示"

### 2. **ROOT权限**
如果设备已ROOT：
- 应用会自动检测并使用ROOT权限
- 点击成功率最高

### 3. **无障碍服务**
如果没有ROOT：
- 需要手动开启无障碍服务
- 设置 → 无障碍 → WangZhe Auto Clicker → 开启

### 4. **游戏窗口模式**
- 确保游戏以**1280x720**分辨率运行
- 不同分辨率需要调整坐标或添加分辨率适配

## 🎯 测试建议

### 1. **基础功能测试**
- [x] 应用安装
- [x] 悬浮窗权限授予
- [x] 悬浮球显示
- [x] 菜单展开/收起
- [x] Test按钮点击测试

### 2. **点击功能测试**
- [ ] ROOT点击测试（如有ROOT）
- [ ] 无障碍点击测试（如无ROOT）
- [ ] Test按钮是否能正常点击屏幕中心

### 3. **完整流程测试**
- [ ] Start按钮开始自动点击
- [ ] 观察11步坐标执行
- [ ] Stop按钮停止
- [ ] 检查日志输出

### 4. **王者荣耀测试**
- [ ] 游戏以1280x720分辨率运行
- [ ] 启动自动点击器
- [ ] 观察是否能正常完成11步
- [ ] 检查是否卡在任何步骤

## 📞 技术支持

### 常见问题解决
1. **悬浮窗不显示** → 检查悬浮窗权限
2. **点击无效** → 检查ROOT或无障服服务
3. **坐标不准** → 确保游戏分辨率1280x720
4. **应用被杀** → 添加到白名单，关闭省电优化

### 联系信息
- **GitHub**: https://github.com/diskk-create/wangzhe-autoclicker
- **开发者**: diskk-create
- **邮箱**: 577112825@qq.com

---

**更新日期**: 2026-03-31  
**版本**: v1.1.0 (坐标完善版)  
**状态**: ✅ 基础功能可用，等待测试验证