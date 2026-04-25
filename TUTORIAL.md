# 🛠️ Step-by-Step Guide: How to Use Byte Recovery

Welcome to the Byte Recovery tool! This guide will walk you through exactly how to use this tool to recover deleted files from your hard drives or USB sticks.

---

## Step 1: Preparation 
Before you start, make sure you have two things:
1. **Python 3 installed** on your system.
2. **Administrator Rights**. Windows does not allow normal users to read raw disks. You *must* run the tool as an Administrator.

**How to open Command Prompt as Administrator:**
1. Click the Windows Start menu.
2. Type `cmd`.
3. Right-click on **Command Prompt** and select **Run as administrator**.
4. Navigate to the folder where the tool is located:
   ```cmd
   cd C:\path\to\byte-recovery
   ```

---

## Step 2: Identify Your Drive
You need to know the name/path of the drive you want to scan.

- **If it has a Drive Letter (like a USB stick):**
  If you plug in a USB stick and it shows up as `E:`, then your drive path is `E`. 
  *(The script will automatically format this into the correct Windows path `\\.\E:`)*.

- **If you are scanning an entire Physical Hard Drive:**
  If you want to scan your whole primary hard drive or a drive without a letter:
  1. Right-click the Start Menu and select **Disk Management**.
  2. Look at the bottom half of the screen for "Disk 0", "Disk 1", etc.
  3. Your drive path will be `PhysicalDrive0` or `PhysicalDrive1`.

> **Pro Tip:** You can also run `python recovery.py --list-drives` to see a quick list of available drive letters!

---

## Step 3: Running the Tool (Interactive Mode)
The easiest way to use the tool is to let it ask you for the details. 

1. Simply run the script with no arguments:
   ```cmd
   python recovery.py
   ```
2. **Enter the drive:** Type your drive letter (e.g., `E`) or physical drive (e.g., `PhysicalDrive1`) and press Enter.
3. **Enter destination:** Press Enter to use the default `./recovered` folder, or type a custom path like `C:\RecoveryBackup`.
4. **Filter by types:** If you only want images, type `jpg png`. If you want everything, just press Enter.

The tool will now display a nice scanning UI and show you the progress as it recovers files!

---

## Step 4: Advanced CLI Mode (For Power Users)
If you prefer running a single command without prompts, you can use flags.

**Basic Recovery (All files from Drive D):**
```cmd
python recovery.py -d D -o ./my_recovered_files
```

**Recovering ONLY Photos & Videos:**
```cmd
python recovery.py -d D -t jpg png mp4 avi
```

**Skipping the first 10 Gigabytes of a large drive:**
*(10GB = 10737418240 bytes)*
```cmd
python recovery.py -d PhysicalDrive1 --offset 10737418240
```

---

## Step 5: Understanding Your Recovered Files
Once the scan finishes, go to your output directory (e.g., `./recovered`).

> **Warning:** Because this tool bypasses the file system and reads raw data off the disk, **the original file names and folders are lost forever.**

- Files will be named sequentially: `recovered_20260425_180000_000001.jpg`.
- **Note on Modern Office Files:** Modern Microsoft Office files like `.docx`, `.xlsx`, and `.pptx` are actually just ZIP archives in disguise. If the tool recovers a `.zip` file, try renaming the extension to `.docx` or `.xlsx` and opening it! 
