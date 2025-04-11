import argparse
import csv
import shutil
from datetime import datetime
from pathlib import Path
from tqdm import tqdm


def parse_arguments():
    parser = argparse.ArgumentParser(description="Clean up unnecessary files and folders.")
    parser.add_argument("input", type=Path, default=Path("C:/Projects"), help="Folder to search")
    parser.add_argument("--no-subfolders", action="store_true", help="Don't delete subfolders")
    parser.add_argument("--confirm", action="store_true", help="Ask for confirmation before deleting")
    parser.add_argument("--dry-run", action="store_true", help="Generate a CSV report without deleting")
    return parser.parse_args()


def should_delete(path: Path):
    patterns = [
        "Notes",
        "unique",
        "licence",
        "license",
        "backup",
        "Print",
        "User",
        "Access",
    ]
    return any(pattern in path.name for pattern in patterns)

def find_items_to_delete(root_path: Path):
    files_to_delete = []
    folders_to_delete = []
    project_folders = list(root_path.iterdir())
    
    for project_folder in tqdm(project_folders):
        if project_folder.is_symlink():
            # Initial space helpful in VS Code when inside a tqdm loop.
            print(f" Warning: Ignoring symlink found: {project_folder}")
            continue
        if project_folder.is_dir():
            for path in project_folder.glob('*'):
                if path.is_file():
                    if should_delete(path):
                        files_to_delete.append(path)
                if path.is_dir():
                        folders_to_delete.append(path)

    return files_to_delete, folders_to_delete


def delete_items(args):
    files_to_delete, folders_to_delete = find_items_to_delete(args.input)
    
    for file_to_delete in tqdm(files_to_delete, desc="Deleting files"):
        if args.confirm:
            if input(f"Delete {file_to_delete}? (y/n): ").lower() != "y":
                continue
        file_to_delete.unlink()

        
    if args.no_subfolders or len(folders_to_delete) == 0:
        return
    else:
        for folder_to_delete in tqdm(folders_to_delete, desc="Deleting folders"):
            if args.confirm:
                if input(f"Delete {folder_to_delete}? (y/n): ").lower() != "y":
                    continue
            shutil.rmtree(folder_to_delete)
    
    print(f"Deleted {len(files_to_delete)} files and {len(folders_to_delete)} folders.")


def dry_run(args):
    now = datetime.now()
    now_filestamp = now.strftime('%Y%m%d_%H%M%S')
    now_csv_date = now.strftime('%Y %m %d')
    now_csv_time = now.strftime('%H:%M:%S')

    files_to_delete, folders_to_delete = find_items_to_delete(args.input)
        
    csv_file = Path(f"clean_projects_{now_filestamp}.csv")
    
    total_size = 0
    
    with csv_file.open("w", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([f"The clean_projects script was run on {now_csv_date} at {now_csv_time}."])
        csv_writer.writerow(["With these arguments", f"{str(args)}"])
        csv_writer.writerow([])
        csv_writer.writerow(["Path", "Type", "Size (bytes)"])
    
        for folder_to_delete in folders_to_delete:
            size = sum(f.stat().st_size for f in folder_to_delete.rglob('*') if f.is_file())
            total_size += size
            csv_writer.writerow([str(folder_to_delete), "Folder", size])
        if len(folders_to_delete) == 0:
            csv_writer.writerow([0, "Folders", 0])

        for file_to_delete in files_to_delete:
            size = file_to_delete.stat().st_size
            total_size += size
            csv_writer.writerow([str(file_to_delete), "File", size])
        
        if len(files_to_delete) == 0:
            csv_writer.writerow([0, "Files", 0])

        csv_writer.writerow([])
        csv_writer.writerow(["Summary"])
        csv_writer.writerow(["File Count", "Folder Count", "Total Size (bytes)", "Total size (MB)"])
        csv_writer.writerow([len(files_to_delete), len(folders_to_delete), total_size, f"{total_size / (1024 * 1024):.2f}"])

        if args.no_subfolders:
            csv_writer.writerow(["The total size is the sum of the file sizes not including those in project subfolders."])
            csv_writer.writerow(["Run without the --no-subfolders option to deal with the subfolders in projects."])
        
        elif len(folders_to_delete) == 0:
            csv_writer.writerow(["No folders were found to delete."])

        if len(files_to_delete) == 0:
            csv_writer.writerow(["No files were found to delete."])

    print(f"Dry run results saved to {csv_file}")
    print(f"Total size that would be freed: {total_size / (1024 * 1024):.2f} MB")
    print(f"Total files: {len(files_to_delete)}")
    print(f"Total folders: {len(folders_to_delete)}")


def main():
    args = parse_arguments()
    
    if args.dry_run:
        dry_run(args)
    else:
        delete_items(args)


if __name__ == "__main__":
    main()