[app]

# (str) Title of your application
title = HR Strength System
version = 1.0

# (str) Package name
package.name = hrstrengthapp

# (str) Package domain (needed for android packaging)
package.domain = org.hrsystem

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (this includes your json databases)
source.include_exts = py, png, jpg, kv, json

# (list) List of exclusions using pattern matching
source.exclude_exts = spec

# (list) Application requirements
# Buildozer handles downloading and injecting these safely
requirements = python3, kivy

# (str) Supported orientations (landscape, portrait or all)
orientation = portrait

# ==========================================================
# ANDROID CONFIGURATION
# ==========================================================

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions required by the app for CSV file exporting
android.permissions = android.permission.WRITE_EXTERNAL_STORAGE, android.permission.READ_EXTERNAL_STORAGE, android.permission.MANAGE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip truetype fonts to reduce APK size
android.skip_heapsnapshot = 1

# (list) The Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Allow backup
android.allow_backup = True

# ==========================================================
# BUILDOZER SETTINGS
# ==========================================================

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
