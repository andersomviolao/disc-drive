# Changelog

All notable changes to **disc-drive** are documented in this file.

This changelog combines the latest version notes with reconstructed historical entries from uploaded source snapshots. Older versions were rebuilt from source snapshots, so very small visual tweaks may not be listed individually.

## [3.0.61]

### Changed

- Replaced the old **App Version** row with a new **About** card in **Settings**.
- Added a clickable GitHub project link.
- Added build metadata with version and fixed build date.
- Added programming-language, credits, and license-notice fields to the interface.
- Kept the new information block visually aligned with the existing card system.

## [3.0.60]

### Fixed

- Wrapped the **Webhook Profile** controls in the same inline container pattern used elsewhere in the interface.
- Improved layout consistency inside the profile card on the **Customize Post** page.

## [3.0.59]

### Changed

- Reworked the home **Recent Uploads** gallery to use **6 columns × 5 rows** instead of 7 columns.
- Made thumbnail tile size derive from the available width for more stable alignment.
- Standardized inline control-row helpers across the settings and customize sections.
- Refactored shared card foundations so settings rows and content cards follow the same internal structure.

## [3.0.58]

### Changed

- Moved the home recent-history block into a proper card section so it matches the rest of the project skeleton.
- Simplified timer-related config normalization around the current minute-based delay flow.
- Removed some leftover legacy helpers and old config fields that were no longer needed.

## [3.0.57]

### Changed

- Unified page, body, scroll, and card stack spacing through a shared section-spacing constant.
- Simplified page scroll-area creation by relying more directly on the shared page skeleton builder.

## [3.0.56]

### Changed

- Linked page skeleton card sizing to the shared card dimension constants.
- Reduced duplicated layout values for profile and post-content card sizing.
- Continued tightening the shared layout foundation used across pages.

## [3.0.55]

### Changed

- Introduced a shared page skeleton system for headers, top rows, scroll containers, and card spacing.
- Standardized page construction around shared margin and spacing helpers.
- Improved structural consistency between **Home**, **Settings**, and **Customize Post**.

## [3.0.54]

### Changed

- Expanded the home-page history gallery from 2 rows to 5 rows.
- Made the home page content scrollable so larger history blocks fit without breaking the fixed window size.
- Moved the history section into the main home scroll flow and tightened home scroll spacing.

## [3.0.53]

### Changed

- Simplified thumbnail-strip positioning by switching to a fixed 7-column slot layout.
- Made row placement and spacing more predictable across different history counts.

## [3.0.52]

### Changed

- Reworked the home thumbnail strip to use responsive spacing helpers instead of a fixed overall width.
- Centered the **Last sent** gallery more cleanly while keeping 7 columns and wrapped rows.
- Improved row-spacing controls for the home history gallery.

## [3.0.51]

### Fixed

- Fixed external-scrollbar parenting so overlay scrollbars attach to the main panel correctly.
- Improved scrollbar stacking and placement reliability in pages using the custom external scroll pane.

## [3.0.50]

### Changed

- Moved custom page scrollbars farther outside the content area for cleaner visual alignment.
- Added logic to re-parent and preserve external scrollbars correctly when page containers change.

## [3.0.49]

### Changed

- Slimmed the custom page scrollbar again for a lighter visual style.
- Repositioned the external scrollbar to sit tighter against the page edge.
- Added geometry refresh helpers so the scrollbar tracks page resizing more accurately.

## [3.0.48]

### Added

- Added a custom external vertical scrollbar system for scrollable pages.

### Changed

- Reworked page scroll containers to hide the native Qt vertical scrollbar and use a detached overlay scrollbar instead.
- Reduced scrollbar width and radius for a cleaner appearance.

## [3.0.47]

### Changed

- Moved more fonts, weights, alignment values, margins, and spacing rules into shared constants.
- Standardized typography and spacing across pages, cards, popups, and history sections.
- Tightened scrollbar configuration values for the refreshed layout system.

## [3.0.46]

### Changed

