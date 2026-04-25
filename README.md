# Byte Recovery Tool

A simple and effective file recovery tool built in Python. This tool uses a technique known as **File Carving**, which means it bypasses the file system entirely (like NTFS or FAT32) and reads the raw bytes on the disk to find hidden or deleted files based on their file signatures (Magic Numbers).

## Features
- Recovers deleted files directly from physical drives or disk image files (`.img`, `.dd`).
- Supports recovering almost all common file types:
  - **Images**: `.jpg`, `.png`, `.gif`, `.bmp`, `.tif`, `.webp`
  - **Documents**: `.pdf`, `.doc`, `.xls`, `.ppt`, `.rtf` (Note: `.docx`, `.xlsx`, etc. are recovered as `.zip`)
  - **Archives**: `.zip`, `.rar`, `.7z`, `.gz`, `.tar`
  - **Media**: `.mp3`, `.mp4`, `.avi`, `.wav`, `.mkv`, `.flv`
  - **Executables & DBs**: `.exe`, `.sqlite`
- Cross-platform, but fully supports Windows raw drive access (e.g., `\\.\C:`).

## Prerequisites
- **Python 3.x** installed on your system.
- **Administrator Privileges**: On Windows, accessing physical raw drives requires running the terminal/command prompt as an Administrator.

## How to Run

**Requires Administrator privileges** - Right-click Command Prompt/PowerShell and select "Run as administrator".

### Interactive Mode (Recommended)
```cmd
python recovery.py
```

### CLI Mode
```cmd
python recovery.py -d D -o ./recovered
```

**Options:**
| Flag | Description |
|------|-------------|
| `-d, --drive` | Drive letter (e.g., `D`) or `PhysicalDriveN` |
| `-o, --output` | Output directory (default: `./recovered`) |
| `-m, --max-size` | Max file size in MB (default: 50) |
| `-t, --types` | Filter by file types (e.g., `jpg png pdf`) |
| `--offset` | Start at byte offset |
| `--limit` | Stop after N bytes |
| `--list-drives` | Show available drives |
| `--list-types` | Show supported file types |

**Examples:**
```cmd
# Recover only images from USB drive D
python recovery.py -d D -t jpg png gif bmp -o ./photos

# Scan first 10GB of physical drive 0, max 100MB files
python recovery.py -d PhysicalDrive0 -m 100 --limit 10737418240

# Show available drives
python recovery.py --list-drives

# List supported file types
python recovery.py --list-types
```

## How it Works
When a file is deleted on Windows, the OS marks the space as "available" in the Master File Table (MFT), but the actual data remains until overwritten.

This tool uses **file carving**:
1. Opens the raw disk using Win32 API (requires Admin)
2. Scans disk in 512KB chunks for known **magic numbers** (file signatures)
3. When a header is found, reads until the **footer** is detected or max size reached
4. Handles signatures that span chunk boundaries
5. Auto-detects Office/ZIP-based formats (docx, xlsx, etc.) by content inspection

**Key improvements:**
- Proper Windows raw drive access via `CreateFileW` with `FILE_FLAG_NO_BUFFERING`
- 512KB read chunks (not 512 bytes) for much faster scanning
- Cross-boundary signature detection prevents missed files
- Footer detection for accurate file size (JPG, PDF, ZIP, etc.)
- Type filtering and scan limits for targeted recovery

## Limitations
- Fragmented files might not be recovered correctly (File Carving expects the data to be contiguous on the disk).
- Original file names are lost (recovered files will be named `recovered_1.jpg`, `recovered_2.pdf`, etc.) because the file system metadata is ignored.
