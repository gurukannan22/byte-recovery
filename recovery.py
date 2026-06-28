import os
import sys
import ctypes
from pathlib import Path
from datetime import datetime
from typing import BinaryIO, Optional, List, Tuple, Dict, Set

# ANSI Colors for visual representation
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# ═══════════════════════════════════════════════════════════════════════════
# FILE SIGNATURES (Magic Numbers)
# Format: extension: (header_bytes, footer_bytes, max_size_bytes, description)
# ═══════════════════════════════════════════════════════════════════════════
FILE_SIGNATURES: Dict[str, Tuple[bytes, Optional[bytes], int, str]] = {
    # ── Images ────────────────────────────────────────────────────────────
    "jpg":  (b"\xFF\xD8\xFF", b"\xFF\xD9", 50*1024*1024, "JPEG Image"),
    "png":  (b"\x89PNG\r\n\x1a\n", b"IEND\xAE\x42\x60\x82", 50*1024*1024, "PNG Image"),
    "gif":  (b"GIF8", b"\x00\x3B", 10*1024*1024, "GIF Image"),
    "bmp":  (b"BM", None, 20*1024*1024, "BMP Image"),
    "tif":  (b"II*\x00", None, 50*1024*1024, "TIFF Image"),
    "webp": (b"RIFF", None, 20*1024*1024, "WebP Image"),  # RIFF....WEBP pattern inside
    
    # ── Documents ─────────────────────────────────────────────────────────
    "pdf":  (b"%PDF", b"%%EOF", 100*1024*1024, "PDF Document"),
    "doc":  (b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1", None, 50*1024*1024, "Old MS Office"),
    "rtf":  (b"{\rtf1", b"}", 10*1024*1024, "Rich Text"),
    
    # ── Archives ──────────────────────────────────────────────────────────
    "zip":  (b"PK\x03\x04", b"PK\x05\x06", 500*1024*1024, "ZIP Archive"),
    "rar":  (b"Rar!", None, 500*1024*1024, "RAR Archive"),
    "7z":   (b"7z\xBC\xAF'\x1C", None, 500*1024*1024, "7-Zip Archive"),
    "gz":   (b"\x1F\x8B\x08", None, 100*1024*1024, "GZip Archive"),
    
    # ── Audio/Video ───────────────────────────────────────────────────────
    "mp3":  (b"ID3", None, 50*1024*1024, "MP3 Audio"),
    "mp3_nf": (b"\xFF\xFB", None, 50*1024*1024, "MP3 (no ID3)"),  # No ID3 tag
    "mp4":  (b"ftyp", None, 500*1024*1024, "MP4 Video"),  # Usually at offset 4
    "avi":  (b"RIFF", b"AVI ", 2*1024*1024*1024, "AVI Video"),
    "wav":  (b"RIFF", b"WAVE", 200*1024*1024, "WAV Audio"),
    "mkv":  (b"\x1A\x45\xDF\xA3", None, 2*1024*1024*1024, "MKV Video"),
    "flv":  (b"FLV\x01", None, 200*1024*1024, "FLV Video"),
    "ogg":  (b"OggS", None, 200*1024*1024, "OGG Audio/Video"),
    "flac": (b"fLaC", None, 200*1024*1024, "FLAC Audio"),
    
    # ── Executables & DBs ────────────────────────────────────────────────
    "exe":  (b"MZ", None, 100*1024*1024, "Windows Executable"),
    "elf":  (b"\x7fELF", None, 50*1024*1024, "Linux Executable"),
    "db":   (b"SQLite format 3\x00", None, 500*1024*1024, "SQLite Database"),
}

# Office files are ZIP-based - detect by content patterns inside ZIP
OFFICE_PATTERNS: Dict[bytes, str] = {
    b"word/": "docx",
    b"xl/": "xlsx", 
    b"ppt/": "pptx",
    b"AndroidManifest.xml": "apk",
    b"META-INF/": "jar",
}

# ═══════════════════════════════════════════════════════════════════════════
# DEFAULT CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════
DEFAULT_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
CHUNK_SIZE = 512 * 1024                   # 512 KB read buffer  
MAX_SCAN_CHUNK = 4 * 1024                   # Look ahead for footers

# ═══════════════════════════════════════════════════════════════════════════
# WINDOWS RAW DRIVE ACCESS
# ═══════════════════════════════════════════════════════════════════════════

def open_raw_drive_windows(drive_path: str) -> BinaryIO:
    """Open Windows raw drive with proper Win32 API flags. Requires Admin."""
    if sys.platform != 'win32':
        raise OSError("Raw drive access requires Windows")
    
    import msvcrt
    kernel32 = ctypes.windll.kernel32
    
    GENERIC_READ = 0x80000000
    FILE_SHARE_READ = 0x00000001
    FILE_SHARE_WRITE = 0x00000002
    OPEN_EXISTING = 3
    FILE_FLAG_NO_BUFFERING = 0x20000000
    
    # Normalize path
    if len(drive_path) == 1 and drive_path.isalpha():
        path = fr'\\.\{drive_path.upper()}:'
    elif 'physicaldrive' in drive_path.lower():
        drive_num = ''.join(filter(str.isdigit, drive_path))
        path = fr'\\.\PhysicalDrive{drive_num}'
    elif drive_path.startswith('\\\\.\\'):
        path = drive_path
    else:
        path = fr'\\.\{drive_path}'
    
    hDevice = kernel32.CreateFileW(
        path, GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE,
        None, OPEN_EXISTING, FILE_FLAG_NO_BUFFERING, None
    )
    if hDevice == -1:
        err = ctypes.get_last_error()
        if err == 5:
            raise PermissionError(f"Access denied to {path}. Run as Administrator.")
        raise OSError(f"Cannot open {path}. Error {err}")
    
    fd = msvcrt.open_osfhandle(hDevice, os.O_RDONLY)
    return os.fdopen(fd, 'rb')


def get_available_drives() -> List[str]:
    """Return list of available Windows drive letters."""
    if sys.platform != 'win32':
        return []
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in range(26):
        if bitmask & (1 << letter):
            drives.append(chr(ord('A') + letter))
    return drives


def get_available_drives_info() -> List[Dict[str, str]]:
    """Return list of available drives with description, size, and type."""
    drives = []
    if sys.platform == 'win32':
        # 1. Logical Drives
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in range(26):
            if bitmask & (1 << letter):
                drive_letter = chr(ord('A') + letter)
                volume_name = ctypes.create_unicode_buffer(1024)
                file_system_name = ctypes.create_unicode_buffer(1024)
                res = ctypes.windll.kernel32.GetVolumeInformationW(
                    f"{drive_letter}:\\",
                    volume_name, len(volume_name),
                    None, None, None,
                    file_system_name, len(file_system_name)
                )
                name = volume_name.value if (res and volume_name.value) else "Local Disk"
                drives.append({
                    "path": f"{drive_letter}:",
                    "name": f"Logical Drive {drive_letter}: ({name})",
                    "type": "logical"
                })
        # 2. Physical Drives via PowerShell
        import subprocess
        import json
        try:
            cmd = ["powershell", "-Command", "Get-CimInstance Win32_DiskDrive | Select-Object DeviceID, Model, Size | ConvertTo-Json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                try:
                    disks = json.loads(result.stdout)
                    if isinstance(disks, dict):
                        disks = [disks]
                    for disk in disks:
                        dev_id = disk.get("DeviceID", "")
                        model = disk.get("Model", "Unknown Disk")
                        size_bytes = disk.get("Size", 0)
                        if size_bytes:
                            size_gb = size_bytes / (1024**3)
                            size_str = f"{size_gb:.1f} GB"
                        else:
                            size_str = "Unknown Size"
                        if dev_id:
                            drives.append({
                                "path": dev_id,
                                "name": f"Physical Disk {dev_id.split('L')[-1]} - {model} ({size_str})",
                                "type": "physical"
                            })
                except Exception:
                    pass
        except Exception:
            # Fallback to WMIC
            try:
                cmd = ["wmic", "diskdrive", "get", "DeviceID,Caption,Size", "/format:csv"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    for line in lines[1:]:
                        parts = line.strip().split(",")
                        if len(parts) >= 4:
                            dev_id = parts[2].strip()
                            caption = parts[1].strip()
                            size = parts[3].strip()
                            if dev_id and caption:
                                try:
                                    size_gb = int(size) / (1024**3)
                                    size_str = f"{size_gb:.1f} GB"
                                except:
                                    size_str = "Unknown Size"
                                drives.append({
                                    "path": dev_id,
                                    "name": f"Physical Disk {dev_id.split('L')[-1]} - {caption} ({size_str})",
                                    "type": "physical"
                                })
            except Exception:
                pass
    elif sys.platform == 'darwin':
        import subprocess
        import re
        try:
            result = subprocess.run(["diskutil", "list"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                sections = result.stdout.split("\n\n")
                for section in sections:
                    lines = section.strip().split("\n")
                    if not lines:
                        continue
                    first_line = lines[0]
                    match = re.match(r'(/dev/disk\d+)\s+\(([^)]+)\):', first_line)
                    if match:
                        dev_path = match.group(1)
                        desc = match.group(2)
                        size_str = "Unknown Size"
                        for line in lines[1:]:
                            if "*" in line or "+" in line:
                                size_match = re.search(r'[*+]([\d.]+\s+[KMGTP]B)', line)
                                if size_match:
                                    size_str = size_match.group(1)
                                    break
                        raw_path = dev_path.replace("/dev/disk", "/dev/rdisk")
                        drives.append({
                            "path": raw_path,
                            "name": f"{raw_path} ({desc}, {size_str})",
                            "type": "physical"
                        })
        except:
            pass
        if not drives:
            drives = [
                {"path": "/dev/rdisk0", "name": "/dev/rdisk0 (System Drive)", "type": "physical"},
                {"path": "/dev/rdisk1", "name": "/dev/rdisk1 (Secondary Drive)", "type": "physical"},
                {"path": "/dev/rdisk2", "name": "/dev/rdisk2 (External/USB)", "type": "physical"}
            ]
    else:
        import subprocess
        try:
            result = subprocess.run(["lsblk", "-o", "NAME,SIZE,TYPE,MODEL", "-n", "-J"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                for dev in data.get("blockdevices", []):
                    name = dev.get("name", "")
                    size = dev.get("size", "")
                    dtype = dev.get("type", "")
                    model = dev.get("model", "Disk")
                    if name and dtype in ("disk", "loop"):
                        drives.append({
                            "path": f"/dev/{name}",
                            "name": f"/dev/{name} - {model} ({size})",
                            "type": "physical"
                        })
        except:
            pass
        if not drives:
            drives = [
                {"path": "/dev/sda", "name": "/dev/sda (Main Disk)", "type": "physical"},
                {"path": "/dev/sdb", "name": "/dev/sdb (External/USB)", "type": "physical"}
            ]
    return drives


# ═══════════════════════════════════════════════════════════════════════════
# RECOVERY ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class RecoveryStats:
    def __init__(self):
        self.scanned = 0
        self.found = 0
        self.recovered = 0
        self.errors = 0
        self.by_type: Dict[str, int] = {}
    
    def print_summary(self):
        print("\n" + "="*60)
        print("RECOVERY SUMMARY")
        print("="*60)
        print(f"Bytes scanned:  {self.scanned:,} ({self.scanned / (1024**3):.2f} GB)")
        print(f"Files found:    {self.found}")
        print(f"Files saved:    {self.recovered}")
        print(f"Errors:         {self.errors}")
        if self.by_type:
            print("\nBy file type:")
            for ext, count in sorted(self.by_type.items(), key=lambda x: -x[1]):
                print(f"  {ext:10s} {count:4d}")


class RecoveryEngine:
    def __init__(self, drive_path: str, output_dir: str, max_size: int = DEFAULT_MAX_FILE_SIZE,
                 file_types: Optional[Set[str]] = None, verbose: bool = False, progress_callback=None):
        self.drive_path = drive_path
        self.output_dir = Path(output_dir)
        self.max_size = max_size
        self.file_types = file_types
        self.verbose = verbose
        self.progress_callback = progress_callback
        self.stats = RecoveryStats()
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def log(self, msg: str):
        if self.verbose:
            print(f"[DBG] {msg}")
    
    def _detect_file_type(self, data: bytes, offset: int) -> Optional[Tuple[str, bytes, Optional[bytes], int, str]]:
        """Check if data at offset matches a known signature."""
        for ext, (header, footer, max_sz, desc) in FILE_SIGNATURES.items():
            if self.file_types and ext not in self.file_types:
                continue
            end = offset + len(header)
            if end > len(data):
                continue
            if data[offset:end] == header:
                # Special handling: RIFF files - check sub-type for webp/wav/avi
                if header == b"RIFF" and len(data) > offset + 12:
                    sub_type = data[offset+8:offset+12]
                    if b"WEBP" in sub_type:
                        return (ext, data[offset:offset+4], footer, max_sz, "WebP Image")
                    elif b"WAVE" in sub_type:
                        return ("wav", data[offset:offset+4], footer, max_sz, "WAV Audio")
                    elif b"AVI " in sub_type:
                        return ("avi", data[offset:offset+4], footer, max_sz, "AVI Video")
                # For ZIP-based files, peek ahead for office patterns
                if ext == "zip":
                    ahead = data[offset:offset+4096]
                    for pat, office_ext in OFFICE_PATTERNS.items():
                        if pat in ahead:
                            if not self.file_types or office_ext in self.file_types:
                                return (office_ext, header, footer, max_sz, f"{office_ext.upper()} (ZIP-based)")
                return (ext, header, footer, max_sz, desc)
        return None
    
    def _recover_file(self, fh: BinaryIO, start_offset: int, ext: str, header: bytes,
                     footer: Optional[bytes], max_size: int, desc: str) -> bool:
        """Recover a single file from the given offset, handling sector alignment."""
        old_pos = None
        try:
            old_pos = fh.tell()
        except OSError:
            pass
            
        try:
            SECTOR_SIZE = 512
            is_windows_raw = (sys.platform == 'win32' and 
                              (self.drive_path[0].isalpha() or 
                               'physicaldrive' in self.drive_path.lower()))
            
            if is_windows_raw:
                aligned_start = (start_offset // SECTOR_SIZE) * SECTOR_SIZE
                skip = start_offset - aligned_start
            else:
                aligned_start = start_offset
                skip = 0
                
            try:
                fh.seek(aligned_start)
            except OSError:
                return False
                
            actual_max = min(max_size, self.max_size)
            buffer = bytearray()
            chunk_size = 64 * 1024
            remaining = actual_max + skip
            
            found_footer = False
            footer_pos = -1
            
            while remaining > 0:
                to_read = min(chunk_size, remaining)
                if is_windows_raw and to_read % SECTOR_SIZE != 0:
                    to_read = ((to_read + SECTOR_SIZE - 1) // SECTOR_SIZE) * SECTOR_SIZE
                    
                data = fh.read(to_read)
                if not data:
                    break
                    
                buffer.extend(data)
                remaining -= len(data)
                
                if footer:
                    search_start = max(skip, len(buffer) - len(data) - len(footer))
                    idx = buffer.find(footer, search_start)
                    if idx != -1:
                        footer_pos = idx + len(footer)
                        found_footer = True
                        break
            
            if found_footer:
                file_data = bytes(buffer[skip:footer_pos])
            else:
                file_data = bytes(buffer[skip:skip + actual_max])
                
            if not file_data or len(file_data) < len(header):
                return False
                
            if not file_data.startswith(header):
                return False
                
            self.stats.found += 1
            seq = self.stats.found
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recovered_{ts}_{seq:06d}.{ext}"
            
            # Save files organized by extension subdirectory
            type_dir = self.output_dir / ext
            type_dir.mkdir(parents=True, exist_ok=True)
            out_path = type_dir / filename
            
            try:
                with open(out_path, 'wb') as out_fh:
                    out_fh.write(file_data)
                self.stats.recovered += 1
                self.stats.by_type[ext] = self.stats.by_type.get(ext, 0) + 1
                print(f"[+] {desc}: {ext}/{filename} ({len(file_data):,} bytes)")
                return True
            except OSError as e:
                self.stats.errors += 1
                self.log(f"Error writing {filename}: {e}")
                return False
        finally:
            if old_pos is not None:
                try:
                    fh.seek(old_pos)
                except OSError:
                    pass
    
    def scan(self, start_offset: int = 0, limit: Optional[int] = None):
        """Scan the drive for file signatures, keeping disk operations aligned."""
        print(f"\n{Colors.OKCYAN}{Colors.BOLD}╔════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.OKCYAN}{Colors.BOLD}║{Colors.ENDC} {Colors.OKBLUE}Target Drive:{Colors.ENDC} {self.drive_path: <43} {Colors.OKCYAN}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{Colors.OKCYAN}{Colors.BOLD}║{Colors.ENDC} {Colors.OKBLUE}Destination:{Colors.ENDC}  {str(self.output_dir.absolute()): <43} {Colors.OKCYAN}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{Colors.OKCYAN}{Colors.BOLD}║{Colors.ENDC} {Colors.OKBLUE}Start Offset:{Colors.ENDC} {f'{start_offset:,} bytes': <43} {Colors.OKCYAN}{Colors.BOLD}║{Colors.ENDC}")
        if self.file_types:
            filter_str = ', '.join(sorted(self.file_types))
            print(f"{Colors.OKCYAN}{Colors.BOLD}║{Colors.ENDC} {Colors.OKBLUE}Filtering:{Colors.ENDC}    {filter_str[:43]: <43} {Colors.OKCYAN}{Colors.BOLD}║{Colors.ENDC}")
        print(f"{Colors.OKCYAN}{Colors.BOLD}╚════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")
        
        # Open drive
        try:
            if os.path.isdir(self.drive_path):
                raise ValueError(f"Target cannot be a directory ('{self.drive_path}'). You must specify a raw drive or a disk image file.")
                
            if sys.platform == 'win32' and (self.drive_path[0].isalpha() or 
                                               'physicaldrive' in self.drive_path.lower()):
                fh = open_raw_drive_windows(self.drive_path)
            else:
                fh = open(self.drive_path, 'rb')
        except PermissionError as e:
            raise PermissionError(f"Permission denied. Did you forget to run with sudo (Mac/Linux) or as Administrator (Windows)?\n{e}")
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise Exception(f"Cannot open drive: {e}")
        
        try:
            SECTOR_SIZE = 512
            is_windows_raw = (sys.platform == 'win32' and 
                              (self.drive_path[0].isalpha() or 
                               'physicaldrive' in self.drive_path.lower()))
            
            if is_windows_raw:
                aligned_start = (start_offset // SECTOR_SIZE) * SECTOR_SIZE
                skip_bytes = start_offset - aligned_start
            else:
                aligned_start = start_offset
                skip_bytes = 0
                
            fh.seek(aligned_start)
            buffer = b''
            offset = start_offset
            bytes_read = 0
            first_chunk = True
            
            while True:
                if limit and bytes_read >= limit:
                    break
                
                to_read = min(CHUNK_SIZE, limit - bytes_read) if limit else CHUNK_SIZE
                if is_windows_raw and to_read % SECTOR_SIZE != 0:
                    to_read = ((to_read + SECTOR_SIZE - 1) // SECTOR_SIZE) * SECTOR_SIZE
                    
                data = fh.read(to_read)
                if not data:
                    break
                
                bytes_read += len(data)
                self.stats.scanned = bytes_read
                
                if first_chunk:
                    if skip_bytes > 0:
                        data = data[skip_bytes:]
                    first_chunk = False
                
                # Combine with leftover from previous chunk
                scan_data = buffer + data
                scan_limit = len(scan_data) - 64  # Keep tail for boundary signatures
                if scan_limit <= 0:
                    buffer = scan_data
                    continue
                
                # Scan for signatures
                i = 0
                while i < scan_limit:
                    match = self._detect_file_type(scan_data, i)
                    if match:
                        ext, header, footer, max_sz, desc = match
                        abs_offset = offset - len(buffer) + i
                        self._recover_file(fh, abs_offset, ext, header, footer, max_sz, desc)
                        i += len(header) + 16  # Skip ahead
                    else:
                        i += 1
                
                buffer = scan_data[scan_limit:]
                offset += len(data)
                
                # Progress update
                if bytes_read % (50 * 1024 * 1024) < CHUNK_SIZE:
                    mb = bytes_read / (1024 * 1024)
                    progress_text = f"\r{Colors.OKGREEN}► Scanning...{Colors.ENDC} {Colors.BOLD}{mb:,.1f} MB{Colors.ENDC} processed | "
                    progress_text += f"{Colors.OKCYAN}Files Found: {self.stats.found}{Colors.ENDC} | "
                    progress_text += f"{Colors.OKBLUE}Saved: {self.stats.recovered}{Colors.ENDC}"
                    sys.stdout.write(progress_text)
                    sys.stdout.flush()
                    
                    if hasattr(self, 'progress_callback') and self.progress_callback:
                        self.progress_callback(bytes_read, self.stats.found, self.stats.recovered)
        
        finally:
            fh.close()
            print()  # New line after progress

if __name__ == "__main__":
    import argparse
    
    ASCII_ART = f"""{Colors.OKBLUE}{Colors.BOLD}
    ____        __         ____                                
   / __ )__  __/ /____    / __ \\___  _________ _   _____  _______  __
  / __  / / / / __/ _ \\  / /_/ / _ \\/ ___/ __ \\ | / / _ \\/ ___/ / / /
 / /_/ / /_/ / /_/  __/ / _, _/  __/ /__/ /_/ / |/ /  __/ /  / /_/ / 
/_____/\\__, /\\__/\\___/ /_/ |_|\\___/\\___/\\____/|___/\\___/_/   \\__, /  
      /____/                                                /____/   
{Colors.ENDC}"""

    print(ASCII_ART)
    print(f"{Colors.OKCYAN}{Colors.BOLD}         A File Carving & Recovery Utility{Colors.ENDC}\n")
    
    parser = argparse.ArgumentParser(
        description="Recover deleted files from raw drives using file carving."
    )
    parser.add_argument("-d", "--drive", help="Target drive (e.g., C, PhysicalDrive1, or .\\image.dd)")
    parser.add_argument("-o", "--output", default="./recovered", help="Output directory (default: ./recovered)")
    parser.add_argument("-m", "--max-size", type=int, default=50, help="Max file size in MB (default: 50)")
    parser.add_argument("-t", "--types", nargs="+", help="Only recover specific types (e.g., jpg png pdf)")
    parser.add_argument("--offset", type=int, default=0, help="Start at byte offset")
    parser.add_argument("--limit", type=int, help="Stop after N bytes")
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug output")
    parser.add_argument("--list-drives", action="store_true", help="Show available drives")
    parser.add_argument("--list-types", action="store_true", help="Show supported file types")
    
    args = parser.parse_args()
    
    # Handle info flags
    if args.list_drives:
        drives_info = get_available_drives_info()
        print("Available drives:")
        for d in drives_info:
            print(f"  Path: {d['path']: <20} | Name: {d['name']}")
        if sys.platform == 'win32':
            print("\nUse 'PhysicalDriveN' for physical disks (e.g., PhysicalDrive0)")
        elif sys.platform == 'darwin':
            print("\nUse the raw disk path (e.g., /dev/rdisk2) for maximum scan speed.")
        sys.exit(0)
    
    if args.list_types:
        print("Supported file types:")
        seen = set()
        for ext, (_, _, _, desc) in sorted(FILE_SIGNATURES.items(), key=lambda x: x[1][3]):
            if desc not in seen:
                seen.add(desc)
                print(f"  {ext:10s} - {desc}")
        print("\nOffice types detected inside ZIP archives:")
        for pat, ext in OFFICE_PATTERNS.items():
            print(f"  {ext:10s} - (contains '{pat.decode('utf-8', errors='replace')}')")
        sys.exit(0)
    
    # Interactive mode if no drive specified
    target_drive = args.drive
    output_dir = args.output
    max_size = args.max_size * 1024 * 1024
    
    if not target_drive:
        if sys.platform == 'win32':
            print(f"{Colors.WARNING}Interactive Mode Started (Run as Administrator!){Colors.ENDC}\n")
            drives = get_available_drives()
            if drives:
                print(f"{Colors.OKGREEN}Available Windows Drives: {Colors.ENDC}{', '.join(drives)}\n")
            example_prompt = f"{Colors.OKBLUE}D{Colors.ENDC} or {Colors.OKBLUE}PhysicalDrive0{Colors.ENDC}"
        elif sys.platform == 'darwin':
            print(f"{Colors.WARNING}Interactive Mode Started (Run with sudo!){Colors.ENDC}\n")
            print(f"{Colors.OKGREEN}Tip: Run 'diskutil list' in another terminal to find your drive.{Colors.ENDC}\n")
            example_prompt = f"{Colors.OKBLUE}/dev/rdisk2{Colors.ENDC}"
        else:
            print(f"{Colors.WARNING}Interactive Mode Started (Run with sudo!){Colors.ENDC}\n")
            print(f"{Colors.OKGREEN}Tip: Run 'lsblk' in another terminal to find your drive.{Colors.ENDC}\n")
            example_prompt = f"{Colors.OKBLUE}/dev/sdb{Colors.ENDC}"
            
        target_drive = input(f"{Colors.BOLD}Enter target drive{Colors.ENDC} (e.g., {example_prompt}): ").strip()
        while not target_drive:
            target_drive = input(f"{Colors.FAIL}Drive is required:{Colors.ENDC} ").strip()
        
        out = input(f"{Colors.BOLD}Enter destination directory{Colors.ENDC} for recovered files [default: {Colors.OKBLUE}./recovered{Colors.ENDC}]: ").strip()
        if out:
            output_dir = out
        
        types_input = input(f"{Colors.BOLD}Filter by types{Colors.ENDC} (space separated, or '{Colors.OKBLUE}all{Colors.ENDC}') [default: all]: ").strip()
        if types_input and types_input.lower() != 'all':
            args.types = types_input.split()
    
    # Run recovery
    file_types = set(args.types) if args.types else None
    
    engine = RecoveryEngine(
        drive_path=target_drive,
        output_dir=output_dir,
        max_size=max_size,
        file_types=file_types,
        verbose=args.verbose
    )
    
    engine.scan(start_offset=args.offset, limit=args.limit)
    engine.stats.print_summary()