- Reworked the post editor to start at a single visible line and grow automatically with the content.
- Removed the internal scrollbar from the post text field.
- Allowed the **Post Content** card itself to expand and shrink with the editor height.

## [3.0.45]

### Changed

- Centralized card styling into shared helpers and layout constants.
- Standardized card borders, radius, padding, and spacing across the customize page.
- Rebalanced profile and post-content card minimum heights.

## [3.0.44]

### Changed

- Moved button, input, popup, avatar, and color-control dimensions into shared constants.
- Standardized the minimum button width to **80px** across the interface.
- Normalized input, toggle, and popup sizing for a more consistent layout foundation.

## [3.0.43]

### Changed

- Refined the embed-color popup layout by moving the **Hex** label into its own aligned row.
- Standardized related action buttons to a fixed 28px height for cleaner alignment.

## [3.0.42]

### Changed

- Compacted the overall interface sizing with smaller controls and tighter card proportions.
- Reduced the embed-color popup footprint and trimmed editor height to match the denser layout.
- Adjusted button widths and control heights toward a cleaner, more compact presentation.

## [3.0.41]

### Changed

- Reworked button and input styling for a more polished, consistent visual language.
- Replaced the small gear-only settings action on the home page with a labeled **Settings** button.
- Standardized 30px control heights across key buttons and fields in the customize flow.

## [3.0.40]

### Changed

- Rebalanced the **Customize Post** page card sizes to reduce empty space and keep the layout more compact.
- Swapped the embed section to the same setting-row pattern used elsewhere in the interface.
- Enabled live saving of post-template text while typing in the editor.

## [3.0.39]

### Added

- Added a scrollable container to the **Customize Post** page.

### Changed

- Stacked the profile, embed, and post-content sections inside a scroll area to prevent overflow.
- Rebalanced card heights and control sizes for the new scrolling layout.
- Slightly enlarged the top-right settings icon button styling.

## [3.0.38]

### Changed

- Reworked the **Customize Post** page into clearer card-style sections.
- Updated the home-page settings button to a rounded icon-style action.
- Refined profile, embed, and post-editor styling for a cleaner, more unified look.

## [3.0.37]

### Changed

- Polished home-page header spacing and settings-button behavior.
- Added a tooltip to the settings action.
- Relaxed the fixed width of the customize-page back button for a cleaner header layout.

## [3.0.36]

### Removed

- Removed the **Send Now** button from the home page.
- Removed the remaining manual send-now backend flow and related UI wiring.

### Changed

- Expanded the **Last sent** gallery from one row of 7 thumbnails to two rows of 7 thumbnails.
- Updated thumbnail positioning to support the wrapped 2-row layout.
- Tuned thumbnail fade and move timings for a lighter, cleaner home-page animation flow.

## [3.0.35]

### Changed

- Simplified webhook and watched-folder setup by keeping both actions directly inside **Settings**.
- Removed the separate dedicated webhook and folder edit pages from the navigation flow.
- Shortened the **Post Timer** description to keep the settings layout visually cleaner.
- When required setup is missing, the app now opens **Settings** directly instead of redirecting to standalone edit pages.

## [3.0.34]

### Changed

- Added a shortened / masked webhook subtitle display to prevent long webhook URLs from breaking the settings layout.
- Kept the full webhook value available through the tooltip while showing a cleaner compact label in the interface.

## [3.0.33]

### Added

- Added a **Paste** action for the webhook setting using the clipboard.

### Changed

- Replaced the inline webhook text field and save button in **Settings** with a more compact clipboard-driven workflow.
- The webhook row now shows the saved webhook directly in the subtitle area.

## [3.0.32]

### Changed

- Simplified watched-folder editing in **Settings** by using a direct browse workflow instead of a readonly text field plus separate save action.
- Updated the watched-folder row to show the current folder path in the subtitle area.

## [3.0.31]

### Changed

- Moved webhook and watched-folder editing from the home screen into the **Settings** page.
- Reworked both settings rows to support compact inline controls.
- Renamed the home-page history section from **History** to **Last sent**.

## [3.0.30]

### Changed

