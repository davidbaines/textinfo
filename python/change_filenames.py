import argparse
from pathlib import Path

def change_file_names(folder, from_ext=".SFM", to_ext=".SFM", from_suffix="", to_suffix="", remove_suffix=False):

    # Get pattern to match
    if from_suffix:
        pattern = f"*{from_suffix}{from_ext}"
    else:
        pattern = f"*{from_ext}"

    if remove_suffix:
        new_pattern = f"{to_ext}"
    elif to_suffix:
        new_pattern = f"{to_suffix}{to_ext}"
    else:
        print(f"Not sure what to do with remove_suffix: {remove_suffix} and to_suffix: {to_suffix}")

    # Iterate through each file in the folder
    for file_path in folder_path.glob(pattern):

        # Construct the new file name with the new extension
        new_file_name = file_path.stem[:-len(from_suffix)] + new_pattern
        
        
        # Rename the file with the new extension 
        print(f"Would rename {file} to {new_file_name}")
        #file_path.rename(file_path.with_name(new_file_name))
        #print(f"Renamed '{file_path}' to '{new_file_name}'")


# def change_project_suffix(folder, from_suffix, to_suffix):
    
#     # Convert the folder path to a Path object
#     folder_path = Path(folder)

#     # Check if the folder exists
#     if not folder_path.exists():
#         print(f"The folder '{folder}' does not exist.")
#         return

#     # Iterate through each file in the folder
#     for file in folder_path.glob(f'*{from_suffix}.*'):
#         ext = file.suffix

#         # Construct the new file name with the new extension
#         new_file_name = file.stem[:-len(from_suffix)] + f"{to_suffix}{ext}"

#         # Rename the file with the new extension
#         print(f"Would rename {file} to {new_file_name}")
#         #file_path.rename(file_path.with_name(new_file_name))
#         #print(f"Renamed '{file_path}' to '{new_file_name}'")


def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Change file extensions in a folder.")

    # Add positional arguments for folder, from_ext, and to_ext
    parser.add_argument("folder", help="Path to the folder containing files.")
    parser.add_argument("--from_ext", default='.SFM', help="Current extension of the files.")
    parser.add_argument("--to_ext", default='.SFM', help="New extension for the files.")
    parser.add_argument("--from_suffix", default='',help="Current suffix of the files.")
    parser.add_argument("--to_suffix", default='', help="New suffix for the files.")

    # Parse the command-line arguments
    args = parser.parse_args()
    folder = Path(args.folder)
    
    # Check if the folder exists
    if not folder.is_dir():
        print(f"The folder '{folder}' does not exist.")
        return
    
    from_ext = args.from_ext
    to_ext = args.to_ext
    from_suffix = args.from_suffix
    to_suffix = args.to_suffix

    if to_suffix == '':
        remove_suffix = True
        to_suffix = None
    else:
        remove_suffix = False

    # Call the function to change file extensions
    change_file_names(args.folder, from_ext, to_ext, from_suffix, to_suffix, remove_suffix)

if __name__ == "__main__":
    main()
