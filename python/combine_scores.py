import argparse
import csv
from pathlib import Path

def aggregate_csv(folder_path):
    # Create a list to store all rows from CSV files
    all_rows = []

    # Iterate over all CSV files in the folder and its subfolders
    for csv_file in folder_path.rglob("*/scores-*.csv"):
        series = csv_file.parts[-3]  # Extract series folder name
        experiment = csv_file.parts[-2]  # Extract experiment folder name
        steps = csv_file.stem.split("-")[-1]  # Extract steps from file name

        # Read the CSV file and add new columns
        with open(csv_file, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)

            # Add column headers to the first row
            all_rows.append(["Series", "Experiment", "Steps"] + rows[0])
            
            
            # Add columns to the beginning of each row
            for row in rows[1:]:
                all_rows.append([series, experiment, steps] + row)

    # Write the aggregated data to a new CSV file
    output_file = folder_path / "scores.csv"
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(all_rows)
        # Write the folder path to the last line of the CSV file
        writer.writerow([folder_path])

def main():
    parser = argparse.ArgumentParser(description="Aggregate CSV files in a folder.")
    parser.add_argument("folder", type=Path, help="Path to the folder containing CSV files.")
    args = parser.parse_args()

    aggregate_csv(args.folder)

if __name__ == "__main__":
    main()
