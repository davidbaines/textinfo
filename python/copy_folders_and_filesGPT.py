import argparse
import shutil
from datetime import datetime
from pathlib import Path

def get_folder_with_date(input_folder,output_path):
    
    # Get current date in desired format
    today = datetime.today().strftime("_%Y_%m_%d")

    # Construct new folder name with date appended
    parts = list(input_folder.parts)
    parts[-1] += today
    output_folder = output_path / parts[-1]
    return output_folder
    

def copy_folder_selectively(source_folder, destination_folder):
    """
    Copies a folder ignoring certain files and all folders.

    Args:
        source_folder (str or Path): Path to the source folder.
        destination_folder (str or Path): Path to the desired destination folder.
    """
    #print(f"In copy_folder_selectively, {source_folder} to {destination_folder}")

    # List files in the source folder

    for file in source_folder.iterdir():
        # Skip subfolders
        if file.is_dir():
            continue

        filename = file.name

        # Skip files with specific strings in the name
        if any(string in filename for string in ["Notes", "unique", "licence", "license", "backup, Print", "User" "Access"]):
            continue

        # Construct source and destination file paths
        destination_file = destination_folder / filename

        # Copy the file
        shutil.copy2(file, destination_file)
        #print(f"Copying {file} to {destination_file}")

    print(f"Copied folder {source_folder} to {destination_folder}")


def main():
    parser = argparse.ArgumentParser(
        description="Copy subfolders and files based on patterns."
    )
    parser.add_argument("--input_folder", type=Path, default="C:/My Paratext 9 Projects", help="Path to the input folder.")
    parser.add_argument("--output_folder", type=Path, default="C:/projects", help="Path to the output folder.")
    parser.add_argument(
        "subfolders", type=str, nargs="+", help="The names of the subfolders to copy."
    )
    args = parser.parse_args()
    projects_dir_in = Path(args.input_folder)
    projects_dir_out = Path(args.output_folder)
    s_drive_projects = Path("S:/Paratext/projects")
    folders_to_extract = []

    for subfolder_name in args.subfolders:
        project_dir_in = projects_dir_in / subfolder_name
        project_dir_out = get_folder_with_date(project_dir_in, projects_dir_out)

        # Create the new folder
        project_dir_out.mkdir(exist_ok=True)
        folders_to_extract.append(project_dir_out)

        copy_folder_selectively(project_dir_in, project_dir_out)

        # Get the path to the s Drive projects folder
        s_drive_project = s_drive_projects / project_dir_out.name
        # Also copy the folder to the S Drive.
        shutil.copytree(project_dir_out, s_drive_project)
        print(f"Copied {project_dir_out} to {s_drive_project} ")
        
    print(f"Run command\npython -m silnlp.common.extract_corpora {' '.join([f.name for f in folders_to_extract])}")


if __name__ == "__main__":
    main()