- Improved file ordering and timestamp formatting by preferring the real Windows creation timestamp when available, while keeping safe fallback paths for other metadata sources.
- Added dedicated helpers for creation-date handling used by sorting and post-template rendering.

## [3.0.24]

### Removed

- Removed the full **Debug Mode** system to reduce code size.
- Removed the **Debug Mode** toggle from the settings page.
- Removed `debug_mode` from configuration handling.
- Removed `debug.json` generation and debug session/file writing.

### Changed

- Kept a no-op internal `debug_log()` stub only to avoid breaking existing call sites while producing no output.
- The application now stays silent in normal operation, leaving only regular Python errors when something actually breaks.

## [3.0.23]

### Changed

- Moved the default local image lookup from `LOCALAPPDATA` to the application's runtime folder.
- The app now looks for `files/default-img.png` next to the main script / executable.

## [3.0.22]

### Removed

- Removed the remote URL-based default placeholder download flow.
- Removed SVG-based placeholder rendering for the default avatar source.

### Changed

- The default image is now expected as a local file at `files/default-img.png`.
- Added a generated temporary fallback avatar for webhook sending when the local default image is missing.
- The interface now shows a solid Discord blue block when no local default image is available.
- Updated avatar handling to prefer:
  - webhook default avatar
  - local `default-img.png`
  - generated temporary Discord blue avatar
- Standardized the main blue accent color to Discord blue `#5865F2`.
- Changed the default embed color to Discord blue `#5865F2`.
- Updated color-related placeholders and hover states to match the new blue palette.

## [3.0.21]

### Changed

- Reordered the settings page for a cleaner and more practical workflow.
- The settings page now follows this order:
  - Delete after send
  - Clear log
  - Start with Windows
  - Customize post
  - Post timer
  - Open folder
  - Debug mode
  - App version

## [3.0.20]

### Changed

- Increased cached thumbnail size to **300px**.
- Kept the existing thumbnail rendering logic while improving source quality for new history items.

## [3.0.19]

### Changed

- Reduced drag-related debug noise.
- Removed repeated `window_drag_moved` entries from drag logging.
- Kept only the drag start and drag release debug events.

## [3.0.18]

### Changed

- Reduced idle debug spam in the console.
- Stopped printing tray refresh messages on every timer tick.
- Removed repetitive monitoring loop and sleep tick events.
- Limited folder scan logging to cases where files actually exist for analysis.

## [3.0.17]

### Fixed

- Fixed the `ApplicationState` debug crash in `on_application_state_changed`.
- Replaced the invalid direct `int(state)` cast with safe enum handling.
- Adjusted active-state comparison for PySide6 application state enums.

## [2.0.5]

### Added

- Introduced a popup-based embed color picker (`EmbedColorPopup`) with:
  - saturation/value area
  - hue slider
  - HEX input
  - live color preview
  - save-on-close behavior

### Changed

- Replaced the previous dialog-based color picker with a lightweight floating popup workflow.
- Moved the **Test Webhook** action into the post customization page.
- Improved live synchronization between the post page color swatch and the popup picker.

### Fixed

- Improved embed color editing reliability and popup state handling.

## [2.0.4]

### Changed

- Reworked the embed color selection flow again using a Qt color dialog-based implementation.
- Restored the **Test Webhook** action inside the post customization workflow.

### Fixed

- Improved color preview and HEX field synchronization.

## [2.0.3]

### Added

- Added a custom embed color editor with:
  - `ColorSpectrumBox`
  - `HueSlider`
  - manual HSV/HEX synchronization

### Changed

- Replaced the simpler color dialog flow with a more advanced custom picker experience.

## [2.0.2]

### Added

- Added post mode selection with optional embed sending.
- Added embed configuration fields in the post customization page.
- Added stored embed color support in configuration.
- Added `ColorSwatchButton` and the first dedicated embed color dialog.

### Changed

- The uploader can now send either plain text content or a Discord embed with configurable color.

## [2.0.1]

### Added

- Added a full **Post Template Page**.
- Added `post.txt` save/load support from the interface.
- Added template rendering helpers for filename and timestamp placeholders.
- Added automatic save behavior when navigating away from the post editor.

