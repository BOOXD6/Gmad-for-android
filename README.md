# GMAD & VPK Extractor

A simple Android app for extracting `.gma` (Garry's Mod addon) and `.vpk` (Valve Pak) files straight from your phone. No PC needed — pick a file, hit extract, and get a zip back with everything inside it.

Built with Python, Kivy, and KivyMD.

## Why this exists

I got tired of having to plug my phone into a PC (or use some sketchy web tool) just to peek inside a `.gma` file or pull assets out of a `.vpk`. This does it locally, on-device, no uploads anywhere.

## Features

- Extract `.gma` files (Garry's Mod addons)
- Extract `.vpk` files (Source engine paks)
- Pick a file manually by typing the path, or use the built-in file browser
- Output is zipped automatically and saved to `/sdcard/Gmad_Extracted/`
- Progress shown live while it's working
- Dark UI, no ads, nothing weird

## How to use it

1. Open the app and grant it file access when it asks (needed to read/write to your storage — see below).
2. Enter the path to your `.gma` or `.vpk` file, or tap **Choose From Files** to browse for it.
3. Tap **Extract**.
4. Wait for it to finish — bigger files take longer, especially ones with lots of small assets.
5. Your extracted files will be zipped up in `/sdcard/Gmad_Extracted/GMAD_Files/` or `/sdcard/Gmad_Extracted/VPK_Files/`.

## Permissions

The app needs full storage access to read the file you point it at and to write the extracted zip back to your SD card. On Android 11+, this means granting "All files access" in system settings — the app will send you straight to that screen on first launch if it isn't granted yet.

## Troubleshooting

**"This is not a GMAD file"**
You're probably trying to extract a file that's actually LZMA/BIN-compressed (common with mods downloaded straight from the Workshop). Open it in something like ZArchiver first, extract the real `.gma` out of it, then point this app at that.

**VPK extraction fails / file not found**
Multi-part VPKs (`pak01_dir.vpk` plus `pak01_000.vpk`, `pak01_001.vpk`, etc.) all need to be sitting in the same folder. If they're split up, extraction will fail looking for the missing pieces.

**Something else broke**
DM me on Discord (link below) with the error message and I'll take a look.

## Building it yourself

Dependencies:

```
kivy
kivymd
construct
requests
vpk
```

This is a python-for-android / Buildozer project, so if you want to build the APK yourself you'll need Buildozer set up with those packages listed in your `buildozer.spec`.

## Notes

- The Steam Workshop downloader that used to be in here has been pulled out — it'll probably come back as its own separate app at some point.
- Everything runs locally on your device. Nothing you extract gets sent anywhere.

## Contact

Questions, bugs, feature ideas — [join the Discord](https://discord.gg/juZZs7hYwy) and ping boo271.

## Credits
Built with help from Claude (Anthropic) 
