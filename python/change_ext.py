import argparse
from pathlib import Path

def change_file_extensions(folder, from_ext, to_ext):
    # Convert the folder path to a Path object
    folder_path = Path(folder)

    # Check if the folder exists
    if not folder_path.exists():
        print(f"The folder '{folder}' does not exist.")
        return

    # Iterate through each file in the folder
    for file_path in folder_path.glob(f'*.{from_ext}'):
        # Construct the new file name with the new extension
        new_file_name = file_path.stem + '.' + to_ext
        # Rename the file with the new extension
        
        file_path.rename(file_path.with_name(new_file_name))
        print(f"Renamed '{file_path}' to '{new_file_name}'")

def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Change file extensions in a folder.")

    # Add positional arguments for folder, from_ext, and to_ext
    parser.add_argument("folder", help="Path to the folder containing files.")
    parser.add_argument("from_ext", help="Current extension of the files.")
    parser.add_argument("to_ext", help="New extension for the files.")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the function to change file extensions
    change_file_extensions(args.folder, args.from_ext, args.to_ext)

if __name__ == "__main__":
    main()
