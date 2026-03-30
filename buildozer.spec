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
version = 3.1.0

# Dependencies - Include OpenCV for image recognition
requirements = python3,kivy,pyjnius,opencv,numpy

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
