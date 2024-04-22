import argparse
import cProfile
import csv
import time
from collections import Counter
from itertools import combinations
from pathlib import Path

import pandas as pd
import xxhash

IDENTICAL = 0
VERY_SIMILAR = 1
SIMILAR = 2
DIFFERENT = 3
sim_dict = {0: "IDENTICAL", 1: "VERY_SIMILAR", 2: "SIMILAR", 3: "DIFFERENT"}


def generate_hash(file_path):
    """
    Generate a hash for a given file.

    Arguments:
    file_path -- the path to the file for which to generate a hash.

    Returns:
    A string representing the file's hash.
    """
    with open(file_path, "rb") as file:
        file_content = file.read()
        return str(xxhash.xxh64(file_content).hexdigest())


def compare_two_bibles(bible1, bible2):
    # Read the Bibles into memory
    with open(bible1, "r", encoding="utf-8") as f:
        bible1_lines = f.readlines()
    with open(bible2, "r", encoding="utf-8") as f:
        bible2_lines = f.readlines()

    # Initialize counters
    comparison_counts = Counter()

    # Compare each pair of verses
    for verse1, verse2 in zip(bible1_lines, bible2_lines):
        if verse1.strip():
            comparison_counts["num_verses_bible1"] += 1
        if verse2.strip():
            comparison_counts["num_verses_bible2"] += 1
        if verse1.strip() and verse2.strip():
            comparison_result = compare_verses(verse1, verse2)
            if comparison_result == IDENTICAL:
                comparison_counts["num_identical_verses"] += 1
            else:
                comparison_counts["num_different_verses"] += 1

    # Add all necessary keys to the Counter
    for key in ["num_verses_bible1", "num_verses_bible2", "num_identical_verses", "num_different_verses"]:
        if key not in comparison_counts:
            comparison_counts[key] = 0

    return comparison_counts



def compare_verses(verse1, verse2):
    # Convert verses to string and split into words
    words1 = str(verse1).split()
    words2 = str(verse2).split()

    # Return category as an integer:
    # 0: Identical
    # 1: Different
    return IDENTICAL if words1 == words2 else DIFFERENT


def read_cache(cache_file):
    """Read the cache file into a Pandas DataFrame."""
    if cache_file.is_file():
        df = pd.read_csv(cache_file, index_col=["hash1", "hash2"])
    else:
        df = pd.DataFrame(
            columns=[
                "hash1",
                "hash2",
                "filename1",
                "filename2",
                "num_verses_bible1",
                "num_verses_bible2",
                "num_identical_verses",
                "num_different_verses",
            ]
        )
        df.set_index(["hash1", "hash2"], inplace=True)

    # Remove the rows where all values are NaN
    df = df.dropna(how='all')

    # Save the cache.
    write_cache(df, cache_file)

    return df




def write_cache(df, cache_file):
    """Write the cache DataFrame to a file."""
    # Ensure correct columns order
    df = df.reset_index()[
        [
            "hash1",
            "hash2",
            "filename1",
            "filename2",
            "num_verses_bible1",
            "num_verses_bible2",
            "num_identical_verses",
            "num_different_verses",
        ]
    ]
    df.to_csv(cache_file, index=False)


def update_df(df, hash1, hash2, filename1, filename2, comparison):
    """Update the cache DataFrame with a new comparison result."""
    update_dict = {
        "hash1": hash1, 
        "hash2": hash2, 
        "filename1": filename1, 
        "filename2": filename2, 
        "num_verses_bible1": comparison.get("num_verses_bible1", 0),
        "num_verses_bible2": comparison.get("num_verses_bible2", 0),
        "num_identical_verses": comparison.get("num_identical_verses", 0),
        "num_different_verses": comparison.get("num_different_verses", 0)
    }
    new_df = pd.DataFrame([update_dict])
    new_df.set_index(["hash1", "hash2"], inplace=True)
    return pd.concat([df, new_df])



def check_df(df, hash1, hash2):
    """Check if a comparison result is in the cache."""
    if (hash1, hash2) in df.index or (hash2, hash1) in df.index:
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Compare Bibles.")
    parser.add_argument(
        "folders", nargs="+", help="A list of folders to search for Bibles."
    )
    parser.add_argument(
        "--ext",
        default="txt",
        help="The file extension of the Bibles. Defaults to txt.",
    )
    parser.add_argument(
        "--cache",
        default=Path("F:/GitHub/davidbaines/textinfo/test/compare_bibles/cache.csv"),
        help="The path to the cache.",
    )

    args = parser.parse_args()
    cache = Path(args.cache)

    # Find all Bibles in the specified folders with the specified extension.
    bibles = []
    for folder in args.folders:
        path = Path(folder)
        bibles.extend(path.glob(f"*.{args.ext}"))

    # Read the hash cache from disk.
    df = read_cache(cache)

    # Calculate the file hash for each Bible.
    hashdict = {generate_hash(bible): bible for bible in bibles}
    
    # DEBUG: Print out the list of Bibles
    print(f"Bibles: {bibles}")

    # DEBUG: Print out the hashdict
    print(f"Hashdict: {hashdict}")

    # Calculate the similarity for each pair of Bibles if the pair have different hashes
    for hash1, hash2 in combinations(hashdict.keys(), 2):
        bible1 = hashdict[hash1]
        bible2 = hashdict[hash2]

        # If we don't have a comparison result for these Bibles, calculate it.
        if not check_df(df, hash1, hash2):
            comparison_result = compare_two_bibles(bible1, bible2)
            df = update_df(df, hash1, hash2, bible1, bible2, comparison_result)
        
    # DEBUG: Print out the DataFrame
    print(f"Dataframe:\n{df}")

    # Write the updated comparison cache back to disk.
    write_cache(df, cache)


if __name__ == "__main__":
    main()
