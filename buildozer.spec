[app]

# 应用信息
title = 王者荣耀自动点击器
package.name = wangzheautoclicker
package.domain = org.wangzhe

# 源代码
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt

# 版本
version = 3.0.0

# 依赖（精简版，移除opencv和numpy）
requirements = python3,kivy,pyjnius

# 屏幕方向（固定竖屏）
orientation = portrait
fullscreen = 0

# Android权限
android.permissions = SYSTEM_ALERT_WINDOW,BIND_ACCESSIBILITY_SERVICE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# Android API
android.api = 33
android.minapi = 24
android.ndk = 25b

# SDK设置
android.skip_update = False
android.accept_sdk_license = True

# 关键配置：防止Activity重建
android.manifest_activity_attributes = android:configChanges="orientation|screenSize|keyboardHidden"

# 多架构支持（ARM + x86）
android.archs = armeabi-v7a,arm64-v8a,x86,x86_64

# 允许备份
android.allow_backup = True

# 日志过滤
android.logcat_filters = *:S python:D

[buildozer]

# 日志级别
log_level = 2

# 警告root用户
warn_on_root = 1
