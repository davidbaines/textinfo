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
            df['Experiment'] = experiment_name
            df['Steps'] = scores_number
            # Further processing if "Scorer" is "Bleu"
            if 'Scorer' in df.columns and 'Score' in df.columns:
                if df['Scorer'].str.contains('BLEU').any():  # Check if BLEU scorer exists in the file
                    bleu_score = df.loc[df['Scorer'] == 'BLEU', 'Score'].str.split('/').str[0]
                    df['Score'] = bleu_score
            all_data.append(df)  # Append modified DataFrame to the list
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    return all_data

# Function to combine all scores files into one Scores.csv file
def combine_scores_files(all_data, output_file):
    if all_data:  # Check if there is any data to concatenate
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df.pivot_table(index=['book', 'src_iso', 'trg_iso', 'num_refs', 'references', 'sent_len', 'scorer', 'Score'],
                                              columns=['Experiment'], values=['Steps'], aggfunc='first').reset_index()
        combined_df.columns = combined_df.columns.map('_'.join).str.strip('_')
        combined_df.to_csv(output_file, index=False)
        print(f"Combined scores saved to {output_file}")
    else:
        print("No data to combine. No output file generated.")

# Main function to execute the process
def main():
    series_folder = Path("path/to/Series")  # Update with the path to your Series folder
    scores_files = find_scores_files(series_folder)
    all_data = add_experiment_info(scores_files)
    combine_scores_files(all_data, series_folder / "Scores.csv")

if __name__ == "__main__":
    main()
