[app]

# App info
title = WangZheAutoClicker
package.name = wangzheautoclicker
package.domain = org.wangzhe

# Source
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt

# Exclude directories
source.exclude_dirs = scripts,templates,configs

# Version
version = 3.0.6

# Dependencies - Include Pyjnius for Android API
requirements = python3,kivy,pyjnius

# Screen orientation
orientation = landscape

# Fullscreen
fullscreen = 0

# Android permissions
android.permissions = INTERNET

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
