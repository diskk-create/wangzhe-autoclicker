[app]

# 应用信息
title = WangZheAutoClicker
package.name = wangzheautoclicker
package.domain = org.wangzhe

# 源代码
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt

# 版本
version = 3.0.0

# 依赖（不包含OpenCV，确保构建成功）
requirements = python3,kivy,pyjnius

# 屏幕方向
orientation = portrait
fullscreen = 0

# Android权限
android.permissions = SYSTEM_ALERT_WINDOW,BIND_ACCESSIBILITY_SERVICE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# Android API
android.api = 31
android.minapi = 21

# SDK设置
android.skip_update = False
android.accept_sdk_license = True

# 架构（支持ARM和x86）
android.archs = armeabi-v7a,arm64-v8a,x86,x86_64

[buildozer]

# 日志级别
log_level = 2

# 警告root用户
warn_on_root = 1
