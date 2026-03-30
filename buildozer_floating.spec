[app]

# (str) Title of your application
title = WangZhe Floating Ball

# (str) Package name
package.name = wangzhefloat

# (str) Package domain (needed for android/ios packaging)
package.domain = org.wangzhe

# (str) Source code where the main.py live
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt

# (List) Source files to include (let empty to include all the files)
source.include_patterns = main_floating.py

# (str) Application versioning
version = 4.0.0

# (list) Application requirements
requirements = python3,kivy,pyjnius

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (landscape, portrait or all)
orientation = all

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,SYSTEM_ALERT_WINDOW,ACCESSIBILITY_SERVICES

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 24

# (int) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = False

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = armeabi-v7a, arm64-v8a

# (str) python-for-android branch to use (master, develop, or specific tag)
#p4a.branch = master

# (str) Entry point, default is main.py
android.entrypoint = main_floating.py

# (str) Application theme
#android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Intent filters for the main activity
#android.intent_filters = 

# (str) Additional file to copy into the assets
#android.add_assets =

# (list) Copy libs instead of making a new archive
#android.copy_libs = 1

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
