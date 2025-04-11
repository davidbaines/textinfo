import argparse
import csv
import shutil
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

def parse_arguments():
    parser = argparse.ArgumentParser(description="Clean up unnecessary files and folders.")
    parser.add_argument("--input", type=Path, default=Path("S:/Paratext/projects"), help="Folder to search")
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
            print(f" Warning: Ignoring symlink found: {project_folder}")
            continue
        if project_folder.is_dir():
            for path in project_folder.glob('*'):
                if path.is_file() and should_delete(path):
                    files_to_delete.append(path)
                if path.is_dir():
                    folders_to_delete.append(path)

    return files_to_delete, folders_to_delete

# New function to handle CSV writing
def write_csv_report(args, files_to_delete, folders_to_delete):
    now = datetime.now()
    now_filestamp = now.strftime('%Y%m%d_%H%M%S')
    now_csv_date = now.strftime('%Y %m %d')
    now_csv_time = now.strftime('%H:%M:%S')

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

        for file_to_delete in files_to_delete:
            size = file_to_delete.stat().st_size
            total_size += size
            csv_writer.writerow([str(file_to_delete), "File", size])

    print(f"CSV report generated: {csv_file}")
    return total_size

def dry_run(args):
    files_to_delete, folders_to_delete = find_items_to_delete(args.input)

    if args.no_subfolders:
        folders_to_delete = []

    write_csv_report(args, files_to_delete, folders_to_delete)


def delete_items(args):
    files_to_delete, folders_to_delete = find_items_to_delete(args.input)

    if args.no_subfolders:
        folders_to_delete = []

    # Write CSV before deletion for tracking
    write_csv_report(args, files_to_delete, folders_to_delete)

    for file_to_delete in tqdm(files_to_delete, desc="Deleting files"):
        if args.confirm:
            if input(f" Delete {file_to_delete}? (y/n): ") == 'y':
                file_to_delete.unlink()
        else:
            file_to_delete.unlink()

    for folder_to_delete in tqdm(folders_to_delete, desc="Deleting folders"):
        if args.confirm:
            if input(f" Delete {folder_to_delete}? (y/n): ") == 'y':
                shutil.rmtree(folder_to_delete)
        else:
            shutil.rmtree(folder_to_delete)


def main():
    args = parse_arguments()
    
    if args.dry_run:
        dry_run(args)
    else:
        delete_items(args)


if __name__ == "__main__":
    main()