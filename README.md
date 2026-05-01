# Folder2Discord

A lightweight Windows desktop app for automatically uploading images and videos from a local folder to a Discord webhook.

The project is focused on a simple workflow: watch a folder, queue supported files, and send them to Discord with optional delay, custom post text, embed mode, avatar handling, tray behavior, and recent-file thumbnails.

## Current status

This README reflects the current behavior up to version **3.0.61**.

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

Show up to **30** recent thumbnails on the home page in a **6 × 5** gallery.

Use a scrollable home layout so larger recent-history sections fit without breaking the fixed window size.

Use a scrollable **Customize Post** page so all cards stay accessible in the compact window.

Use an auto-growing post editor that starts at a single visible line and expands or shrinks with the content.

Keep the home recent-history area visually aligned with the same card system used across the rest of the interface.

Open a dedicated **About** card inside **Settings** with the project GitHub link, current build and date, programming language, credits, and license notices.

Clear the sent-history log when needed.

Start with Windows.

Optionally move sent files to the Recycle Bin.

## Supported file types

Images:

`png` `jpg` `jpeg` `gif` `webp` `bmp`

Videos:

`mp4` `mov` `m4v` `avi` `mkv` `webm` `wmv` `mpeg` `mpg` `m2ts` `ts`

## Webhook and folder setup

The current interface no longer uses separate webhook and folder edit pages.

Both actions now live directly inside **Settings**:

1. Paste the webhook with the **Paste** button.
2. Choose the watched folder with the **Browse** button.
3. All changes are saved immediately.

Long webhook URLs are shown in a shortened form in the interface so the layout stays clean.

## Post editor behavior

The **Post Content** area now starts in a compact single-line state.

There is no internal text-field scrollbar.

As the text grows, the card itself grows with it.

When text is removed, the card shrinks back automatically.

## Avatar behavior

The app can work with three avatar sources:

1. A manually selected custom image.
2. The current webhook avatar.
3. The local default image at `files/default-img.png`.

If the local default image is missing, the app generates a fallback default image automatically.

## About card

The **About** section in **Settings** includes:

1. A clickable link to the GitHub project.
2. The current app version and build date.
3. The programming language used by the project.
4. Credits.
5. Project and dependency license notices.

The build date is stored directly in code and should be updated with every new version.

## Default image location

The application expects the default image here:

```text
Folder2Discord/
├─ main.pyw
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
%LOCALAPPDATA%/Folder2Discord/
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

## License

The project license is **MIT**. See `LICENSE` for the full text.

The app also references license notices for major runtime components inside the **About** card.

## Notes

The home page now focuses on monitoring state and recent history.

The old **Send Now** action is no longer part of the interface.

The settings page is the main place for connection, folder setup, runtime options, and project information.

The interface uses a compact visual system with shared sizing rules for buttons, inputs, cards, and scroll behavior.

The project is Windows-focused because of tray behavior, startup integration, and Windows-specific file handling.

## Recommended folder layout

```text
Folder2Discord/
├─ main.pyw
├─ files/
│  └─ default-img.png
└─ ffmpeg/
   └─ bin/
      └─ ffmpeg.exe
```

## Changelog

See `CHANGELOG.md` for version history.
