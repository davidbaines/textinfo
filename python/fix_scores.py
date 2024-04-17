import argparse
import shutil
from pathlib import Path

import boto3
import pandas as pd


# Function to find all scores files in a given directory
def find_scores_files(directory):
    scores_files = []
    for file_path in Path(directory).rglob("scores-*.csv"):
        scores_files.append(file_path)
    return scores_files


# Function to create copies of the original files with "_copy" suffix
def create_copy_files(scores_files,destination):
    for file_path in scores_files:
        copy_file_path = destination / file_path.parent / (file_path.stem + "_copy.tsv")
        if not copy_file_path.exists():
            shutil.copy(file_path, copy_file_path)
            print(f"Copied scores from {file_path.name} to {copy_file_path} ")
        else:
            print(f"{copy_file_path} already exists.")


# Function to remove additional columns and save files in their original state
def restore_original_state(scores_files):
    for file_path in scores_files:
        df = pd.read_csv(file_path)
        original_columns = [
            "book",
            "src_iso",
            "trg_iso",
            "num_refs",
            "references",
            "sent_len",
            "scorer",
            "score",
        ]
        additional_columns = [col for col in df.columns if col not in original_columns]
        if additional_columns:
            df.drop(columns=additional_columns, inplace=True)
            df.to_csv(file_path, index=False)
            print(f"Removed additional columns from {file_path}")


# Main function to execute the process
def main():
    parser = argparse.ArgumentParser(
        description="Combine csv scores into a single file."
    )
    parser.add_argument("folder", type=Path, help="Directory to search")
    args = parser.parse_args()

    series_folder = Path(args.folder)
    scores_files = find_scores_files(series_folder)
    for file in scores_files:
        print(file)
    destination = Path("C:/Users/David/Documents/MT/experiments/Markose")
    #create_copy_files(scores_files,destination)
    restore_original_state(scores_files)


if __name__ == "__main__":
    main()
