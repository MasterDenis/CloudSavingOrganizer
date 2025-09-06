import os
import tkinter as tk
from tkinter import filedialog, simpledialog
import subprocess
import re
import shutil
import time
import sys

# --- UTILITY FUNCTIONS ---

def is_junction(path):
    """
    Checks if a given path is a directory junction (reparse point) on Windows.
    This is more reliable than os.path.islink for junctions created with mklink /J.
    """
    try:
        # The reparse point attribute for a junction is 1024
        return bool(os.stat(path).st_file_attributes & 1024)
    except (OSError, AttributeError):
        # OSError if path doesn't exist, AttributeError on non-Windows platforms
        return False

def get_user_choice():
    """
    Displays a Tkinter window to ask the user for their desired action.
    Returns 'add', 'run', or exits the script.
    """
    choice = ""
    
    def on_add():
        nonlocal choice
        choice = 'add'
        root.destroy()

    def on_run():
        nonlocal choice
        choice = 'run'
        root.destroy()
        
    def on_cancel():
        nonlocal choice
        choice = 'exit'
        root.destroy()

    root = tk.Tk()
    root.title("Choose an Action")

    # Center the window
    window_width = 350
    window_height = 120
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))
    root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")


    label = tk.Label(root, text="What would you like to do?", font=('Helvetica', 12))
    label.pack(pady=10)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=5)

    add_btn = tk.Button(btn_frame, text="Add a New Save Folder", command=on_add, width=20)
    add_btn.pack(side=tk.LEFT, padx=10)

    run_btn = tk.Button(btn_frame, text="Run Maintenance", command=on_run, width=20)
    run_btn.pack(side=tk.LEFT, padx=10)
    
    root.protocol("WM_DELETE_WINDOW", on_cancel)
    root.mainloop()

    if choice == 'exit':
        print("Operation cancelled by user.")
        sys.exit()
        
    return choice

def add_command_if_not_exists(filepath, command_to_add, path_to_check):
    """
    Reads a file and adds a command if no command for the specified path exists.
    """
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        with open(filepath, 'rb+') as f:
            f.seek(-1, os.SEEK_END)
            if f.read() != b'\n':
                f.write(b'\n')

    existing_commands = []
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            existing_commands = file.readlines()

    path_found = any(f'"{path_to_check}"' in cmd for cmd in existing_commands)

    if not path_found:
        print(f"Adding new command to {os.path.basename(filepath)} for path: {path_to_check}")
        with open(filepath, 'a') as file:
            file.write(command_to_add + "\n")
    else:
        print(f"Command for path {path_to_check} already exists in {os.path.basename(filepath)}. Skipping.")

def run_failsafe_check_and_move(locations_file_path, saves_folder_path):
    """
    Reads the locations.bat file and fixes any original folders that were not correctly moved.
    """
    print("\n--- Running Fail-Safe Check ---")
    if not os.path.exists(locations_file_path):
        print("locations.bat not found. Skipping fail-safe check.")
        return

    with open(locations_file_path, 'r') as file:
        commands = file.readlines()

    link_pattern = re.compile(r'mklink /J "(.+?)" "(.+?)"')

    for command in commands:
        match = link_pattern.search(command)
        if not match: continue

        original_path, new_path_target = match.groups()

        # A folder is "unmoved" if it exists as a directory but IS NOT a junction.
        if os.path.isdir(original_path) and not is_junction(original_path):
            print(f"FAIL-SAFE: Found an unmoved original folder: {original_path}")
            
            # Check if the target location in SAVES already exists
            if os.path.exists(new_path_target):
                print(f"           Target '{os.path.basename(new_path_target)}' already exists in SAVES.")
                print(f"           Assuming data is safe, removing the original folder to allow linking.")
                try:
                    shutil.rmtree(original_path)
                    print(f"SUCCESS: Removed redundant original folder '{original_path}'.")
                except Exception as e:
                    print(f"ERROR: Could not remove original folder '{original_path}'. Reason: {e}")
            else:
                # Target does not exist, so we can safely move the original folder.
                print(f"           Target does not exist in SAVES. Moving folder.")
                os.makedirs(os.path.dirname(new_path_target), exist_ok=True)
                try:
                    shutil.move(original_path, new_path_target)
                    print(f"SUCCESS: Safely moved folder to {new_path_target}")
                except Exception as e:
                    print(f"ERROR during fail-safe move for {original_path}. Reason: {e}")

    print("--- Fail-Safe Check Complete ---\n")


