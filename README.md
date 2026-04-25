# 🔍 Byte Recovery Pro

> **Advanced File Carving & Recovery Utility**  
> Developed by **Guru Kannan**

Byte Recovery Pro is a powerful, cross-platform file recovery tool that uses **File Carving** — bypassing the file system entirely — to scan raw disk sectors and recover deleted files based on their binary signatures (Magic Numbers).

Available in two modes:
- 🖥️ **Desktop GUI App** — Modern, beautiful UI powered by Python + HTML/CSS
- ⌨️ **CLI / Terminal** — Full-featured command-line interface for power users

---

## ✨ Features

- **Deep Sector Scanning** — Reads raw disk bytes, recovering files even after deletion, format, or partition loss.
- **30+ File Types Supported:**
  - **Images**: `.jpg`, `.png`, `.gif`, `.bmp`, `.tif`, `.webp`
  - **Documents**: `.pdf`, `.doc`, `.xls`, `.ppt`, `.rtf`, `.docx`, `.xlsx`, `.pptx` (Office files detected inside ZIPs)
  - **Archives**: `.zip`, `.rar`, `.7z`, `.gz`, `.tar`
  - **Audio/Video**: `.mp3`, `.mp4`, `.avi`, `.wav`, `.mkv`, `.flv`, `.ogg`, `.flac`
  - **Executables & DBs**: `.exe`, `.sqlite`
- **Cross-Platform** — Windows (`\\.\D:`), macOS (`/dev/rdisk2`), and Linux (`/dev/sdb`)
- **Type Filtering** — Recover only the file types you need
- **Live Progress** — Real-time stats: MB scanned, files found, files saved
- **Smart Chunk Scanning** — 512KB chunks with cross-boundary detection for maximum accuracy

---

## 📋 Prerequisites

| Requirement | Notes |
|---|---|
| **Python 3.8+** | Download from [python.org](https://python.org) |
| **eel** (for GUI) | `pip install eel` |
| **Admin/Root privileges** | Required to read raw disk data |

---

## 🚀 How to Run

### Option 1: GUI Desktop App (Recommended)

Install the dependency and launch:

```bash
pip install eel
python app.py
```

> **Windows**: Run Command Prompt as Administrator before running the above.  
> **Mac/Linux**: Use `sudo python3 app.py`

The app will open a beautiful desktop window where you can:
- Select your target drive from a dropdown or type it manually
- Choose your output folder
- Filter specific file types
- Watch real-time scan progress

---

### Option 2: CLI — Interactive Mode

```bash
python recovery.py
```

The tool will guide you step-by-step with prompts.

---

### Option 3: CLI — Direct Command Mode

```bash
# Windows – Recover all files from drive D:
python recovery.py -d D -o ./recovered

# Mac/Linux – Scan a raw disk
sudo python3 recovery.py -d /dev/rdisk2 -o ./recovered

# Recover ONLY photos
python recovery.py -d D -t jpg png gif -o ./photos

# Scan a disk image file
python recovery.py -d ./backup.img -o ./recovered
```

**All CLI Options:**

| Flag | Description |
|------|-------------|
| `-d, --drive` | Target drive or image file path |
| `-o, --output` | Output directory (default: `./recovered`) |
| `-m, --max-size` | Max file size in MB (default: 50) |
| `-t, --types` | Filter by types (e.g., `jpg png pdf`) |
| `--offset` | Start scan at byte offset |
| `--limit` | Stop after N bytes |
| `-v, --verbose` | Enable debug output |
| `--list-drives` | Show available drives (Windows only) |
| `--list-types` | List all supported file types |

---

## 🏗️ Build Windows .exe

To distribute as a standalone Windows executable, run the included batch script on a Windows machine:

```bat
build.bat
```

This installs `PyInstaller` and packages everything into a single `dist/ByteRecoveryPro.exe`.

---

## 🔬 How It Works

When a file is deleted, the OS only removes its entry from the file system index (like NTFS MFT). The actual data sits untouched until overwritten.

**Byte Recovery Pro's carving process:**

1. Opens the raw physical drive using OS-level APIs (Win32 `CreateFileW` on Windows, direct `open()` on Unix)
2. Reads the disk in **512KB chunks** for maximum speed
3. Scans each buffer for known **magic number headers** (e.g., `FF D8 FF` for JPEG)
4. When a header is found, reads until a matching **footer** is detected or the max file size is reached
5. Detects Office formats (`.docx`, `.xlsx`) by inspecting ZIP archive contents
6. Saves each carved file to the output directory

---

## ⚠️ Limitations

- **Fragmented files** may be partially recovered or corrupted (carving assumes contiguous data)
- **Original filenames & folders** are lost — files are saved as `recovered_TIMESTAMP_000001.jpg`
- **macOS internal drives** are protected by System Integrity Protection (SIP); use an external USB drive for testing on Mac
- **BitLocker-encrypted drives** on Windows: target the drive letter (e.g., `D`) instead of `PhysicalDriveN` for on-the-fly decryption

---

## 📁 Project Structure

```
byte-recovery/
├── app.py            # GUI desktop app entry point (uses Eel)
├── recovery.py       # Core carving engine + CLI interface
├── build.bat         # Windows .exe build script
├── web/
│   ├── index.html    # App UI layout
│   ├── style.css     # App styling (glassmorphism, dark mode)
│   └── script.js     # Frontend logic & Eel bridge
├── README.md         # This file
└── TUTORIAL.md       # Step-by-step usage guide
```

---

*Developed with ❤️ by **Guru Kannan***
