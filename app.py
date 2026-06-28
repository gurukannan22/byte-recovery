import eel
import os
import sys
import threading
import ctypes
from recovery import RecoveryEngine, get_available_drives_info, FILE_SIGNATURES

# Initialize eel with the web directory
eel.init('web')

engine_instance = None

@eel.expose
def get_drives():
    return get_available_drives_info()

@eel.expose
def check_admin():
    if sys.platform == 'win32':
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    else:
        try:
            return os.getuid() == 0
        except:
            return False

@eel.expose
def get_file_types():
    return list(FILE_SIGNATURES.keys())

@eel.expose
def start_recovery(drive, output_dir, types):
    global engine_instance
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            return {"status": "error", "message": f"Could not create output dir: {e}"}
            
    def progress_callback(bytes_scanned, files_found, files_saved):
        # Update UI progress
        mb_scanned = round(bytes_scanned / (1024 * 1024), 2)
        try:
            eel.update_progress(mb_scanned, files_found, files_saved)()
        except:
            pass # Ignore if UI is closed
            
    engine_instance = RecoveryEngine(
        drive_path=drive,
        output_dir=output_dir,
        file_types=set(types) if types and len(types) > 0 else None,
        progress_callback=progress_callback
    )
    
    def run_scan():
        try:
            engine_instance.scan()
            eel.recovery_finished(engine_instance.stats.found, engine_instance.stats.recovered)()
        except Exception as e:
            eel.recovery_error(str(e))()

    # Run scanning logic in a background thread so it doesn't block the UI
    threading.Thread(target=run_scan, daemon=True).start()
    return {"status": "started"}

if __name__ == '__main__':
    # Start the app, attempting to open a Chrome window of size 900x700
    try:
        eel.start('index.html', size=(900, 700), mode='chrome')
    except EnvironmentError:
        # Fallback to default browser if Chrome is not found
        eel.start('index.html', size=(900, 700), mode='default')
