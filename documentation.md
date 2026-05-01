# Folder2Discord Documentation

This document describes the current Folder2Discord repository and runtime behavior.

## 1. Purpose

Folder2Discord is a compact Windows tray app that watches one local folder and uploads supported images or videos to a Discord webhook. It is designed for a small, always-running desktop workflow with quick access from the system tray.

## 2. Repository Layout

```text
Folder2Discord
  main.pyw           Main PySide6 application entrypoint
  img                Default image assets used by the app
  img/scripts        Image-related helper scripts, when present
  ffmpeg             Optional local FFmpeg runtime for thumbnail support
  requirements.txt   Python dependencies
  README.md          User-facing overview
  documentation.md   Technical and maintenance notes
  CHANGELOG.md       Version history
  LICENSE            MIT license
```

Generated folders such as `__pycache__` are local development artifacts and should not be committed.

## 3. Runtime Data

The app stores user data under:

```text
%LOCALAPPDATA%\Folder2Discord
```

Typical runtime files include:

- `config.json`: watched folder, webhook, post template, timing, UI, and startup settings.
- `sent_log.json`: recent upload history.
- `avatar.png`: selected or cached webhook avatar.
- `thumbs-log`: thumbnail cache for recent uploads.

## 4. Main Workflow

1. The user selects a folder and Discord webhook in Settings.
2. The monitor detects supported media files.
3. Files are queued using creation-time ordering when available.
4. Optional delay and post interval settings are applied.
5. The app sends files to the configured Discord webhook.
6. Sent files can optionally be moved to the Recycle Bin.
7. Recent uploads are shown as thumbnails in the compact home view.

## 5. Supported Media

Image formats:

```text
png, jpg, jpeg, gif, webp, bmp
```

Video formats:

```text
mp4, mov, m4v, avi, mkv, webm, wmv, mpeg, mpg, m2ts, ts
```

## 6. Development

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run:

```powershell
pythonw .\main.pyw
```

Basic syntax validation:

```powershell
python -m py_compile .\main.pyw
```

## 7. Maintenance Guidelines

- Keep `APP_VERSION`, `APP_BUILD_DATE`, and `CHANGELOG.md` aligned.
- Keep `README.md` focused on user-facing behavior.
- Keep this file focused on implementation, runtime data, and maintenance.
- Keep `img/default-img.png` beside the script or packaged executable.
- Keep image-related helper scripts under `img/scripts`.
- Keep optional FFmpeg at `ffmpeg/bin/ffmpeg.exe` when video thumbnails are needed.

## 8. License

Folder2Discord is distributed under the MIT License. See `LICENSE` for the full text.
