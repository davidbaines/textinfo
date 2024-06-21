import argparse
from pathlib import Path

def rename_files(folder, from_ext=None, to_ext=None, from_suffix=None, to_suffix=None, dry_run=True):
    folder_path = Path(folder)
    
    if not folder_path.is_dir():
        print(f"The folder '{folder}' does not exist.")
        return

    # Create the pattern for globbing
    pattern = "*"
    if from_suffix:
        pattern += f"{from_suffix}"
    if from_ext:
        pattern += f"{from_ext}"
    else:
        pattern += "*"
    

    files = [file for file in folder_path.glob(pattern)]
    if not files:
        print(f"No files matching pattern '{pattern}' were found.")
        exit()

    new_files = {}

    for file in files:
        new_name = file.stem

        if from_suffix and new_name.endswith(from_suffix):
            new_name = new_name[:-len(from_suffix)]
        
        if to_suffix is not None:
            new_name += to_suffix
        
        new_name += to_ext or file.suffix
        new_file = file.with_name(new_name)
        if file != new_file:
            new_files[file] = new_file

    print(f"newfiles {new_files} dry-run: {dry_run}")
    if new_files and dry_run:
        for file, new_file in new_files.items():
            print(f"Would rename '{file}' to '{new_file}'")
    elif new_files and not dry_run:
        for file, new_file in new_files.items():
            file.rename(new_file)
            print(f"Attempted to rename '{file}' to '{new_file}'")
    elif not new_files:
        print(f"No file names would be changed.")
        for file in files:
            print(f"{file} would not change.")
    

def main():
    parser = argparse.ArgumentParser(description="Rename files in a folder by changing their extension or suffix.")
    
    parser.add_argument("folder", help="Path to the folder containing files.")
    parser.add_argument("--from-ext", help="Current extension of the files to change.")
    parser.add_argument("--to-ext", help="New extension for the files.")
    parser.add_argument("--from-suffix", help="Current suffix of the files to change.")
    parser.add_argument("--to-suffix", help="New suffix for the files. Use an empty string to remove the suffix.", nargs='?', const='')
    parser.add_argument("-d", "--dry-run", action='store_true', default=False, help="Print the proposed changes only")
    args = parser.parse_args()
    
    rename_files(args.folder, args.from_ext, args.to_ext, args.from_suffix, args.to_suffix, args.dry_run)

if __name__ == "__main__":
    main()
