import os
import tkinter as tk
from tkinter import filedialog

directories = os.path.join(os.path.dirname(__file__), "Directories")
if not os.path.exists(directories):
    os.mkdir(directories)

deletions_file = os.path.join(directories, "deletions.bat")
if not os.path.exists(deletions_file):
    with open(deletions_file, 'w') as file:
        file.write("")

locations_file = os.path.join(directories, "locations.bat")
if not os.path.exists(locations_file):
    with open(locations_file, 'w') as file:
        file.write("")

root = tk.Tk()
root.withdraw()
original_folder = filedialog.askdirectory()

temp_file = os.path.join(directories, "temp_file.txt")
with open(temp_file, 'w') as file:
    file.write(original_folder)

if not os.path.exists(original_folder):
    print("The folder", original_folder, "does not exist.")
    os.remove(temp_file)
    exit(1)

new_folder = os.path.join(os.path.dirname(__file__), "SAVES", os.path.basename(original_folder))

if os.path.exists(original_folder):
    with open(deletions_file, 'a') as file:
        file.write("RD /S /Q \"" + original_folder + "\"\n")

    if os.path.exists(new_folder):
        os.system("RD /S /Q \"" + original_folder + "\"")
        print("Original folder already exists and has been deleted.")
    else:
        saves_folder = os.path.join(os.path.dirname(__file__), "SAVES")
        if not os.path.exists(saves_folder):
            os.mkdir(saves_folder)
        os.system("move /y \"" + original_folder + "\" \"" + new_folder + "\"")
        with open(locations_file, 'a') as file:
            file.write("mklink /J \"" + original_folder + "\" \"" + new_folder + "\"\n")
        print("Original folder has been moved to the new location.")

os.system("call \"" + locations_file + "\"")
os.system("call \"" + deletions_file + "\"")
os.system("call \"" + locations_file + "\"")
