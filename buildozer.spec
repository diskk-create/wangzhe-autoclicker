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

# 依赖（最小化）
requirements = python3,kivy

# 屏幕方向
orientation = portrait

# Android API（使用稳定版本）
android.api = 27
android.minapi = 21
android.ndk = 19b

# 架构（只构建ARM）
android.archs = armeabi-v7a

# 接受许可证
android.accept_sdk_license = True

[buildozer]

# 日志级别
log_level = 2
