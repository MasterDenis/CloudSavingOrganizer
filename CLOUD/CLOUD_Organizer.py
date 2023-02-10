import os
import shutil

def add_to_deletions_bat(original_folder):
    with open(os.path.join("Directories", "deletions.bat"), "a") as f:
        f.write(f"RD /S /Q \"{original_folder}\"\n")

def add_to_locations_bat(original_folder, new_folder):
    with open(os.path.join("Directories", "locations.bat"), "a") as f:
        f.write(f"mklink /J \"{original_folder}\" \"{new_folder}\"\n")

def main():
    directories = os.path.join(os.path.dirname(__file__), "Directories")
    if not os.path.exists(directories):
        os.makedirs(directories)

    if not os.path.exists(os.path.join(directories, "deletions.bat")):
        open(os.path.join(directories, "deletions.bat"), "w").close()
    if not os.path.exists(os.path.join(directories, "locations.bat")):
        open(os.path.join(directories, "locations.bat"), "w").close()

    original_folder = input("Enter the original folder location: ")
    new_folder = os.path.join(os.path.dirname(__file__), "SAVES", os.path.basename(original_folder))

    if os.path.exists(original_folder):
        add_to_deletions_bat(original_folder)
        if os.path.exists(new_folder):
            os.system(f"RD /S /Q \"{original_folder}\"")
        else:
            os.makedirs(os.path.dirname(new_folder), exist_ok=True)
            shutil.move(original_folder, new_folder)
            add_to_locations_bat(original_folder, new_folder)
    else:
        print(f"The folder {original_folder} does not exist.")

    os.system(os.path.join(directories, "locations.bat"))

if __name__ == "__main__":
    main()