# --- MAIN SCRIPT EXECUTION ---

# 0. Get user's desired action
action = get_user_choice()

# 1. Setup Directories and Files
script_dir = os.path.dirname(__file__)
directories_folder = os.path.join(script_dir, "Directories")
saves_folder = os.path.join(script_dir, "SAVES")

os.makedirs(directories_folder, exist_ok=True)
os.makedirs(saves_folder, exist_ok=True)

deletions_file = os.path.join(directories_folder, "deletions.bat")
locations_file = os.path.join(directories_folder, "locations.bat")

for f in [deletions_file, locations_file]:
    if not os.path.exists(f):
        open(f, 'w').close()
        print(f"Created empty file: {os.path.basename(f)}")

# 2. Process based on user choice
if action == 'add':
    print("\n--- Adding New Save Folder ---")
    root = tk.Tk()
    root.withdraw()
    original_folder = filedialog.askdirectory(title="Select a folder to move to SAVES")

    if not original_folder:
        print("No folder selected. Aborting 'add' operation.")
    elif not os.path.exists(original_folder):
        print(f"Error: The selected folder '{original_folder}' does not exist.")
    elif is_junction(original_folder):
         print(f"The selected path '{original_folder}' is already a link. No new action taken.")
    else:
        new_folder_location = os.path.join(saves_folder, os.path.basename(original_folder))
        
        deletion_cmd = f'RD /S /Q "{original_folder}"'
        location_cmd = f'mklink /J "{original_folder}" "{new_folder_location}"'

        add_command_if_not_exists(deletions_file, deletion_cmd, original_folder)
        add_command_if_not_exists(locations_file, location_cmd, original_folder)

        retries = 3
        delay_seconds = 5
        for i in range(retries):
            try:
                print(f"Attempting to move '{original_folder}' to '{new_folder_location}'...")
                shutil.move(original_folder, new_folder_location)
                print("Move successful.")
                break
            except PermissionError as e:
                if i < retries - 1:
                    print(f"Warning: Could not move folder. Retrying in {delay_seconds} seconds...")
                    time.sleep(delay_seconds)
                else:
                    print("\n" + "="*80)
                    print("FATAL ERROR: Could not move folder. A file is locked by another program.")
                    print(f"DETAILS: {e}")
                    print("ACTION: Close the application using the folder and run this script again.")
                    print("="*80 + "\n")
                    sys.exit(1)
            except Exception as e:
                print(f"ERROR: An unexpected error occurred during move. Reason: {e}")
                sys.exit(1)

elif action == 'run':
    print("\n--- Running Maintenance Only ---")

# 3. Run the Fail-Safe Check (always runs)
run_failsafe_check_and_move(locations_file, saves_folder)

# 4. Execute Batch Files (always runs)
print("Executing batch files...")
try:
    print("Running locations.bat (Pass 1)...")
    subprocess.run(["cmd.exe", "/c", "call", locations_file], check=True, capture_output=True, text=True)
    
    print("Running deletions.bat...")
    subprocess.run(["cmd.exe", "/c", "call", deletions_file], check=True, capture_output=True, text=True)
    
    print("Running locations.bat (Pass 2)...")
    subprocess.run(["cmd.exe", "/c", "call", locations_file], check=True, capture_output=True, text=True)
    
    print("\nScript finished successfully.")

except subprocess.CalledProcessError as e:
    # Batch files often exit with non-zero status even on success (e.g., if a link already exists),
    # so we don't treat all errors as fatal. We print the output for inspection.
    print(f"Info: A batch file finished with a non-zero status (this can be normal).")
    if e.stdout:
        print(f"STDOUT:\n{e.stdout}")
    if e.stderr:
        print(f"STDERR:\n{e.stderr}")
    print("\nScript finished.")

except FileNotFoundError:
    print("Error: 'cmd.exe' not found. This script is designed for Windows.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
