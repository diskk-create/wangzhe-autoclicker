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
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
# Do not prefix with './'
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning
version = 3.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,pyjnius,android,opencv,numpy

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
# Valid options are: landscape, portrait or portrait-reverse or landscape-reverse
# 固定竖屏模式，避免横屏闪退
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# 悬浮窗和无障碍服务权限
android.permissions = SYSTEM_ALERT_WINDOW,BIND_ACCESSIBILITY_SERVICE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 24

# (int) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
#android.activity_class_name = org.kivy.android.PythonActivity

# (str) Extra xml to write directly inside the <manifest> element of AndroidManifest.xml
# use that parameter to provide a filename from where to load your custom XML code
#android.manifest_entries = src/manifest.xml

# (str) Extra xml to write directly inside the <manifest> element of AndroidManifest.xml
# android.manifest_placeholders = [manifest_entries]

# (str) Extra xml to write directly inside the <application> element of AndroidManifest.xml
# use that parameter to provide a filename from where to load your custom XML code
#android.extra_manifest_application_xml = src/extra_manifest_application.xml

# (str) Extra xml to write directly inside the <activity> element of AndroidManifest.xml
# use that parameter to provide a filename from where to load your custom XML code
#android.extra_manifest_activity_xml = src/extra_manifest_activity.xml

# (str) Extra attributes for the <activity> tag in AndroidManifest.xml
# 修复横屏闪退：防止Activity在配置变化时重建
android.manifest_activity_attributes = android:configChanges="orientation|screenSize|keyboardHidden"

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# 支持多架构：ARM真机 + x86模拟器
android.archs = armeabi-v7a, arm64-v8a, x86, x86_64

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) The Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Android 主题，使用Material Design
android.widget_style=android:Theme.Material.Light.NoActionBar

# (str) Android 白名单，允许一些库
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching, for example:
# OUYA-ODK/libs/*.jar
#android.add_jars = foo.jar,bar.jar,path/to/mors/*.jar

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
#android.add_src =

# (list) Android AAR archives to add (currently builds only AAR)
#android.add_aars =

# (list) Put these files or directories in the apk assets directory.
# Either form may be used, and assets need not be in your source directory.
#android.add_assets = assets/

# (list) Put these files or directories in the apk res directory.
# The option can be used to rename a file or directory, or to add files from
# a different location.  For example: res/mipmap-*/*->res/drawable-*/*
#android.add_res =

# (list) Gradle dependencies to add (currently works only with sdl2 bootstrap)
#android.gradle_dependencies =

# (list) Gradle repositories to add (currently works only with sdl2 bootstrap)
#android.gradle_repositories =

# (list) Java class path for annotation processors (currently works only with sdl2 bootstrap)
#android.processor_class_path =

# (list) Java annotation processors (currently works only with sdl2 bootstrap)
#android.annotation_processors =

# (str) Android additional libraries to copy
#android.add_libs_armeabi =
#android.add_libs_armeabi_v7a =
#android.add_libs_arm64_v8a =
#android.add_libs_x86 =
#android.add_libs_x86_64 =

# (bool) enables Android broadcast receiver
#android.broadcast_receivers =

# (str) Override the default launch mode
#android.launch_mode = singleTop

# (str) Override the default launch mode for the activity used to handle intents
#android.launch_mode_intent = singleTop

# (str) Override the default intent filters
#android.intent_filters =

# (str) Override the default meta-data
#android.meta_data =

# (str) Override the default meta-data for the activity used to handle intents
#android.meta_data_intent =

# (str) Specifies the parameters of a notification used by the application
#android.notification =

# (str) The Android additional files to pack using a particular pattern
#android.add_src_pattern =

# (str) The Android additional native libraries to pack
#android.add_native_libs =

# (bool) If True, then automatically copy the source files to the application directory
#android.copy_libs = 1

# (str) The Android attribute to the activity tag
#android.activity_attributes =

# (str) The XML string to add as a child of the application tag
#android.application_attributes =

