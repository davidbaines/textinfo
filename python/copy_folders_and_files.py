import argparse
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

import yaml
from prompt_toolkit import prompt


def make_new_folder_with_date(input_folder, output_parent):
    # Get current date
    current_date = datetime.now().strftime("_%Y_%m_%d")
    new_folder_name = input_folder.name + current_date
    output_folder = output_parent / new_folder_name
    # Create the output subfolder
    os.makedirs(output_folder, exist_ok=True)


def copy_subfolders_and_files(
    input_folder, subfolder_names, output_folder, pattern_file
):
    """
    Copies files from the input folder to the output folder,
    based on patterns specified in a YAML file. Prompts the user for handling unmatched files.
    Modifies copied folder names by appending the date and ignores sub-sub-folders.

    Args:
        input_folder (str): Path to the input folder.
        subfolder_names (list): List of names of subfolders to copy.
        output_folder (str): Path to the output folder.
        pattern_file (str): Path to the YAML file containing filename patterns.
    """

    # Load patterns from the YAML file
    with open(pattern_file, "r") as f:
        patterns = yaml.safe_load(f)

    # Get current date
    current_date = datetime.now().strftime("_%Y_%m_%d")

    # Iterate through the specified subfolders
    for subfolder_name in subfolder_names:


        # Get direct children (avoid sub-sub-folders)
        files = [file for file in subfolder_path.glob("*") if file.is_file]
        for file in files:

            # Check if the filename matches any pattern
            should_copy = True
            for pattern in patterns.get("include", []):
                if re.search(pattern, file.name):
                    should_copy = True
                    break

            for pattern in patterns.get("exclude", []):
                if re.search(pattern, file.name):
                    should_copy = False
                    break

            if not should_copy:
                # Ask user about unmatched files
                answer = prompt(
                    "File '{}' doesn't match any pattern. Copy it? (y/n)".format(
                        file.name
                    )
                )

                if answer.lower() == "y":
                    pattern = prompt("Enter a pattern to match this file:")
                    section = prompt("Add pattern to 'include' or 'exclude' (i/e)?")
                    if section.lower() == "i":
                        patterns.setdefault("include", []).append(pattern)
                    else:
                        patterns.setdefault("exclude", []).append(pattern)

                    # Update the YAML file
                    with open(pattern_file, "w") as f:
                        yaml.dump(patterns, f)

                    # Copy the file
                    shutil.copy2(file, output_subfolder / file.name)

                else:
                    # Copy the file if matched
                    shutil.copy2(file, output_subfolder / file.name)


def main():
    parser = argparse.ArgumentParser(
        description="Copy subfolders and files based on patterns."
    )
    parser.add_argument("input_folder", type=Path, help="Path to the input folder.")
    parser.add_argument(
        "subfolder_names", type=str, nargs="+", help="The subfolder names to copy."
    )
    parser.add_argument("output_folder", type=Path, help="Path to the output folder.")
    parser.add_argument(
        "pattern_file",
        type=Path,
        help="Path to the text file containing filename patterns.",
    )
    args = parser.parse_args()

    copy_subfolders_and_files(
        Path(args.input_folder),
        args.subfolder_names,
        Path(args.output_folder),
        Path(args.pattern_file),
    )


if __name__ == "__main__":
    main()
