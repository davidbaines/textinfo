import argparse
from pathlib import Path
import pandas as pd

# Function to find all scores files in a given directory
def find_scores_files(directory):
    scores_files = []
    for file_path in Path(directory).rglob("scores-*.csv"):
        scores_files.append(file_path)
    return scores_files

# Function to add experiment and scores number columns to each scores file
def add_experiment_info(scores_files):
    all_data = []  # List to hold all modified DataFrame objects
    for file_path in scores_files:
        experiment_name = file_path.parent.name
        scores_number = file_path.stem.split("-")[-1]
        try:
            df = pd.read_csv(file_path)
            df['experiment'] = experiment_name
            df['steps'] = scores_number
            # Further processing if "Scorer" is "Bleu"
            if 'scorer' in df.columns and 'score' in df.columns:
                if df['scorer'].str.contains('BLEU').any():  # Check if BLEU scorer exists in the file
                    if '/' in df.loc[df['scorer'] == 'BLEU', 'score']:
                        bleu_score = df.loc[df['scorer'] == 'BLEU', 'score'].str.split('/').str[0]
                        df['score'] = bleu_score
            all_data.append(df)  # Append modified DataFrame to the list
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    return all_data

# Function to combine all scores files into one Scores.csv file
def combine_scores_files(all_data, output_file):
    if all_data:  # Check if there is any data to concatenate
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df.pivot_table(index=['book', 'src_iso', 'trg_iso', 'num_refs', 'references', 'sent_len', 'scorer', 'score'],
                                              columns=['experiment'], values=['steps'], aggfunc='first').reset_index()
        combined_df.columns = combined_df.columns.map('_'.join).str.strip('_')
        combined_df.to_csv(output_file, index=False)
        print(f"Combined scores saved to {output_file}")
    else:
        print("No data to combine. No output file generated.")


# Function to combine all scores files into one Scores.csv file
def combine_scores_files2(all_data, output_file):
    if all_data:  # Check if there is any data to concatenate
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df.pivot_table(index=['book', 'src_iso', 'trg_iso', 'num_refs', 'references', 'sent_len', 'scorer', 'score'],
                                              columns=['experiment'], values='steps', aggfunc='first').reset_index()
        combined_df.columns = combined_df.columns.map(lambda x: x[0] if x[1] == '' else f"{x[0]}_{x[1]}")
        combined_df.to_csv(output_file, index=False)
        print(f"Combined scores saved to {output_file}")
    else:
        print("No data to combine. No output file generated.")


# Function to combine all scores files into one Scores.csv file
def combine_scores_files3(all_data, output_file):
    if all_data:  # Check if there is any data to concatenate
        combined_df = pd.concat(all_data, ignore_index=True)
        print("Combined DataFrame:")
        print(combined_df.head())  # Print first few rows of the combined DataFrame
        combined_df = combined_df.pivot_table(index=['book', 'src_iso', 'trg_iso', 'num_refs', 'references', 'sent_len', 'scorer', 'score'],
                                              columns=['experiment'], values='steps', aggfunc='first').reset_index()
        combined_df.columns = combined_df.columns.map(lambda x: x[0] if x[1] == '' else x[1].lower())  # Convert column names to lowercase
        print("Combined DataFrame after pivot:")
        print(combined_df.head())  # Print first few rows of the combined DataFrame after pivot
        combined_df.to_csv(output_file, index=False)
        print(f"Combined scores saved to {output_file}")
    else:
        print("No data to combine. No output file generated.")


def combine_dataframes_to_csv(dataframes, output_file):
    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df.to_csv(output_file, index=False)
    print(f"Combined data saved to {output_file}")


def rename_files_in_subfolders(directory):
    # Iterate through all subfolders and their files
    for subfolder in Path(directory).iterdir():
        if subfolder.is_dir():
            for file in subfolder.glob("scores-*_copy.tsv"):
                new_filename = file.name.replace("_copy.tsv", ".tsv").replace("scores-", "score-copy-")
                file.rename(file.parent / new_filename)
                print(f"Renamed file {file} to {file.parent / new_filename}")


# Main function to execute the process
def main():
    parser = argparse.ArgumentParser(
        description="Combine csv scores into a single file."
    )
    parser.add_argument("folder", type=Path, help="Directory to search")
    parser.add_argument(
        "-r", "--rename", action="store_true", help="Rename scores tsv files."
    )
    args = parser.parse_args()

    series_folder = Path(args.folder)
    scores_files = find_scores_files(series_folder)
    
    if args.rename:
        rename_files_in_subfolders(series_folder)
    elif scores_files:
        print("Found these files:")
        for scores_file in scores_files:
            print(scores_file)
        all_data = add_experiment_info(scores_files)
        print(f"Found this data:\n{all_data}")
        print(f"\n{len(all_data)} lists found.")
        #all_data.to_csv(series_folder / "all_scores.csv", index=False)
        #combine_dataframes_to_csv(all_data, series_folder / "Scores.csv")
        #combine_scores_files3(all_data, series_folder / "Scores.csv")

    else:
        print("Didn't find any scores files.")


if __name__ == "__main__":
    main()
