from pathlib import Path
import csv
import argparse

def parse_scores_file(scores_file):
    """Parse the CHRF3 scores along with src_iso and trg_iso from a scores file."""
    scores_data = []
    with open(scores_file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        chrf3_score = None
        src_iso = None
        trg_iso = None
        for row in reader:
            if row['scorer'] == 'CHRF3':
                chrf3_score = float(row['score'])
                src_iso = row['src_iso']
                trg_iso = row['trg_iso']
                if chrf3_score is not None and src_iso is not None and trg_iso is not None:
                    scores_data.append({'src_iso': src_iso, 'trg_iso': trg_iso, 'CHRF3': chrf3_score})
                    print(f"src_iso: {src_iso}  trg_iso: {trg_iso}  CHRF3: {chrf3_score}")
    return scores_data

def aggregate_chrf3_scores(series_folder):
    """Aggregate CHRF3 scores for each experiment in the series."""
    chrf3_scores = {}
    for experiment_folder in series_folder.iterdir():
        if experiment_folder.is_dir():
            scores_files = experiment_folder.glob('scores-*.csv')
            for scores_file in scores_files:
                print(f"Reading {scores_file}")
                scores = parse_scores_file(scores_file)
                if scores:
                    experiment_name = experiment_folder.name
                    chrf3_scores[experiment_name] = scores

    return chrf3_scores

def write_aggregated_scores(series_folder, chrf3_scores):
    """Write aggregated CHRF3 scores to a CSV file in the series folder."""
    series_name = series_folder.name
    output_file = series_folder / f'{series_name}_chrf3_scores.csv'

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Experiment', 'src_iso', 'trg_iso', 'CHRF3'])
        for experiment, scores_list in chrf3_scores.items():
            for scores_data in scores_list:
                writer.writerow([experiment, scores_data['src_iso'], scores_data['trg_iso'], scores_data['CHRF3']])

def main():
    parser = argparse.ArgumentParser(description='Aggregate CHRF3 scores from experiments folder.')
    parser.add_argument('experiments_folder', type=str, help='Path to the experiments folder')
    parser.add_argument('--series', type=str, help='Path to the series folder')
    args = parser.parse_args()

    experiments_folder = Path(args.experiments_folder)
    if args.series:
        series_folder = experiments_folder / args.series
        if series_folder.is_dir():
            print(f"Looking in series {series_folder}")
            chrf3_scores = aggregate_chrf3_scores(series_folder)
            if chrf3_scores:
                print(f"Found scores in {series_folder}")
                write_aggregated_scores(series_folder, chrf3_scores)
            else :
                print(f"No scores in {series_folder}")
    else :
        for series_folder in experiments_folder.iterdir():
            if series_folder.is_dir():
                print(f"Looking in series {series_folder}")
                chrf3_scores = aggregate_chrf3_scores(series_folder)
                if chrf3_scores:
                    print(f"Found scores in {series_folder}")
                    write_aggregated_scores(series_folder, chrf3_scores)
                else :
                    print(f"No scores in {series_folder}")

if __name__ == "__main__":
    main()

