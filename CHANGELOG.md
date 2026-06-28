# Changelog

All notable changes to **Byte Recovery Pro** are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) — versions use `MAJOR.MINOR.PATCH`.

---

## [2.1.0] — 2026-06-28

### Added
- `version.txt` — single source of truth for the app version number; UI reads it dynamically via Eel
- `CHANGELOG.md` — this file; tracks all notable changes across releases
- **GitHub link** in sidebar footer — clickable pill button linking to [gurukannan22](https://github.com/gurukannan22)
- **"Made with ♥ by Guru Kannan"** credit with animated heartbeat in sidebar footer

### Fixed
- **"How it Works" tab rendering blank** — root cause: `class="tab-panel hidden"` combined with `.hidden { display:none !important }` was overriding the `.active` CSS rule; removed static `hidden` class from `tab-info` so tab toggling works correctly

---

## [2.0.0] — 2026-06-28

### Added
- **Full UI redesign** — premium two-panel layout (sidebar + main content area)
- **Sidebar navigation** — brand logo, Recover / How it Works tabs, system status indicator
- **Live log feed** — timestamped real-time panel showing each signature match with color-coded entries (green = found, red = error)
- **Stat cards** — three cards (Data Scanned / Files Detected / Saved) with colored icons during scanning
- **Type-chip selectors** — file type filters are now interactive toggle chips with "All / None" quick buttons
- **"How it Works" tab** — four-step explainer (Open Raw Disk → Chunk Scanning → Signature Matching → File Extraction)
- **Shake animation** — primary button shakes if drive input is empty instead of showing a plain alert
- **Shimmer animation** on the primary Start Deep Scan button
- **Animated orb background** — three floating gradient blobs with a subtle grid overlay
- **Admin privilege indicator** — colored dot in sidebar footer (green = elevated, red = no rights)
- Fonts upgraded to **Inter 800** (headings) + **JetBrains Mono** (paths, code, log feed)

### Changed
- Layout changed from single centered card to **full-viewport sidebar + scrollable main area**
- File type selector changed from plain checkboxes to **chip pills**
- Progress bar is now a **slim 4px indeterminate sweep**, turns solid green on completion
- All element references in `script.js` updated to match the new HTML structure
- `recovery_finished` no longer crashes — correctly references `.radar-ping` → `.pulse-ring` and `.progress-wrapper`

### Removed
- Old glassmorphism centered container layout
- Old `pulse-ring` / `progress-container` references that caused JS crashes on scan completion

---

## [1.1.0] — 2026-06-28

### Added
- `get_available_drives_info()` — cross-platform drive lister returning path, name, and disk size:
  - **Windows**: logical drives via Win32 `GetVolumeInformationW` + physical drives via PowerShell `Get-CimInstance Win32_DiskDrive` (with WMIC fallback)
  - **macOS**: parses `diskutil list` to extract raw `/dev/rdiskN` paths and sizes
  - **Linux**: queries `lsblk -J` for active block devices
- `check_admin()` Eel endpoint — returns `True` when running as Administrator (Windows) or root (macOS/Linux)
- **Admin warning banner** in GUI — red alert shown when app is launched without elevated privileges
- `--list-drives` CLI flag now works on **all platforms** (previously Windows-only), showing path + description

### Fixed
- **Sector-aligned disk reads** — `_recover_file` and `scan` now align offsets and chunk sizes to 512-byte boundaries when scanning raw Windows disks opened with `FILE_FLAG_NO_BUFFERING`; previously caused `OSError: [Errno 22] Invalid argument`
- **Shared file pointer desynchronization** — `_recover_file` now saves (`fh.tell()`) and restores (`fh.seek()`) the main scan pointer in a `finally` block; previously the scan loop lost its position after every recovered file
- **GUI scan completion crash** — `recovery_finished` in `script.js` referenced `.pulse-ring` and `.progress-container` which did not exist; corrected to `.radar-ping` and `.progress-wrapper`

### Changed
- Recovered files now organized into **extension subdirectories** (e.g. `recovered/jpg/`, `recovered/pdf/`) instead of a flat folder; aligns with TUTORIAL.md documentation
- `get_drives()` Eel endpoint updated to return rich `{path, name, type}` objects instead of plain strings
- Drive dropdown in GUI now shows disk model, size, and type alongside the path

---

## [1.0.0] — 2026-06-27 *(Initial Release)*

### Added
- **Core file carving engine** (`recovery.py`) — sector-level scanning using magic number signatures
- **30+ supported file types**: JPEG, PNG, GIF, BMP, TIFF, WebP, PDF, DOC, RTF, ZIP, RAR, 7z, GZip, MP3, MP4, AVI, WAV, MKV, FLV, OGG, FLAC, EXE, ELF, SQLite
- **Office file detection** inside ZIP archives — detects `.docx`, `.xlsx`, `.pptx`, `.apk`, `.jar` by peeking at internal paths
- **Windows raw drive access** via Win32 `CreateFileW` with `FILE_FLAG_NO_BUFFERING` and `FILE_SHARE_READ|WRITE`
- **Cross-boundary signature detection** — 64-byte tail buffer prevents missing headers split across chunk boundaries
- **512 KB chunk scanning** with cross-boundary tail buffer
- **GUI app** (`app.py`) using Python Eel + Chrome/Chromium window (900×700)
- **Glassmorphism UI** — dark mode with animated mesh gradient background, Inter font
- **CLI interactive mode** — guided prompts for drive, output dir, and file type filters
- **CLI direct mode** — full argument parser (`-d`, `-o`, `-m`, `-t`, `--offset`, `--limit`, `-v`, `--list-drives`, `--list-types`)
- **Live progress** — real-time MB scanned, files found, and files saved display
- **Windows `.exe` build script** (`build.bat`) — PyInstaller one-file bundle with embedded `web/` assets
- `README.md` — full documentation with prerequisites, usage examples, and architecture overview
- `TUTORIAL.md` — step-by-step guide for Windows, macOS, and Linux

---

*Developed with ❤️ by [Guru Kannan](https://github.com/gurukannan22)*
