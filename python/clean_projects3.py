import argparse
import csv
import os
import shutil
from datetime import datetime
from pathlib import Path
from tqdm import tqdm


def parse_arguments():
    parser = argparse.ArgumentParser(description="Clean up unnecessary files and folders.")
    parser.add_argument("--input", type=Path, default="S:/Paratext/projects", help="Folder to search")
    parser.add_argument("--no-subfolders", action="store_true", help="Don't delete subfolders")
    parser.add_argument("--confirm", action="store_true", help="Ask for confirmation before deleting")
    parser.add_argument("--dry-run", action="store_true", help="Generate a CSV report without deleting")
    return parser.parse_args()


def get_size(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            total_size += os.path.getsize(os.path.join(dirpath, filename))
    return total_size


def should_delete(name):
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
    # Add more patterns carefully as needed.

    return any(pattern in name for pattern in patterns)


def process_item(path, args, csv_writer):
    global total_size, file_count, folder_count

    if should_delete(os.path.basename(path)):
        size = get_size(path)
        total_size += size

        if os.path.isfile(path):
            file_count += 1
            item_type = "File"
        else:
            folder_count += 1
            item_type = "Folder"

        if args.dry_run:
            csv_writer.writerow([path, item_type, size, datetime.fromtimestamp(os.path.getmtime(path))])
        else:
            if args.confirm:
                if input(f"Delete {path}? (y/n): ").lower() != "y":
                    return
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)


def main():
    args = parse_arguments()
    root_dir = Path(args.input)
    global total_size, file_count, folder_count
    total_size = 0
    file_count = 0
    folder_count = 0

    csv_writer = None
    if args.dry_run:
        csv_file = f"cleanup_dry_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        f = open(csv_file, "w", newline="")
        csv_writer = csv.writer(f)
        csv_writer.writerow(["Path", "Type", "Size (bytes)", "Date Modified"])

    projects = [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]

    for project in tqdm(projects, desc="Processing projects"):
        project_path = os.path.join(root_dir, project)

        if args.no_subfolders:
            for item in os.listdir(project_path):
                item_path = os.path.join(project_path, item)
                if os.path.isfile(item_path):
                    process_item(item_path, args, csv_writer)
        else:
            for root, dirs, files in os.walk(project_path):
                for item in files + dirs:
                    item_path = os.path.join(root, item)
                    process_item(item_path, args, csv_writer)

    if args.dry_run:
        csv_writer.writerow([])
        csv_writer.writerow(["Summary"])
        csv_writer.writerow(["Total Size (bytes)", "File Count", "Folder Count", "Timestamp"])
        csv_writer.writerow([total_size, file_count, folder_count, datetime.now()])
        f.close()

        print(f"\nTotal size that would be freed: {total_size / (1024 * 1024):.2f} MB")
        print(f"Total files: {file_count}")
        print(f"Total folders: {folder_count}")
        print(f"Dry run results saved to {csv_file}")


if __name__ == "__main__":
    main()
