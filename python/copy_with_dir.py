from pathlib import Path
#from tqdm import tqdm as tqdm
import shutil

source_folder_str = "S:/MT/experiments"
dest_folder_str = "E:/Work/MT/experiments" 
source = Path(source_folder_str)
dest = Path(dest_folder_str) 

source_drive = "S:"
dest_drive = "E:"
subfolder = "BT-Spanish"
infer_folder = "infer"

test_source = source / subfolder

top_shared_folder_name = "MT"
bottom_shared_folder_name = "experiments"

# Only copy if there are scores.
scores_pattern = "scores-*.csv"

patterns = ("config.yml", "effective-config*.yml") # "test*")

# https://stackoverflow.com/questions/4568580/python-glob-multiple-filetypes
#Not recursive?
#files = [file for file in source.iterdir() if any(file.match(pattern) for pattern in patterns)]

#scores_files = [file for file in source.rglob(scores_pattern) if (file.parent / "config.yml").is_file()]
scores_files = [file for file in test_source.rglob(scores_pattern) if (file.parent / "config.yml").is_file()]
config_files = [file.with_name("config.yml") for file in scores_files]

source_folders = sorted(set([file.parent for file in scores_files]))

#infer_folders = []
#for source_folder in source_folders:
#    source_infer_folder = source_folder / infer_folder
#    if source_infer_folder.is_dir():
#        dest_infer_folder = dest / str(file_to_copy.parent)[len(source_folder_str) + 1:] / infer_folder
#        print(f"Copying {source_infer_folder} to {dest_infer_folder}")
#        #shutil.copytree(source_infer_folder ,dest_infer_folder)

#effective_config_files = []
#for source_folder in source_folders:
#    for file in source_folder.glob("effective-config*.yml"):
#        effective_config_files.append(file)

effective_config_files = [file for source_folder in source_folders for file in source_folder.glob("effective-config*.yml")]
inferred_files = [file for source_folder in source_folders for file in source_folder.rglob("*.sfm")]

files_to_copy = scores_files
files_to_copy.extend(config_files)
files_to_copy.extend(effective_config_files)
files_to_copy.extend(inferred_files)

# Filter out existing files
filtered_files_to_copy = []
for file_to_copy in files_to_copy:
    
    copy_to = dest / str(file_to_copy.parent)[len(source_folder_str) + 1:] / file_to_copy.name
    print(f"Checking to see if {copy_to} exists: {copy_to.is_file()}.")
    if not copy_to.is_file():
        filtered_files_to_copy.append((file_to_copy, copy_to))

#dest_folders = [dest / str(source_folder)[len(source_folder_str) + 1:] for source_folder in source_folders ]


print(f"Found {len(scores_files)} scores files in {test_source}.")
# print(scores_files)
# print(f"Found {len(source_folders)} source folders.")
# for source_folder in source_folders:
#     print(source_folder)

# for dest_folder in dest_folders:
#     print(dest_folder)
# print(dest_folder_str)

#for effective_config_file in effective_config_files:
#    print(effective_config_file)
for source_file, dest_file in filtered_files_to_copy:
    #print(s,d)
    #print(s.is_file(), d.is_file())
    dest_folder = dest / str(source_file.parent)[len(source_folder_str) + 1:]
    #if not dest_folder.is_dir():
    #    print(f"Creating folder:  {dest_folder}")
    dest_folder.mkdir(parents=True, exist_ok=True)

    # Write an exact copy of the file from the source to the new destination folder if necessary.
    print(f"Writing:  {dest_file}")
    shutil.copyfile(source_file, dest_file)

#    copy_to = dest / str(file_to_copy.parent)[len(source_folder_str) + 1:] / file_to_copy.name
#    print(copy_to)
#    print(copy_to.is_file())
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

            


