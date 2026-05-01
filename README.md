# Folder2Discord

A lightweight Windows desktop app for automatically uploading images and videos from a local folder to a Discord webhook.

The project is focused on a simple workflow: watch a folder, queue supported files, and send them to Discord with optional delay, custom post text, embed mode, avatar handling, tray behavior, and recent-file thumbnails.

## Current Status

This README reflects the current behavior up to version **3.0.63**.

## What The App Includes

- Monitor a local folder for supported media.
- Upload files to a Discord webhook.
- Keep files ordered by real creation date when possible.
- Apply an optional delay before sending new posts.
- Use a configurable interval between uploads.
- Pause or resume monitoring from the home page.
- Hide to the system tray and restore near the tray area.
- Auto-hide the interface when it loses focus.
- Edit webhook, watched folder, and main options directly inside Settings.
- Customize post text, webhook name, webhook image, and embed color.
- Show up to 30 recent thumbnails on the home page in a 6 x 5 gallery.
- Open an About card with project link, build metadata, credits, and license notices.
- Optionally move sent files to the Recycle Bin.

## Supported File Types

Images:

```text
png, jpg, jpeg, gif, webp, bmp
```

Videos:

```text
mp4, mov, m4v, avi, mkv, webm, wmv, mpeg, mpg, m2ts, ts
```

## Setup

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

Run:

```powershell
pythonw .\main.pyw
```

In Settings:

1. Paste the Discord webhook.
2. Choose the watched folder.
3. Configure delay, interval, startup, deletion, and post options.

## Runtime Data

Folder2Discord stores runtime data in:

```text
%LOCALAPPDATA%\Folder2Discord
```

Typical files and folders include:

- `config.json`
- `sent_log.json`
- `avatar.png`
- `thumbs-log`

## Recommended Layout

```text
Folder2Discord
  main.pyw
  img
    default-img.png
  ffmpeg
    bin
      ffmpeg.exe
```

The `img` folder must stay next to the main script or executable. FFmpeg is optional but improves video thumbnail support.

## Documentation

See [documentation.md](documentation.md) for architecture, runtime data, thumbnail handling, startup behavior, and maintenance notes.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

The project license is MIT. See [LICENSE](LICENSE) for the full text.
