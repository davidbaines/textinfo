import argparse
import csv
import shutil
from datetime import datetime
from pathlib import Path
from tqdm import tqdm


def parse_arguments():
    parser = argparse.ArgumentParser(description="Clean up unnecessary files and folders.")
    parser.add_argument("input", type=Path, default=Path("C:/Projects"), help="Folder to search")
    parser.add_argument("--confirm", action="store_true", help="Ask for confirmation before deleting")
    parser.add_argument("--dry-run", action="store_true", help="Generate a CSV report without deleting")
    return parser.parse_args()


def is_project_folder(folder_path: Path):
    """Check if a folder is a project folder.
    
    A project folder contains more than one SFM file and a Settings.xml file.
    """
    if not folder_path.is_dir():
        return False
    
    # Count SFM files
    sfm_files = list(folder_path.glob('*.[sS][fF][mM]'))
    has_settings = folder_path.joinpath('Settings.xml').exists() or folder_path.joinpath('settings.xml').exists()
    
    return len(sfm_files) > 1 and has_settings


def should_retain(path: Path):
    # File types to retain (case insensitive)
    retained_extensions = ['.sfm', '.usfm', '.ldml', '.sty', '.cct']
    
    # Specific XML files to retain
    retained_xml_files = [
        "settings.xml", 
        "booknames.xml", 
        "canons.xml", 
        "lexicon.xml",
        "wordanalyses.xml"
    ]
    
    # For files that contain specific text in the name
    xml_contains = ["term"]
    
    # Other specific files to retain
    other_retained_files = ["autocorrect.txt"]
    
    # Check if file should be retained
    if path.is_file():
        # Check file extension (case insensitive)
        if path.suffix.lower() in retained_extensions:
            return True
            
        # Check for XML files
        if path.suffix.lower() == '.xml':
            # Check for specific XML filenames (case insensitive)
            if path.name.lower() in retained_xml_files:
                return True
                
            # Check for XML files containing "term" (case insensitive)
            if any(pattern.lower() in path.stem.lower() for pattern in xml_contains):
                return True
                
        # Check for other specific files
        if path.name.lower() in other_retained_files:
            return True
            
    return False


def find_items_to_delete(root_path: Path):
    files_to_delete = []
    folders_to_delete = []
    project_folders = []
    non_project_folders = []
    
    # First identify which folders are project folders
    all_folders = list(root_path.iterdir())
    for folder in tqdm(all_folders, desc="Identifying project folders"):
        if folder.is_symlink():
            print(f" Warning: Ignoring symlink found: {folder}")
            continue
        if folder.is_dir():
            if is_project_folder(folder):
                project_folders.append(folder)
            else:
                non_project_folders.append(folder)
    
    print(f"Found {len(project_folders)} project folders and {len(non_project_folders)} non-project folders")
    
    # Process only project folders
    for project_folder in tqdm(project_folders, desc="Processing project folders"):
        for path in project_folder.glob('*'):
            if path.is_file():
                if not should_retain(path):
                    files_to_delete.append(path)
            if path.is_dir():
                folders_to_delete.append(path)

    return files_to_delete, folders_to_delete, project_folders, non_project_folders


def delete_items(args):
    files_to_delete, folders_to_delete, project_folders, non_project_folders = find_items_to_delete(args.input)
    
    for file_to_delete in tqdm(files_to_delete, desc="Deleting files"):
        if args.confirm:
            if input(f"Delete {file_to_delete}? (y/n): ").lower() != "y":
                continue
        file_to_delete.unlink()

    for folder_to_delete in tqdm(folders_to_delete, desc="Deleting folders"):
        if args.confirm:
            if input(f"Delete {folder_to_delete}? (y/n): ").lower() != "y":
                continue
        shutil.rmtree(folder_to_delete)
    
    print(f"Deleted {len(files_to_delete)} files and {len(folders_to_delete)} folders.")
    print(f"Skipped {len(non_project_folders)} non-project folders.")


def dry_run(args):
    now = datetime.now()
    now_filestamp = now.strftime('%Y%m%d_%H%M%S')
    now_csv_date = now.strftime('%Y %m %d')
    now_csv_time = now.strftime('%H:%M:%S')

    files_to_delete, folders_to_delete, project_folders, non_project_folders = find_items_to_delete(args.input)
        
    csv_file = Path(f"clean_projects_{now_filestamp}.csv")
    
    total_size = 0
    
    with csv_file.open("w", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([f"The clean_projects script was run on {now_csv_date} at {now_csv_time}."])
        csv_writer.writerow(["With these arguments", f"{str(args)}"])
        csv_writer.writerow([])
        csv_writer.writerow(["Project folders found", len(project_folders)])
        csv_writer.writerow(["Non-project folders skipped", len(non_project_folders)])
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

        if len(folders_to_delete) == 0:
            csv_writer.writerow(["No folders were found to delete."])

        if len(files_to_delete) == 0:
            csv_writer.writerow(["No files were found to delete."])
            
        csv_writer.writerow([])
        csv_writer.writerow(["Non-project folders (skipped):"])
        for folder in non_project_folders:
            csv_writer.writerow([str(folder)])

    print(f"Dry run results saved to {csv_file}")
    print(f"Total size that would be freed: {total_size / (1024 * 1024):.2f} MB")
    print(f"Total files: {len(files_to_delete)}")
    print(f"Total folders: {len(folders_to_delete)}")
    print(f"Skipped {len(non_project_folders)} non-project folders.")


def main():
    args = parse_arguments()
    
    if args.dry_run:
        dry_run(args)
    else:
        delete_items(args)


if __name__ == "__main__":
    main()