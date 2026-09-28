[app]

title = Gmad

package.name = tools

package.domain = com.gmodkit

source.dir = .

source.include_exts = py,png,jpg,kv,atlas,xml,backports/lzma

version = 2.0

library_dirs = xz-5.2.5/src/liblzma/.libs
include_dirs = xz-5.2.5/src/liblzma/api
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.0,kivymd==1.2.0,pillow,requests,construct,vpk,liblzma

presplash.filename = %(source.dir)s/rell.png

icon.filename = %(source.dir)s/icon.png

orientation = portrait

osx.python_version = 3

osx.kivy_version = 2.0.0

fullscreen = 0

android.presplash_lottie = %(source.dir)s/loading.json

android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE,READ_PHONE_STATE

android.ndk = 25b

android.accept_sdk_license = True
android.storage = sdcard

android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = True

ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master

ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0

ios.codesign.allowed = false


[buildozer]

log_level = 2

warn_on_root = 0
