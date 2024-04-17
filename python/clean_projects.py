from pathlib import Path
import shutil
import argparse

def get_files_to_copy(project):
    
    files = [file for file in project.glob('*') if file.is_file]

    # Only copy if there are sfm files.
    files_to_copy = [file for file in files if file.suffix.lower() in ['.usfm','.sfm']]
    if not files_to_copy:
        return None
    
    files_to_copy.extend([file for file in files if file.name.lower() in ['settings.xml', 'custom.sty'] or file.suffix.lower() == '.ldml' ])
    return files_to_copy

def main():
    
    parser = argparse.ArgumentParser(description="Clean Paratext project prior to uploading.")
    parser.add_argument('input',  type=Path, help="Folder to search")
    parser.add_argument('--output', type=Path, help="Folder for the output results.", required=False)
    args = parser.parse_args()
    
    input = Path(args.input)
    #print(args.output)
 
    default_output = input.parent / "cleaned_projects"
    if args.output:
        output = Path(args.output)
    else:
        output = default_output

    #print(input.parent, type(input.parent))
    print(f"Will write cleaned project folders to {output}")
    output.mkdir(parents=True, exist_ok=True)

    projects = [folder for folder in input.glob('*') if folder.is_dir()]
    #for project in projects:
        #print(project)
    #print()

    for project in projects:
        files_to_copy = get_files_to_copy(project)
        #print(f"Looking in {project}")
        if files_to_copy:
            copy_to_folder = output / files_to_copy[0].parent.name
            print(f"Copying files to {copy_to_folder}")
            copy_to_folder.mkdir(parents=True, exist_ok=True)

            for file_to_copy in files_to_copy:
                dest_file = copy_to_folder / file_to_copy.name

                # Write an exact copy of the file from the source to the new destination.    
                shutil.copyfile(file_to_copy, dest_file) 
                #print(f"Writing:  {dest_file}")
        else:
            print(f"No sfm files found in {project}")
if __name__ == "__main__":
    main()