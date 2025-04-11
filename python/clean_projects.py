import argparse
import sys
from pathlib import Path
#from tqdm import tqdm


def confirm_and_remove(files_to_delete, project):
    files_to_delete_str = "\n".join(f.name for f in files_to_delete)
    print(f"\nThese files are to be deleted from {project}:{files_to_delete_str}")
    if choose_yes_no_quit(
        f"Would you like to delete these {len(files_to_delete)} files from the project {project}?"
    ):
        remove(files_to_delete)


def get_sub_folders(folder):
    return [f for f in folder.glob("*") if f.is_dir()]


def choose_yes_no_quit(prompt: str) -> bool:
    choice: str = ""
    while choice not in ["n", "y", "q"]:
        choice: str = input(prompt).strip().lower()
    if choice == "y":
        return True
    if choice == "n":
        return False
    if choice == "q":
        sys.exit(0)


def remove(files_to_delete):
    for file_to_delete in files_to_delete:
        file_to_delete.unlink()
        print(f"Attempted to delete {file_to_delete}")


def main():
    parser = argparse.ArgumentParser(description="Clean Paratext projects.")
    parser.add_argument("input", type=Path, help="Folder to search")
    parser.add_argument(
        "--careful", action="store_true", help="Only delete Notes and Access"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Ask user for confirmation before deleting.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files that would be deleted but don't delete them.",
    )
    parser.add_argument("--output", type=Path, help="When used with dry-run, save the files that would be deleted in this folder.")

    args = parser.parse_args()
    input = Path(args.input)
    careful = args.careful
    confirm = args.confirm
    dry_run = args.dry_run
    if dry_run and args.output:
        output = Path(args.output)
        log_file = output / "Notes.txt"

        if not output.is_dir():
            raise ValueError("Output folder must be a directory.")

    if careful:
        file_patterns = ["Notes", "User" "Access"]
    else:
        file_patterns = [
            "Notes",
            "unique",
            "licence",
            "license",
            "backup",
            "Print",
            "User",
            "Access",
        ]

    projects = get_sub_folders(input)

    for project in projects:
        #sub_folders = get_sub_folders(project)
        files_to_delete = [
            f
            for f in project.glob("*")
            if f.is_file() and any(string in f.name for string in file_patterns)
        ]
        
        if dry_run:
            if output:
                with open(log_file, "a", encoding="utf-8") as log:
                    if not files_to_delete:
                        log.write(f"No files to delete in {project}\n")
                        continue
                    else : # Copy and log the files to delete.
                        project_folder = project.parts[-1]
                        output_folder = output / project_folder
                        output_folder.mkdir(exist_ok=True)
                        print(f"Saving files from project: {project} to {output_folder}")
                        log.write(f"Saving files from project: {project} to {output_folder}\n")
                        for file in files_to_delete:
                            output_file = output_folder / file.name
                            output_file.write_bytes(file.read_bytes())
            else: # Just print the files to delete.
                print(f"Files to delete in {project}:")
                for file in files_to_delete:
                    print(f"\t{file}")
                    continue

        elif careful:
            if confirm:
                confirm_and_remove(files_to_delete, project)
            else:
                remove(files_to_delete)

        else:
            # Remove all subfolders and remove files
            if confirm:
                confirm_and_remove(files_to_delete, project)
            else:
                remove(files_to_delete)


if __name__ == "__main__":
    main()
