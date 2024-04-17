import argparse
import csv
from pathlib import Path

import xxhash
from tqdm import tqdm


def calculate_file_hash(file):
    with open(file, "rb") as f:
        content = f.read()
        file_hash = xxhash.xxh64(content).hexdigest()
    return file_hash


def list_files_in_folder(folder_path, pattern):
    folder = Path(folder_path)
    return [file for file in folder.glob(f"*{pattern}*") if file.is_file()]


def save_metadata_to_csv(metadata, csv_file):
    with open(csv_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["file", "File_Hash"])
        for file, file_hash in metadata.items():
            writer.writerow([file, file_hash])


def load_metadata_from_csv(csv_file):
    metadata = {}
    with open(csv_file, mode="r") as file:
        reader = csv.reader(file)
        # next(reader)  # Skip header row
        for row in reader:
            file, file_hash = row
            metadata[file] = file_hash
    return metadata


def check_for_duplicates(files, csv_file):
    if Path(csv_file).exists():
        file_metadata = load_metadata_from_csv(csv_file)
    else:
        file_metadata = {}

    duplicate_files = []

    for file in tqdm(files):
        if file in file_metadata:
            file_hash = file_metadata[file]
        else:
            file_hash = calculate_file_hash(file)
            file_metadata[file] = file_hash
            save_metadata_to_csv(
                {file: file_hash}, csv_file
            )  # Save immediately after calculating hash

    return duplicate_files


def main():
    parser = argparse.ArgumentParser(description="Report duplicate files.")
    parser.add_argument("folder", type=Path, help="Directory to search")
    parser.add_argument(
        "pattern", type=str, default=".txt", help="File patterns to search"
    )
    parser.add_argument("csv", type=Path, help="Location of metadata csv file.")
    args = parser.parse_args()

    folder = Path(args.folder)
    pattern = args.pattern
    csv_file = Path(args.csv)
    files = list_files_in_folder(folder, pattern)
    print(f"Found {len(files)} files matching pattern '{pattern}' in {folder}")

    check_for_duplicates(files, csv_file)
    print(f"Saved duplicate file info to: {csv_file}")


if __name__ == "__main__":
    main()
