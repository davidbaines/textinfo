import argparse
import boto3
import shutil
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

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


def write_list(output_file_path,file_list):

    # Open the output file in write mode
    with open(output_file_path, "w") as output_file:
        # Write file paths from the list of files
        for file_path in file_list:
            output_file.write(str(file_path) + "\n")
    print("Paths written to:", output_file_path)


def read_list(text_file):

    # Create an empty list to store the pathlib objects
    path_objects = []

    # Open the text file in read mode
    with open(text_file, "r") as input_file:
        # Read each line from the file
        for line in input_file:
            # Remove any leading or trailing whitespace characters
            line = line.strip()
            # Convert the string path to a pathlib object and append it to the list
            path_objects.append(Path(line))

    return path_objects


def main():
    parser = argparse.ArgumentParser(
        description="Copy subfolders and files based on patterns."
    )
    parser.add_argument("--input-folder", type=Path, default="C:/My Paratext 9 Projects", help="Path to the input folder.")
    parser.add_argument("--output-folder", type=Path, default="C:/projects", help="Path to the output folder.")
    parser.add_argument(
        "--subfolders", type=str, nargs="+", default= [], help="The names of the subfolders to copy."
    )
    parser.add_argument("--list-unnecessary", default=False,
        action="store_true",
        help="List files and folders that are not required in output folder.",
    )
    args = parser.parse_args()
    projects_dir_in = Path(args.input_folder)
    projects_dir_out = Path(args.output_folder)
    s_drive_projects = Path("S:/Paratext/projects")
    folders_to_extract = []


    if args.list_unnecessary:

        #Find the immediate project folders. Add to dictionary.       
        project_folders = [f for f in s_drive_projects.glob("*") if f.is_dir()]

        unnecessary_fs_file = Path("C:\projects\list.txt")
        if unnecessary_fs_file.is_file():
            unnecessary_fs = read_list(unnecessary_fs_file)
            print(f"Read in a list of {len(unnecessary_fs)} unnecessary files and folders.")
            
        else:
            unnecessary_fs = []
        
            project_folders = [f for f in s_drive_projects.glob("*") if f.is_dir()]
            print(f"Found {len(project_folders)} projects in {s_drive_projects}")
            for project_folder in project_folders:
                for f in project_folder.glob("*"):
                    if f.is_dir():
                        unnecessary_fs.append(f)
                    if f.is_file() and any(string in f.name for string in ["Notes", "unique", "licence", "license", "backup", "Print", "User" "Access"]):
                        unnecessary_fs.append(f)
            print(f"Found {len(unnecessary_fs)} unnecessary files and folders")
            write_list(unnecessary_fs_file , unnecessary_fs)
        
        for f in tqdm(unnecessary_fs):
            if f.is_dir():
                print(f"Folder {f} should be deleted.")
                # Use rmdir() to remove the directory and its contents recursively
                f.rmdir()
                print(f"Attempted to delete {f} ")
                exit()
            elif f.is_file():
                print(f"File {f} should be deleted.")
                f.unlink()
                exit()
        exit()

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