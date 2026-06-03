[app]
# (str) Title of your application
title = Strelizia HR System

# (str) Package name
package.name = strelizia_hr

# (str) Package domain (needed for android packaging)
package.domain = org.uav_tech.hr

# (str) Source code directory
source.dir = .

# (list) Source files to include (comma separated)
source.include_exts = py,png,jpg,kv,json

# (str) Application version
version = 1.0.0

# (list) Application requirements
# Crucial: Strictly no spaces after commas. Pinned to stable packages.
requirements = python3,kivy==2.3.0,pillow,openssl,sqlite3

# (int) Preferred orientation (landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# ==========================================================
# ANDROID CONFIGURATIONS
# ==========================================================

# (int) Android API to use (Target SDK)
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android Build Tools version to use
# CRITICAL FIX: Explicitly locked to stable. Prevents auto-fetching version 37.
android.build_tools_version = 33.0.1

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use
android.ndk_api = 21

# (bool) Use private storage for data (Needed for secure app sandboxing)
android.private_storage = True

# (list) Permissions requested by the app
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (list) Architectures to build for (Covering modern arm mobile devices)
android.archs = armeabi-v7a, arm64-v8a

# (bool) Allow Google Play backups
android.allow_backup = True

# ==========================================================
# BUILDOZER ENGINE PROPERTIES
# ==========================================================
[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug with command output)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 0
