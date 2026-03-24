# disc-drive

A lightweight desktop app for automatically uploading images and videos from a local folder to a Discord webhook.

The app was built for a simple workflow: monitor a folder, queue valid files, and send them to Discord with optional custom post text, embed mode, thumbnails, tray behavior, and basic automation controls.

## Current status

This README reflects the current behavior up to version **3.0.24**.

## Main features

- Monitor a local folder for new files
- Upload supported media files to a Discord webhook
- Keep files ordered by real creation date when possible
- Optional delayed posting with a configurable timer
- Optional instant sending mode
- Tray integration with running / paused / sending states
- Settings page inside the main window
- Custom post text editor inside the app
- Optional embed mode for webhook posts
- Default embed color set to **Discord Blue** (`#5865F2`)
- Custom webhook bot name support
- Custom webhook bot image support
- Webhook avatar auto-fetch and refresh
- Local fallback default image support
- Animated / static thumbnail handling for recent files
- Optional delete-after-send behavior
- Start with Windows option
- Clear sent log option

## Default image behavior

The application now expects the default image at:

`files/default-img.png`

This `files` folder must stay next to the main script or executable.

Example:

```text
disc-drive/
├─ main.py
├─ files/
│  └─ default-img.png
```

### Avatar priority

The app uses avatar images in this order:

1. Webhook avatar
2. Local `files/default-img.png`
3. Generated temporary solid Discord Blue avatar

### If `default-img.png` is missing

- The interface shows a solid **Discord Blue** block
- Webhook sending uses a generated temporary blue avatar

## Visual defaults

The main accent color is now **Discord Blue**:

`#5865F2`

The default embed color is also:

`#5865F2`

## Requirements

Typical dependencies may include:

- Python 3
- PySide6
- requests
- Pillow
- send2trash

Depending on your build, additional packages may be required.

## FFmpeg

For better thumbnail support, keep FFmpeg here:

```text
ffmpeg/bin/ffmpeg.exe
```

This folder should stay next to the main script.

## Configuration behavior

The app stores its configuration locally and supports options such as:

- Delete after send
- Clear log
- Start with Windows
- Custom post text
- Post timer
- Open folder shortcut

## Removed behavior

As of **3.0.24**, the project no longer includes the old **Debug Mode** system.

Removed items include:

- Debug Mode toggle
- `debug_mode` config usage
- `debug.json`
- verbose debug logging flow

The app now stays quiet during normal operation, showing only standard Python errors if something actually breaks.

## How to use

1. Open the app
2. Set your Discord webhook URL
3. Choose the folder to monitor
4. Adjust the settings you want
5. Edit the post text if needed
6. Leave the app running or minimize it to tray
7. New supported files will be queued and sent automatically

## Notes

- If a webhook has its own avatar, that avatar takes priority
- Clicking **Clear** in the image area restores the default local image behavior
- If no local default image exists, the app falls back to the generated blue avatar behavior
- The app is designed to stay lightweight and visually minimal

## Recommended folder layout

```text
disc-drive/
├─ main.py
├─ files/
│  └─ default-img.png
├─ ffmpeg/
│  └─ bin/
│     └─ ffmpeg.exe
```

## Changelog

See `CHANGELOG.md` for version history.