# (str) The XML string to add as a child of the service tag
#android.service_attributes =

# (str) The XML string to add as a child of the activity tag
#android.activity_intent_filters =

# (str) The name for the application service
#android.service_name =

# (str) The name for the application alias
#android.alias_name =

# (str) The label for the application alias
#android.alias_label =

# (str) The icon for the application alias
#android.alias_icon =

# (list) The Android Services to add
#android.services =

# (list) The Android Receivers to add
#android.receivers =

# (str) The name of the application class
#android.application_class =

# (bool) If True, then skip the Android NDK download
#android.skip_android_ndk_download = False

# (bool) If True, then skip the Android SDK download
#android.skip_android_sdk_download = False

# (str) The path to a custom Android NDK
#android.ndk_path =

# (str) The path to a custom Android SDK
#android.sdk_path =

# (str) The path to a custom Android NDK version
#android.ndk_version =

# (str) The path to a custom Android SDK version
#android.sdk_version =

# (str) The path to a custom Android keystore
#android.keystore =

# (str) The alias for the custom Android keystore
#android.keystore_alias =

# (str) The password for the custom Android keystore
#android.keystore_password =

# (str) The path to the Android NDK toolchain
#android.ndk_toolchain =

# (str) The toolchain version for the Android NDK
#android.ndk_toolchain_version =

# (str) The build tools version for the Android SDK
#android.sdk_build_tools_version =

# (str) The platform version for the Android SDK
#android.sdk_platform_version =

# (list) Android Blueprints to include (currently works only with sdl2 bootstrap)
#android.blueprints =

# (str) Path to a file containing the Android Blueprints to include
#android.blueprints_src =

# (bool) If True, then disable the Python compilation
#android.no-compile-pyo = False

# (bool) If True, then enable the Python compilation optimization
#android.compile-pyo = True

# (bool) If True, then enable the Python compilation optimization level 2
#android.optimize = True

# (str) The path to the Python installation to use
#python.path =

# (str) The path to the Python installation to use for the host
#python.host_path =

# (str) The path to the Python installation to use for the target
#python.target_path =

# (str) The Python version to use
#python.version =

# (str) The Python major version to use
#python.major_version =

# (str) The Python minor version to use
#python.minor_version =

# (str) The Python micro version to use
#python.micro_version =

# (str) The Python release level to use
#python.release_level =

# (str) The Python release serial to use
#python.release_serial =

# (str) The path to the Python installation to use for the host
#python.host_python =

# (str) The path to the Python installation to use for the target
#python.target_python =

# (str) The path to the Python installation to use for the host
#python.host_python_path =

# (str) The path to the Python installation to use for the target
#python.target_python_path =

# (bool) If True, then enable the Python debug
#python.debug = False

# (bool) If True, then enable the Python profiling
#python.profiling = False

# (bool) If True, then enable the Python tracing
#python.tracing = False

# (bool) If True, then enable the Python coverage
#python.coverage = False

# (str) The path to the Python installation to use for the host
#python.host_python_install =

# (str) The path to the Python installation to use for the target
#python.target_python_install =

# (str) The path to the Python installation to use for the host
#python.host_python_install_path =

# (str) The path to the Python installation to use for the target
#python.target_python_install_path =

# (bool) If True, then use the host Python installation
#python.use_host_python = False

# (bool) If True, then use the target Python installation
#python.use_target_python = False

# (bool) If True, then use the host Python installation for the host
#python.use_host_python_for_host = False

# (bool) If True, then use the target Python installation for the target
#python.use_target_python_for_target = False

# (bool) If True, then use the host Python installation for the target
#python.use_host_python_for_target = False

# (bool) If True, then use the target Python installation for the host
#python.use_target_python_for_host = False

# (bool) If True, then use the host Python installation for the host
#python.use_host_python_for_host_for_host = False

# (bool) If True, then use the target Python installation for the target
#python.use_target_python_for_target_for_target = False

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
