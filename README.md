# disc-drive

A lightweight Windows desktop app for automatically uploading images and videos from a local folder to a Discord webhook.

The project is focused on a simple workflow: watch a folder, queue supported files, and send them to Discord with optional delay, custom post text, embed mode, avatar handling, tray behavior, and recent-file thumbnails.

## Current status

This README reflects the current behavior up to version **3.0.36**.

## What the app includes

Monitor a local folder for supported media.

Upload files to a Discord webhook.

Keep files ordered by real creation date when possible.

Apply an optional delay before sending new posts.

Use a configurable interval between uploads.

Pause or resume monitoring from the home page.

Hide to the system tray and restore near the tray area.

Auto-hide the interface when it loses focus.

Edit webhook, watched folder, and main options directly inside **Settings**.

Customize post text, webhook name, webhook image, and embed color inside **Customize Post**.

Show up to **14** recent thumbnails in a **7 × 2** layout on the home page.

Clear the sent-history log when needed.

Start with Windows.

Optionally move sent files to the Recycle Bin.

## Webhook and folder setup

The current interface no longer uses separate webhook and folder edit pages.

Both actions now live directly inside **Settings**:

1. Paste the webhook with the **Paste** button.
2. Choose the watched folder with the **Browse** button.
3. All changes are saved immediately.

Long webhook URLs are shown in a shortened form in the interface so the layout stays clean.

## Avatar behavior

The app can work with three avatar sources:

1. A manually selected custom image.
2. The current webhook avatar.
3. The local default image at `files/default-img.png`.

If the local default image is missing, the app generates a fallback default image automatically.

## Default image location

The application expects the default image here:

```text
disc-drive/
├─ main.py
├─ files/
│  └─ default-img.png
```

The `files` folder must stay next to the main script or executable.

## FFmpeg

For better thumbnail support, keep FFmpeg here:

```text
ffmpeg/bin/ffmpeg.exe
```

This folder should stay next to the main script or executable.

## Configuration files

The app stores runtime data in:

```text
%LOCALAPPDATA%/disc-drive/
```

Typical files and folders include:

`config.json`

`sent_log.json`

`avatar.png`

`thumbs-log/`

## Python requirements

Install the Python packages listed in `requirements.txt`.

Current runtime dependencies are:

`PySide6`

`requests`

`Send2Trash`

## Notes

The home page now focuses on monitoring state and recent history.

The old **Send Now** action is no longer part of the interface.

The settings page is the main place for connection and folder setup.

The project is Windows-focused because of tray behavior, startup integration, and Windows-specific file handling.

## Recommended folder layout

```text
disc-drive/
├─ main.py
├─ files/
│  └─ default-img.png
└─ ffmpeg/
   └─ bin/
      └─ ffmpeg.exe
```

## Changelog

See `CHANGELOG.md` for version history.
