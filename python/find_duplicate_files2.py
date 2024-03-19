import argparse
import csv
from pathlib import Path

import xxhash
from tqdm import tqdm

def create_metadata_file(csv_file):
    if not Path(csv_file).exists():
        with open(csv_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["file", "hash"])


def save_metadata_to_csv(metadata, csv_file):
    """Save all the metadata to a csv file."""
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["file", "hash"])
        for file, file_hash in metadata.items():
            writer.writerow([file, file_hash])


def save_file_metadata_to_csv(file_path,hash, csv_file):
    """Save one line of metadata to the csv file"""
    with open(csv_file, mode="a", newline="") as csv_file:
        csv_file.write(f"{file_path},{hash}\n")


def load_metadata_from_csv(csv_file):
    metadata = {}
    if Path(csv_file).exists():
        with open(csv_file, mode="r") as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header row
            for row in reader:
                file, file_hash = row
                metadata[file] = file_hash
    return metadata


def calculate_file_hash(file):
    """Calculate the file hash quickly"""
    with open(file, "rb") as f:
        content = f.read()
        file_hash = xxhash.xxh64(content).hexdigest()
    return file_hash


def calculate_hashes(files, csv_file):
    for file in tqdm(files):
        file_hash = calculate_file_hash(file)
        save_file_metadata_to_csv(file,file_hash,csv_file)


def get_dup_groups(metadata):
    
    duplicate_files = {}

    # Compare file hashes with metadata from the CSV file
    for file, hash in metadata.items():
        if hash in duplicate_files:
            duplicate_files[hash].append(file)
        else:
            duplicate_files[hash] = [file]
    
    hash_groups = {}
    for hash, files in duplicate_files.items():
        if len(files) > 1:
            hash_groups[hash] = files
    return hash_groups

def byte_comparison(file1, file2):
    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        while True:
            byte1 = f1.read(1)
            byte2 = f2.read(1)
            if byte1 != byte2:
                return False
            if not byte1:
                # Reached the end of both files without finding any differences
                return True
            
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

    # Create the csv file if necessary
    create_metadata_file(csv_file)

    #Find the files in the folder
    files = [file for file in folder.glob(f"*{pattern}*") if file.is_file()]
    print(f"Found {len(files)} files matching pattern '*{pattern}*' in {folder}")
    
    # Get the existing metadata
    metadata = load_metadata_from_csv(csv_file)
    print(f"Found hashes for {len(metadata)} files in the {csv_file} csv file.")

    #Tidy up the existing metadata file: remove duplicates etc.
    #save_metadata_to_csv(metadata, csv_file)

    files_to_hash = [file for file in files if str(file) not in metadata]
    print(f"There are {len(files_to_hash)} files in {folder} that don't have a hash in the csv file.")

    if files_to_hash:
        # calculate hashes for the new files and save incrementally to the csv file. 
        calculate_hashes(files_to_hash,csv_file)
    
        # Get all the hashes.
        metadata = load_metadata_from_csv(csv_file)
 
    duplicate_files = get_dup_groups(metadata)
    
    if duplicate_files:
        print(f"Found {len(duplicate_files)} groups of duplicate files.")
        for hash, files in duplicate_files.items():
            print(f"\n{hash}")
            for file in files:
                print(f"{file}")

if __name__ == "__main__":
    main()


    # metadata = load_metadata_from_csv(csv_file)
    # print(type(metadata))
    # print(type(str(files[0])))
    # file = files[0]
    # print(f"File {str(file)} is in metadata: {str(file) in metadata}. Type: {type(str(file) in metadata.keys())}")
