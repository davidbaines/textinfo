from pathlib import Path
import shutil
import argparse

def get_sub_folders(folder):
    return [f for f in folder.glob("*") if f.is_dir()]
 

def choose_yes_no(prompt: str) -> bool:

    choice: str = " "
    while choice not in ["n","y"]:
        choice: str = input(prompt).strip()[0].lower()
    if choice == "y":
        return True
    elif choice == "n":
        return False


def main():
    
    parser = argparse.ArgumentParser(description="Clean Paratext projects.")
    parser.add_argument('input',  type=Path, default = Path("S:/Paratext/projects"), help="Folder to search")
    parser.add_argument('--careful',  action='store_true', help="Only delete Notes and Access")
    
    args = parser.parse_args()
    input = Path(args.input)
    careful = args.careful

    if careful:
        file_patterns = ["Notes", "User" "Access"]
    else:
        file_patterns = ["Notes", "unique", "licence", "license", "backup", "Print", "User" "Access"]

    projects = get_sub_folders(input)

    for project in projects:

        sub_folders = get_sub_folders(project)
        files_to_delete  = [ f for f in project.glob("*") if f.is_file() and any(string in f.name for string in file_patterns) ]
        if not careful:
            # Remove all subfolders
            for sub_folder in sub_folders:
                shutil.rmtree(sub_folder)
                print(f"Attempted to delete {sub_folder}")
        
        for file_to_delete in files_to_delete:
            file_to_delete.unlink()
            print(f"Attempted to delete {file_to_delete}")

if __name__ == "__main__":
    main()
