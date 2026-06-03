[app]
title = Strelizia HR System
package.name = strelizia_hr
package.domain = org.uav_tech.hr

source.dir = .
source.include_exts = py,png,jpg,kv,json

version = 1.0.0
requirements = python3,kivy==2.3.0,pillow,openssl,sqlite3

orientation = portrait
fullscreen = 1

# Android Specific Target configurations
android.api = 33
android.minapi = 21
android.build_tools_version = 33.0.1
android.ndk = 25b
android.ndk_api = 21
android.private_storage = True

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.archs = armeabi-v7a, arm64-v8a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 0
