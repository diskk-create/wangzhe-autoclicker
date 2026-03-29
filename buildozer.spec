[app]

# 应用信息
title = WangZheAutoClicker
package.name = wangzheautoclicker
package.domain = org.wangzhe

# 源代码（只包含main.py和assets）
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt
source.exclude_dirs = scripts,tests,docs

# 版本
version = 3.0.0

# 依赖
requirements = python3,kivy

# 屏幕方向
orientation = portrait
fullscreen = 0

# Android权限
android.permissions = SYSTEM_ALERT_WINDOW

# Android API
android.api = 31
android.minapi = 21

# SDK设置
android.skip_update = False
android.accept_sdk_license = True

# 架构
android.archs = armeabi-v7a,arm64-v8a

[buildozer]

# 日志级别
log_level = 2

# 警告root用户
warn_on_root = 1
