# Add project specific ProGuard rules here.
# By default, the flags in this file are appended to flags specified
# in Android SDK tools/proguard/proguard-android.txt

# Keep accessibility service
-keep class com.wangzhe.autoclicker.AccessibilityService { *; }

# Keep floating window service
-keep class com.wangzhe.autoclicker.FloatingWindowService { *; }

# Keep main activity
-keep class com.wangzhe.autoclicker.MainActivity { *; }
