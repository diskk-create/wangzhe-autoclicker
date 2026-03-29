[app]

# (str) Title of your application
title = 王者荣耀自动点击器

# (str) Package name
package.name = wangzheautoclicker

# (str) Package domain (needed for android/ios packaging)
package.domain = org.wangzhe

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,txt

# (list) List of inclusions using pattern matching
source.include_patterns = templates/*,configs/*,assets/*

# (str) Application versioning
version = 2.0.0

# (list) Application requirements
# opencv 使用 buildozer 的 recipe 编译
requirements = python3,kivy,pyjnius,android,opencv,numpy,pillow

# (list) Supported orientations (landscape, sensorLandscape, portrait or all)
orientation = landscape

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = VIBRATE,INTERNET,WAKE_LOCK,SYSTEM_ALERT_WINDOW,BIND_ACCESSIBILITY_SERVICE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,FOREGROUND_SERVICE,CAMERA

# (int) Target Android API
android.api = 33

# (int) Minimum API
android.minapi = 24

# (str) Android NDK version
android.ndk = 25b

# (bool) Accept SDK license
android.accept_sdk_license = True

# (str) Android archs
android.archs = arm64-v8a, armeabi-v7a

# (bool) Enable Android backup
android.allow_backup = True

# (str) Presplash (loading screen) image
#presplash.filename = %(source.dir)s/assets/presplash.png

# (str) Application icon
#icon.filename = %(source.dir)s/assets/icon.png

[buildozer]

# (int) Log level
log_level = 2

# (int) Warn on root
warn_on_root = 1
