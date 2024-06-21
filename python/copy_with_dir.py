from pathlib import Path
#from tqdm import tqdm as tqdm
import shutil
from tqdm import tqdm


def choose_yes_no(prompt: str) -> bool:

    choice: str = " "
    while choice not in ["n","y"]:
        choice: str = input(prompt).strip()[0].lower()
    if choice == "y":
        return True
    elif choice == "n":
        return False

        
source_folder_str = "S:/MT/experiments/FT-AytaMagIndi"
dest_folder_str = "C:/Users/David/Documents/FT-AytaMagIndi"

source = Path(source_folder_str)
dest = Path(dest_folder_str) 

source_drive = "S:"
dest_drive = "C:"
subfolder = ""
source_subfolder = source / subfolder

subfolders = [folder for folder in source_subfolder.glob("*") if folder.is_dir()]
print(f"There are {len(subfolders)} folders in {source_subfolder}")

infer_folder = "infer"
top_shared_folder_name = "MT"
bottom_shared_folder_name = "experiments"

# Only copy if there are scores.
scores_pattern = "scores-*.csv"

patterns = ("config.yml", "effective-config*.yml") # "test*")

# https://stackoverflow.com/questions/4568580/python-glob-multiple-filetypes
#Not recursive?
#files = [file for file in source.iterdir() if any(file.match(pattern) for pattern in patterns)]
files_to_copy = []

for subfolder in subfolders:
    test_source = source / subfolder
    scores_files = [file for file in test_source.rglob(scores_pattern)]
    config_files = [file for file in test_source.rglob("config.yml")]
    effective_config_files = [file for file in test_source.rglob("effective-config*.yml")]

    files_to_copy.extend(config_files)
    files_to_copy.extend(effective_config_files)
    files_to_copy.extend(scores_files)
    
    source_folders = sorted(set([file_to_copy.parent for file_to_copy in files_to_copy]))

#    effective_config_files = [file for source_folder in source_folders for file in source_folder.glob("effective-config*.yml")]
    inferred_files = [file for source_folder in source_folders for file in source_folder.rglob("*.sfm")]
    files_to_copy.extend(inferred_files)

# Filter out existing files
filtered_files_to_copy = []
for file_to_copy in files_to_copy:
    
    copy_to = dest / file_to_copy.parent
    #print(f"Checking to see if {copy_to} exists: {copy_to.is_file()}.")
    if not copy_to.is_file():
        filtered_files_to_copy.append((file_to_copy, copy_to))

print(f"There are {len(filtered_files_to_copy)} files to copy from {source_subfolder}.")
print(f"{len(files_to_copy) - len(filtered_files_to_copy)} files already exist in the destintation folder; {dest}")
        
#     print(f"Found {len(files_to_copy)} files to copy from {subfolder}.  {len(files_to_copy) - len(filtered_files_to_copy)} already exist on the destination.")
# else: 
#     print(f"Found {len(files_to_copy)} files to copy from {subfolder}")

# if not filtered_files_to_copy:
#     continue
# elif not choose_yes_no("Continue y/n ?"):
#     exit()

if filtered_files_to_copy:
    for files in tqdm(filtered_files_to_copy):
        source_file, dest_file = files
        #print(s,d)
        #print(s.is_file(), d.is_file())
        dest_folder = dest / source_file.parent
        if not dest_folder.is_dir():
            print(f"Creating folder:  {dest_folder}")
            dest_folder.mkdir(parents=True, exist_ok=True)

        # Write an exact copy of the file from the source to the new destination folder if necessary.
        #print(f"Writing:  {dest_file}")
        shutil.copyfile(source_file, dest_file)

        #    copy_to = dest / str(file_to_copy.parent)[len(source_folder_str) + 1:] / file_to_copy.name
        #    print(copy_to)
        #    print(copy_to.is_file())
else :
    print(f"All specified files already exist in {dest}")
exit()

#for file_pattern in file_patterns:
#    files = source.rglob(file_pattern)

for file in files:
    for idx, parent in enumerate(file.parents):
#        print(parent, "    ", idx, "    ", parent.name)
        if parent.name == bottom_shared_folder_name:
            
            # Create the folders on the destination drive.
            new_dest = dest_root
            #print(f"Starting to add to {new_dest}")
            for i in reversed(range(idx)):
                #print(f"Adding {file.parents[i].name}")
                new_dest = Path(new_dest , file.parents[i].name)
                #print(f"Dest is now: {new_dest}")

            # Make the folders required if necessary
            if not new_dest.is_dir():
                print(f"Creating folder:  {new_dest}")
                new_dest.mkdir(parents=True, exist_ok=True)
            
            destination_file = new_dest / file.name

            # Write an exact copy of the file from the source to the new destination folder if necessary.
            if not destination_file.is_file():
                print(f"Writing:  {destination_file}")
                shutil.copyfile(file, destination_file)

            


