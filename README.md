# disc-drive

Simple monitoring, polished visuals, and everything inside the same interface.

## Overview

**disc-drive** is a Windows desktop app built with **Python** and **PySide6**.
It watches a folder, sends supported files to a **Discord webhook**, and keeps the workflow inside a compact single-window interface.

The current version is **v3.0.21**.

## Main features

- Watch a local folder and send new files to a Discord webhook
- Support for image and video files
- Send files in creation-time order on Windows
- Optional delay timer before sending new files
- Optional interval between posts
- Optional **Delete after send** behavior using the Recycle Bin
- Manual **Send Now** action
- Editable custom post template
- Template variables for file name and timestamps
- Optional embed mode with color picker
- Custom webhook display name
- Custom webhook profile image
- History area with thumbnails of recently sent files
- Video thumbnail generation through local FFmpeg
- Start with Windows
- Debug mode with console output and `debug.json`
- Open local configuration folder directly from the app
- Clear send history log from the settings page

## Supported file types

### Images

- `.png`
- `.jpg`
- `.jpeg`
- `.gif`
- `.webp`
- `.bmp`

### Videos

- `.mp4`
- `.mov`
- `.m4v`
- `.avi`
- `.mkv`
- `.webm`
- `.wmv`
- `.mpeg`
- `.mpg`
- `.m2ts`
- `.ts`

## Requirements

- Windows 10 or Windows 11
- Python 3.11+
- A valid Discord webhook URL

## Python dependencies

Install the required packages with:

```bash
pip install PySide6 requests send2trash
```

## FFmpeg

Video thumbnails use a local FFmpeg binary.
The expected path is:

```text
ffmpeg\bin\ffmpeg.exe
```

Place the `ffmpeg` folder next to the script or executable.

## How to run

```bash
python main.py
```

Or run the versioned script directly, for example:

```bash
python v3.0.21.py
```

## Basic workflow

1. Open the app
2. Set your Discord webhook URL
3. Choose the watched folder
4. Configure the custom post if needed
5. Turn monitoring on
6. Let the app send supported files automatically

## Custom post variables

The post editor supports these variables:

- `{filename}`
- `{creation_str}`
- `{upload_str}`

## Local files

The app stores its local data in:

```text
%LOCALAPPDATA%\disc-drive
```

Typical files and folders:

- `config.json`
- `sent_log.json`
- `debug.json`
- `thumbs-log\`
- `default-img.png`
- `webhook-default-avatar.png`

## Notes

- If **Delete after send** is disabled, the app keeps the file and relies on the send log to avoid duplicates
- Clearing the log allows previously processed files to be sent again
- New thumbnail quality improvements apply to newly generated thumbnails
- The app is currently designed around a Windows workflow

## Changelog

See `CHANGELOG.md` for recent version history.
