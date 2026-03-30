[app]

# App info
title = WangZheAutoClicker
package.name = wangzheautoclicker
package.domain = org.wangzhe

# Source
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt

# Include templates directory
source.include_dirs = templates

# Version
version = 3.3.2

# Dependencies - Include OpenCV for image recognition
requirements = python3,kivy,pyjnius,opencv,numpy

# Screen orientation
orientation = landscape

# Fullscreen
fullscreen = 0

# Android permissions - 需要的权限
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,SYSTEM_ALERT_WINDOW,ACCESSIBILITY_SERVICES

# Android API
android.api = 33
android.minapi = 24
android.ndk = 25b

# Architectures
android.archs = arm64-v8a,armeabi-v7a

# Accept license
android.accept_sdk_license = True

# Allow backup
android.allow_backup = True

[buildozer]

# Log level
log_level = 2

# Warn on root
warn_on_root = 1