### Changed

- Settings now include a direct entry point for editing the post template.

## [2.0.0]

### Changed

- Version bump and maintenance snapshot following the tray icon redesign work.
- No major visible feature expansion compared with `v1.9.9` in the uploaded source snapshot.

## [1.9.9]

### Added

- Integrated the redesigned animated tray icon directly into the main application.
- Added dedicated drawing routines for:
  - active ring state
  - paused ring state
  - animated sending state

### Changed

- Tray behavior now refreshes dynamically while sending.

## [1.9.8]

### Changed

- Refined the tray exit bubble implementation and sizing.
- Polished the lightweight exit UI shown from the tray interaction flow.

## [1.9.7]

### Added

- Added `TrayExitBubble`, a compact floating exit action shown near the cursor.

### Changed

- Replaced the previous tray exit interaction with a cleaner popup-style action.

## [1.9.6]

### Added

- Added `HomeValueRow` to improve value presentation on the home page.
- Added a dedicated **Send Now** button directly in the main bottom action row.

### Changed

- Refined home page layout and button sizing.
- Improved presentation of the saved webhook and watched folder.
- Continued visual cleanup of the PySide6 interface.

## [1.9.5]

### Added

- Added **Clear Log** / sent-history reset support from settings.
- Added a backend helper to wipe the sent file log.

### Changed

- Expanded settings management with safer re-upload workflow support.

## [1.9.4]

### Added

- Added `hide_to_tray()` behavior.
- Added a small reusable edit-card pattern for the home page.

### Changed

- The close action now hides the window to the tray instead of exiting immediately.
- Updated the home page to use styled text buttons and card-style editing actions.
- Refined settings button sizing and placement.

## [1.9.3]

### Changed

- Adjusted configuration folder handling and related settings-page details.
- Continued polish of the multi-page PySide6 settings layout.

## [1.9.2]

### Added

- Added a scrollable settings area using `QScrollArea`.

### Changed

- Improved settings page scalability for a growing number of options.

## [1.9.1]

### Added

- Added a dedicated **Browse Folder** action in the folder page.

### Changed

- Improved folder editing workflow in the PySide6 interface.

## [1.9.0]

### Added

- Introduced a larger multi-page PySide6 application structure with:
  - `HomePage`
  - `WebhookPage`
  - `FolderPage`
  - `SettingsPage`

### Changed

- Continued the transition away from the earlier simpler layout.

## [1.8.0]

### Added

- Migrated the application UI to **PySide6**.
- Added a cleaner custom interface with in-window pages instead of separate utility popups.

### Changed

- Replaced the older Tk / CustomTkinter based workflow with a more polished Qt-based interface.

## [1.7.2]

### Changed

- Improved file queue behavior and reliability around delayed sending.
- Continued refinement of file ordering and send timing.

## [1.7.1]

### Changed

- Polished the delayed posting workflow.
- Improved general send stability.

## [1.7]

### Added

- Added delayed posting support.
- Added configurable wait time before new files can be sent.
- Added a send interval between uploads.

### Changed

- Improved the monitored-folder send workflow to better support queue-style posting.

## [1.6]

### Added

- Added support for custom post text.
- Added placeholder rendering for file name and dates.

## [1.5]

### Added

- Added tray pause / resume controls.
- Added better sent-log handling.

## [1.4]

### Changed

- Improved basic UI flow and configuration management.

## [1.3]

### Added

- Added configuration storage improvements.
- Added watched-folder persistence.

## [1.2]

### Changed

- Improved webhook validation and first-run behavior.

## [1.1]

### Added

- Added JSON-based config persistence in `LOCALAPPDATA`.
- Added a first-run GUI setup flow.
- Added tray image creation and pause/exit actions.

### Changed

- Replaced hardcoded setup with stored configuration files.

## [1.0]

### Added

- Initial working version of the uploader.
- Added watched-folder scanning.
- Added Discord webhook file upload.
- Added tray controls for pause, resume, and exit.
- Added optional delete-after-send behavior using the recycle bin.
