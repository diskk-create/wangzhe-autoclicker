[app]

# 应用信息
title = WangZheAutoClicker
package.name = wangzheautoclicker
package.domain = org.wangzhe

# 源代码
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt

# 排除scripts目录（避免依赖问题）
source.exclude_dirs = scripts,templates,configs

# 版本
version = 3.0.1

# 依赖（简化版本，不依赖android模块）
requirements = python3,kivy

# 屏幕方向
orientation = landscape

# 全屏
fullscreen = 0

# Android权限
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android API
android.api = 33
android.minapi = 24
android.ndk = 25b

# 架构
android.archs = arm64-v8a,armeabi-v7a

# 接受许可证
android.accept_sdk_license = True

[buildozer]

# 日志级别
log_level = 2

# 警告root用户
warn_on_root = 1
