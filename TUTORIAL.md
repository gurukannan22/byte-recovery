# 🛠️ Byte Recovery Pro — Step-by-Step Guide

> **Developed by Guru Kannan**

Welcome! This guide walks you through everything you need to know to successfully recover deleted files using Byte Recovery Pro.

---

## Step 1: Install Requirements

You need **Python 3.8 or newer**. Check if you have it:
```bash
python3 --version
```

Then install the GUI dependency:

**Windows:**
```cmd
pip install eel
```

**Mac:**
```bash
pip3 install eel --break-system-packages
```

**Linux:**
```bash
pip3 install eel
```

---

## Step 2: Get Administrator / Root Access

Byte Recovery Pro must read raw physical disk data. This requires elevated privileges.

**Windows:**
1. Press the Start menu and type `cmd`
2. Right-click **Command Prompt** → select **Run as administrator**
3. Navigate to the project folder:
   ```cmd
   cd "C:\path\to\byte-recovery"
   ```

**Mac / Linux:**
- You will prepend `sudo` to your command, for example:
  ```bash
  sudo python3 app.py
  ```

---

## Step 3: Identify Your Target Drive

You must provide the correct drive path. Here's how to find it:

### 🪟 Windows
| What to recover from | Drive path to use |
|---|---|
| USB stick showing as `E:` | `E` |
| USB stick showing as `F:` | `F` |
| Whole physical hard drive | `PhysicalDrive0` or `PhysicalDrive1` |
| Disk image file (`.img`, `.dd`) | `C:\path\to\image.img` |

> **Quick Tip:** Run `python recovery.py --list-drives` to list all available drive letters automatically.

You can also find physical drives through **Disk Management** (right-click Start → Disk Management).

---

### 🍎 Mac
1. Open a new Terminal window
2. Run: `diskutil list`
3. You'll see output like:
   ```
   /dev/disk0 (internal, physical)  ← Your main hard drive
   /dev/disk2 (external, physical)  ← A plugged-in USB drive
   ```
4. Use the **raw** path by adding an `r`: `/dev/rdisk2`
   - The `r` prefix gives much faster access

> ⚠️ **Mac Note:** macOS heavily protects the internal drive (`/dev/rdisk0`) with System Integrity Protection (SIP). For best results on Mac, plug in an **external USB drive** and scan that instead.

---

### 🐧 Linux
1. Run: `lsblk`
2. Identify your disk (e.g., `sdb`)
3. Your target path is `/dev/sdb`

---

## Step 4A: Launch the GUI App (Recommended)

The easiest way to use the tool is through the beautiful desktop interface.

**Windows (as Administrator):**
```cmd
python app.py
```

**Mac/Linux (with sudo):**
```bash
sudo python3 app.py
```

The app will open a window. Here's what to do:

1. **Target Drive** — Type your drive path or select from the dropdown
2. **Save Destination** — The folder where recovered files will be saved (default: `./recovered`)
3. **File Filters** — Check specific file types, or leave all unchecked to recover everything
4. Click **Start Deep Scan** and watch the live progress!

---

## Step 4B: Use the CLI Instead (Power Users)

If you prefer the terminal, you can run the CLI directly:

**Interactive Mode (guided prompts):**
```bash
python recovery.py        # Windows
sudo python3 recovery.py  # Mac/Linux
```

**Direct Command Mode:**
```bash
# Recover everything from drive D (Windows)
python recovery.py -d D -o ./recovered

# Recover only JPG and PDF from a USB (Windows)
python recovery.py -d E -t jpg pdf -o ./my_docs

# Scan a disk image file
python recovery.py -d ./backup.img -o ./recovered

# Mac – scan external USB disk
sudo python3 recovery.py -d /dev/rdisk2 -o ./recovered
```

**All available flags:**

| Flag | Description | Example |
|------|-------------|---------|
| `-d` | Target drive path | `-d D` or `-d /dev/rdisk2` |
| `-o` | Output directory | `-o ./recovered` |
| `-m` | Max file size (MB) | `-m 100` |
| `-t` | File type filter | `-t jpg png pdf` |
| `--offset` | Start offset in bytes | `--offset 1073741824` |
| `--limit` | Max bytes to scan | `--limit 10737418240` |
| `--list-drives` | Show drives (Windows only) | |
| `--list-types` | Show all supported types | |

---

## Step 5: Review Recovered Files

Once the scan is complete, open your output folder (e.g., `./recovered`).

**What to expect:**
- Files are named sequentially: `recovered_20260425_180000_000001.jpg`
- Original filenames and folder structure **cannot** be recovered (the file system metadata is gone)
- Subfolders are organized automatically by file type

**💡 Tip — Microsoft Office Files:**  
Modern Office files (`.docx`, `.xlsx`, `.pptx`) are actually ZIP archives. If the tool saves a `.zip` file that you can't open, try renaming it:
- `recovered_0001.zip` → `document.docx`  
- Then open it in Microsoft Word!

---

## Step 6 (Windows Only): Build a Standalone .exe

Want to share the app with others who don't have Python?

1. On your Windows machine, double-click **`build.bat`**
2. It will install the required tools and create a single executable
3. Find the final app at: `dist/ByteRecoveryPro.exe`

Simply right-click the `.exe` → **Run as administrator** to use it!

---

## ❓ Common Issues & Fixes

| Problem | Solution |
|---|---|
| `Permission denied` / `Operation not permitted` | Run with `sudo` (Mac/Linux) or as Administrator (Windows) |
| `No module named 'eel'` | Run `pip install eel` or `pip3 install eel --break-system-packages` on Mac |
| Entered a folder path instead of a drive | Must enter a raw drive path like `/dev/rdisk2` or `D`, not a folder |
| Mac internal drive blocked by SIP | Use an external USB drive for recovery on Mac |
| Recovered `.zip` files won't open | Try renaming to `.docx`, `.xlsx`, or `.pptx` |

---

*Developed with ❤️ by **Guru Kannan***
