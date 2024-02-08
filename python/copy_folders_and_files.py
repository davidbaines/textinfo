import argparse
import fnmatch
import os
import re
import shutil


def copy_subfolders_and_files(input_folder, subfolder_names, output_folder, pattern_file):
    """
    Copies selected subfolders and files from the input folder to the output folder,
    based on regular expression patterns specified in a text file.

    Args:
        input_folder (str): Path to the input folder.
        subfolder_names (list): List of names of subfolders to copy.
        output_folder (str): Path to the output folder.
        pattern_file (str): Path to the text file containing filename patterns.
    """

    # Load regular expression patterns from the text file
    patterns = {}
    with open(pattern_file, 'r') as f:
        for line in f:
            pattern, action = line.strip().split()
            patterns[pattern] = action == 'copy'

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through the specified subfolders
    for subfolder_name in subfolder_names:
        subfolder_path = os.path.join(input_folder, subfolder_name)
        output_subfolder_path = os.path.join(output_folder, subfolder_name)

        # Create the output subfolder
        os.makedirs(output_subfolder_path)

        # Iterate through files in the subfolder
        for filename in os.listdir(subfolder_path):
            file_path = os.path.join(subfolder_path, filename)

            # Check if the filename matches any pattern
            for pattern, should_copy in patterns.items():
                if re.search(pattern, filename):
                    if should_copy:
                        # Copy the file
                        shutil.copy2(file_path, output_subfolder_path)
                    break  # Skip to the next file if a matching pattern is found

def main():
    parser = argparse.ArgumentParser(description="Copy subfolders and files based on patterns.")
    parser.add_argument("input_folder", type=str, help="Path to the input folder.")
    parser.add_argument("subfolder_names", type=str,  nargs="+", help="The subfolder names to copy.")
    parser.add_argument("output_folder", type=str, help="Path to the output folder.")
    parser.add_argument("pattern_file", type=str, help="Path to the text file containing filename patterns.")
    args = parser.parse_args()

    copy_subfolders_and_files(args.input_folder,
                             open(args.subfolder_names).read().splitlines(),
                             args.output_folder,
                             args.pattern_file)

if __name__ == "__main__":
    main()
