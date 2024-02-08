Python
import os
import shutil
import toml
import re
from prompt_toolkit import prompt
from datetime import datetime


def copy_subfolders_and_files(input_folder, subfolder_names, output_folder, pattern_file):
    """
    Copies selected subfolders and files from the input folder to the output folder,
    based on patterns specified in a TOML file. Prompts the user for handling unmatched files.
    Modifies copied folder names by appending the date.

    Args:
        input_folder (str): Path to the input folder.
        subfolder_names (list): List of names of subfolders to copy.
        output_folder (str): Path to the output folder.
        pattern_file (str): Path to the TOML file containing filename patterns.
    """

    # Load patterns from the TOML file
    with open(pattern_file, 'r') as f:
        patterns = toml.load(f)

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get current date
    current_date = datetime.now().strftime("_%Y_%m_%d")

    # Iterate through the specified subfolders
    for subfolder_name in subfolder_names:
        subfolder_path = os.path.join(input_folder, subfolder_name)
        output_subfolder_path = os.path.join(output_folder, subfolder_name + current_date)

        # Create the output subfolder
        os.makedirs(output_subfolder_path)

        # Iterate through files in the subfolder
        for filename in os.listdir(subfolder_path):
            file_path = os.path.join(subfolder_path, filename)

            # Check if the filename matches any pattern
            should_copy = True
            for pattern in patterns.get("include", []):
                if re.search(pattern, filename):
                    should_copy = True
                    break

            for pattern in patterns.get("exclude", []):
                if re.search(pattern, filename):
                    should_copy = False
                    break

            if not should_copy:
                # Ask user about unmatched files
                answer = prompt(
                    "File '{}' doesn't match any pattern. Copy it? (y/n)".format(filename)
                )
                if answer.lower() == 'y':
                    pattern = prompt("Enter a pattern to match this file:")
                    section = prompt("Add pattern to 'include' or 'exclude' (i/e)?")
                    if section.lower() == 'i':
                        patterns.setdefault("include", []).append(pattern)
                    else:
                        patterns.setdefault("exclude", []).append(pattern)

                    # Update the TOML file
                    with open(pattern_file, 'w') as f:
                        toml.dump(patterns, f)

                    # Copy the file
                    shutil.copy2(file_path, output_subfolder_path)

            else:
                # Copy the file if matched
                shutil.copy2(file_path, output_subfolder_path)



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
