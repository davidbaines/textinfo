import argparse
import cProfile
import csv
import time
from collections import Counter
from itertools import combinations
from pathlib import Path

import pandas as pd
import xxhash
import pandas as pd
from pathlib import Path


def create_dataframe(vref_path):
    # Read the vref.txt file to create initial dataframe with verse references as index
    df = pd.read_csv(vref_path, header=None, names=['vref'], encoding='utf-8')
    df.set_index('vref', inplace=True)
    
    return df


def read_bibles(directory, df):
    files = Path(directory).glob('*.txt')
    data = {}

    for file in files:
        # Read each line into its own row in a DataFrame
        data[file] = pd.read_table(file, header=None, encoding='utf-8').squeeze("columns")

    for bible, verses in data.items():
        df[bible] = verses

    return df


def main():
    df = create_dataframe("F:/GitHub/silnlp/silnlp/assets/vref.txt")
    df = read_bibles("F:/GitHub/davidbaines/textinfo/test/bibles1", df)

    print(df)


if __name__ == "__main__":
    main()
