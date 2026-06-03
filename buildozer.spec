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
# Core requirements for Kivy Android distribution
requirements = python3,kivy,pyjnius,android

# (str) Supported orientations (landscape, portrait or all)
orientation = portrait

# ==========================================================
# ANDROID CONFIGURATION
# ==========================================================

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions required by the app for CSV file exporting
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# (int) Target Android API - MUST be at least 33 or 34 for NDK 25b compatibility
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use (Must match minapi to prevent toolchain failures)
android.ndk_api = 21

# (bool) If True, then skip truetype fonts to reduce APK size
android.skip_heapsnapshot = 1

# (list) The Android architectures to build for (Changed to single target for stability)
android.archs = arm64-v8a

# (bool) Allow backup
android.allow_backup = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Accept SDK licenses automatically inside headless CI environments
android.accept_sdk_license = True

# ==========================================================
# BUILDOZER SETTINGS
# ==========================================================

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
