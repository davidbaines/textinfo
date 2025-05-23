import argparse
import csv
import shutil
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

def parse_arguments():
    parser = argparse.ArgumentParser(description="Clean up unnecessary files and folders.")
    parser.add_argument("--input", type=Path, default=Path("S:/Paratext/projects"), help="Folder to search")
    parser.add_argument("--delete-subfolders", action="store_true", help="Also delete project subfolders.")
    parser.add_argument("--no-confirm", action="store_true", help="Ask for confirmation before deleting")
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

def execute_and_report(args):
    now = datetime.now()
    now_filestamp = now.strftime('%Y%m%d_%H%M%S')
    now_csv_date = now.strftime('%Y %m %d')
    now_csv_time = now.strftime('%H:%M:%S')

    files_to_delete, folders_to_delete = find_items_to_delete(args.input)

    if args.no_subfolders:
        folders_to_delete = []

    csv_file = Path(f"clean_projects_{now_filestamp}.csv")
    total_size = 0

    with csv_file.open("w", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([f"The clean_projects script was run on {now_csv_date} at {now_csv_time}."])
        csv_writer.writerow(["With these arguments", f"{str(args)}"])
        csv_writer.writerow([])
        csv_writer.writerow(["Path", "Type", "Size (bytes)", "Deleted"])

        for folder_to_delete in folders_to_delete:
            size = sum(f.stat().st_size for f in folder_to_delete.rglob('*') if f.is_file())
            total_size += size

            deleted = "No" if args.dry_run else try_delete(folder_to_delete, args)
            csv_writer.writerow([str(folder_to_delete), "Folder", size, deleted])

        for file_to_delete in files_to_delete:
            size = file_to_delete.stat().st_size
            total_size += size

            deleted = "No" if args.dry_run else try_delete(file_to_delete, args)
            csv_writer.writerow([str(file_to_delete), "File", size, deleted])

    print(f"CSV report generated: {csv_file}")
    return total_size

def try_delete(item: Path, args) -> str:
    if args.confirm:
        confirmation = input(f"Delete {item}? (y/n): ").strip().lower()
        if confirmation != 'y':
            return "Skipped"

    if item.is_file():
        item.unlink()
    elif item.is_dir():
        shutil.rmtree(item)

    return "Yes"

# Main script logic
def main():
    args = parse_arguments()
    execute_and_report(args)

if __name__ == "__main__":
    main()
